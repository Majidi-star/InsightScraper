import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from config_loader import ConfigLoader
from scraper import Scraper
from ai_agent import AIAgent
from file_manager import FileManager
from urllib.parse import urlparse
import os
from colorama import init, Fore, Back, Style
import sys 
import traceback


# Initialize colorama
init(autoreset=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self):
        self.config = ConfigLoader().load_all()
        self.ai_agent = AIAgent(self.config['model_config'])
        self.file_manager = FileManager()
        self.scraper = Scraper(self.config['limits'])
        self.evaluated_links = set()  # Set to track evaluated links
    
    async def process_page(self, url: str, current_depth: int) -> None:
        """Process a page and its related pages"""
        if current_depth > self.config['limits']['scraping']['max_depth']:
            return
        
        print(Fore.BLUE + f"Visiting page: {url} at depth {current_depth}")
        
        # Get content and links
        content, links, _ = await self.scraper.get_page_content(url)  # Ignore images

        links = list(set(links))  # Remove duplicates from links

        if not content:
            logger.warning(f"Warning: No content found for {url}, but will continue processing links.")

        # Evaluate content if it exists
        is_valuable = False
        if content:
            is_valuable, evaluation = await self.ai_agent.evaluate_content(content, self.config['topics'])
            logger.info(f"Evaluating content for {url}: {evaluation}")
            
            # Generate article if content is valuable
            if is_valuable:
                article = await self.ai_agent.generate_article(content, self.config['topics'])
                logger.info(f"\n\nGenerated article for {url}")  # Log first 100 characters
                if not article:
                    logger.error(f"Error: Article generation failed for {url}")
                else : 
                    title = f"Article for {url}"
                    saved_path = self.file_manager.save_article(title, article, url)
                    if saved_path:
                        logger.info(f"Article saved successfully at {saved_path}")
                    else:
                        logger.error(f"Failed to save article for {url}")

        # Collect scores for all links
        link_scores = []
        link_score_threshold = self.config['model_config']['thresholds']['link_score']  # Fetch threshold from config
        for link in links:
            if link not in self.config['exclusions'] and link not in self.evaluated_links:
                # Evaluate the link individually
                score = await self.ai_agent.evaluate_link(link, self.config['topics'])
                logger.info(f"Evaluating link {link}: Score {score}")
                link_scores.append((link, score))  # Store the link and its score

        # Sort links by score in descending order
        link_scores.sort(key=lambda x: x[1], reverse=True)

        # Truncate the list based on max_links_per_page
        max_links_per_page = self.config['limits']['scraping']['max_links_per_page']
        top_links = link_scores[:max_links_per_page]

        # Add the current link to the evaluated links and exclusion links
        self.evaluated_links.add(url)  
        if url not in self.config['websites']:
            exclusions_file = self.config_dir / "exclusions.txt"
            with open(exclusions_file, 'a', encoding='utf-8') as f:
                f.write(url + '\n')
            logger.info(f"Added {url} to exclusions.txt as it is not in websites.txt")

        # Process the top links
        for link, score in top_links:
            if score >= link_score_threshold:  # Use the threshold from the config
                print(Fore.BLUE + f"Visiting link: {link} with score: {score}")
                await self.process_page(link, current_depth + 1)

    async def run(self):
        """Main program execution"""
        try:
            # Remove files inside the articles directory
            for file in self.file_manager.articles_dir.glob('*'):
                if file.is_file():
                    file.unlink()
            # Process all main websites
            for website in self.config['websites']:
                await self.process_page(website, 0)
            
            # Generate HTML summary
            summary_path = self.file_manager.generate_html_summary()
            if summary_path:
                print(Fore.GREEN + f"HTML summary created at {summary_path}")
            
        except Exception as e:
            print(Fore.RED + f"Error running program: {str(e)}")
            traceback.print_exc()
        finally:
            self.scraper.cleanup()

    def _is_valid_url(self, url: str, base_url: str) -> bool:
        """Check if URL is valid"""
        if not url:
            return False
        # Additional logic...

async def main():
    scraper = WebScraper()
    await scraper.run()

if __name__ == "__main__":
    asyncio.run(main()) 