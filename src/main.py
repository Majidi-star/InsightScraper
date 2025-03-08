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

"""

Evaluate each link based on its relevance to the topics \n\nFor each link, provide a score 
from 0 to 1, where:\n- 0 means no relevance\n- 1 means perfect relevance\n\nFormat your response 
strictly as follows:\nlink1: score1,link2: score2,link3: score3\n\nInclude only the evaluated 
links and their scores. Do not include any explanations or additional text , Given the following 
topics:\n{topics}\n\nAnd the following links:\n{links}\n\n

"""




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
        content, links, images = await self.scraper.get_page_content(url)

        print(f"\n\nimages and links: {len(images)} and {len(links)} \n\n")

        # Log if no content is found but continue processing links
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

        # Process images
        selected_images = []
        if is_valuable: 
            for image_url in images:
                print(image_url)
                # Download image with a name connected to the article
                image_name = f"{urlparse(url).netloc}_{len(selected_images)}.jpg"  # Example naming convention
                image_path = await self.file_manager.download_image(
                    image_url,
                    str(self.file_manager.images_dir),
                    image_name=image_name  # Pass the image name to the download function
                )
                if not image_path:
                    continue
                
                # Just append the image path to selected_images without evaluation
                selected_images.append(image_path)
        
        # Save article if generated
        if is_valuable and article:
            title = f"Article from {urlparse(url).netloc}"
            article_dir = self.file_manager.save_article(title, article, url, selected_images)
            
            # Copy images to article directory
            final_image_paths = []
            for image_path in selected_images:
                copied_path = self.file_manager.copy_image(image_path, article_dir)
                if copied_path:
                    final_image_paths.append(copied_path)
    
        # Process each link one at a time
        for link in links:
            if link not in self.config['exclusions'] and link not in self.evaluated_links:
                # Evaluate the link individually
                score = await self.ai_agent.evaluate_link(link, self.config['topics'])
                logger.info(f"Evaluating link {link}: Score {score}")

                # Only process the link if it has a positive score
                if score > 0.5:
                    print(Fore.BLUE + f"Visiting link: {link}")
                    await self.process_page(link, current_depth + 1)



    async def run(self):
        """Main program execution"""
        try:
            # Process all main websites
            for website in self.config['websites']:
                await self.process_page(website, 0)
            
            # Generate HTML summary
            summary_path = self.file_manager.generate_html_summary()
            if summary_path:
                print(Fore.GREEN + f"HTML summary created at {summary_path}")
            
        except Exception as e:
            print(Fore.RED + f"Error running program: {str(e)}")
        finally:
            self.scraper.cleanup()

async def main():
    scraper = WebScraper()
    await scraper.run()

if __name__ == "__main__":
    asyncio.run(main()) 