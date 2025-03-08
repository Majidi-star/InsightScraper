from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import logging
import asyncio
from typing import List, Dict, Set, Optional, Tuple, Any
import os
from pathlib import Path
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Scraper:
    def __init__(self, limits: Dict[str, Any]):
        self.limits = limits
        self.browser_config = limits['browser']
        self.visited_urls: Set[str] = set()
        self.driver = self._setup_driver()
    
    def _setup_driver(self) -> webdriver.Firefox:
        """Set up and initialize Firefox browser"""
        options = Options()
        if self.browser_config['headless']:
            options.add_argument('--headless')
        
        options.add_argument(f'user-agent={self.browser_config["user_agent"]}')
        
        service = Service(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
        driver.set_page_load_timeout(self.browser_config['timeout'])
        
        return driver
    
    def _is_valid_url(self, url: str, base_url: str) -> bool:
        """Check if URL is valid"""
        if not url:
            return False
        
        # Remove fragment from URL
        url = url.split('#')[0]
        
        try:
            parsed = urlparse(url)
            base_parsed = urlparse(base_url)
            
            # Check if URL is in the same domain
            return (parsed.netloc == base_parsed.netloc or not parsed.netloc) and \
                   parsed.scheme in ('http', 'https', '')
        except Exception:
            return False
        
    def _is_valid_url_without_domain_check(self, url: str) -> bool:
        """Check if URL is valid without considering the domain"""
        if not url:
            return False
        
        # Remove fragment from URL
        url = url.split('#')[0]
        
        try:
            parsed = urlparse(url)
            
            # Check if URL is valid
            return parsed.scheme in ('http', 'https', '')
        except Exception:
            return False
    
    async def get_page_content(self, url: str) -> Tuple[Optional[str], List[str], List[str]]:
        """Get content, links, and images from a page"""
        print('working main scraper ...')
        if url in self.visited_urls:
            print('already visited')
            return None, [], []
        
        self.visited_urls.add(url)
        
        try:
            self.driver.get(url)
            # Wait for page to load
            WebDriverWait(self.driver, self.browser_config['timeout']).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Allow JavaScript to execute
            time.sleep(2)
            
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Remove unnecessary elements
            for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            # Extract text from all elements
            content = ' '.join([element.get_text().strip() for element in soup.find_all()])
            
            # Extract links
            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                full_url = urljoin(url, href)
                if self._is_valid_url(full_url, url):
                    links.append(full_url)
            
            # Extract images
            images = []
            for img in soup.find_all('img', src=True):
                src = img['src']
                if src.startswith('data:'):  # Skip base64 images
                    continue
                full_url = urljoin(url, src)
                if self._is_valid_url_without_domain_check(full_url):
                    images.append(full_url)

            print(f"\n\nImages length : {len(images)}\n\n")
            
            # Delay between requests
            await asyncio.sleep(self.limits['scraping']['request_delay'])
            
            return content, links, images
            
        except TimeoutException:
            logger.error(f"Timeout error loading {url}")
            return None, [], []
        except WebDriverException as e:
            logger.error(f"Browser error at {url}: {str(e)}")
            return None, [], []
        except Exception as e:
            logger.error(f"Unknown error at {url}: {str(e)}")
            return None, [], []
    
    async def download_image(self, image_url: str, output_dir: str) -> Optional[str]:
        """Download and save an image"""
        try:
            import requests
            from PIL import Image
            
            # Create safe filename
            image_name = os.path.basename(urlparse(image_url).path)
            if not image_name:
                image_name = f"image_{hash(image_url)}.jpg"
            
            output_path = os.path.join(output_dir, image_name)
            
            # Download image
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            # Save image
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            # Check and resize image if needed
            with Image.open(output_path) as img:
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                
                max_size = (800, 800)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                img.save(output_path, 'JPEG', quality=85)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error downloading image {image_url}: {str(e)}")
            return None
    
    def cleanup(self):
        """Clean up resources"""
        try:
            self.driver.quit()
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup() 