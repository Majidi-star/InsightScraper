import os
from pathlib import Path
import json
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import shutil
from urllib.parse import urlparse
import requests
from PIL import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileManager:
    def __init__(self, base_dir: str = "output"):
        self.base_dir = Path(base_dir)
        self.articles_dir = self.base_dir / "articles"
        self.images_dir = self.base_dir / "images"
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure required directories exist"""
        self.articles_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)
    
    def save_article(self, title: str, content: str, url: str, images: List[str]) -> str:
        """Save article and its metadata"""
        try:
            # Create safe filename
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title[:50]  # Limit title length
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            article_dir = self.articles_dir / f"{safe_title}_{timestamp}"
            article_dir.mkdir(parents=True, exist_ok=True)
            
            # Save article text
            article_path = article_dir / "article.md"
            with open(article_path, 'w', encoding='utf-8') as f:
                f.write(f"# {title}\n\n")
                f.write(content)
            
            # Save metadata
            metadata = {
                'title': title,
                'source_url': url,
                'timestamp': timestamp,
                'images': images
            }
            
            metadata_path = article_dir / "metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            return str(article_dir)
            
        except Exception as e:
            logger.error(f"Error saving article {title}: {str(e)}")
            return ""
    
    def copy_image(self, source_path: str, article_dir: str) -> str:
        """Copy image to article directory"""
        try:
            if not os.path.exists(source_path):
                return ""
            
            image_name = os.path.basename(source_path)
            dest_path = os.path.join(article_dir, "images", image_name)
            
            # Ensure images directory exists
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            shutil.copy2(source_path, dest_path)
            return dest_path
            
        except Exception as e:
            logger.error(f"Error copying image {source_path}: {str(e)}")
            return ""
    
    def generate_html_summary(self) -> str:
        """Generate HTML summary of all articles"""
        try:
            summary_path = self.base_dir / "summary.html"
            
            html_content = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Article Summary</title>
                <style>
                    body {
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        margin: 0;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }
                    .container {
                        max-width: 1200px;
                        margin: 0 auto;
                    }
                    .article {
                        background: white;
                        border-radius: 8px;
                        padding: 20px;
                        margin-bottom: 20px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }
                    .article h2 {
                        color: #2c3e50;
                        margin-top: 0;
                    }
                    .article-meta {
                        color: #666;
                        font-size: 0.9em;
                        margin-bottom: 15px;
                    }
                    .article-images {
                        display: flex;
                        gap: 10px;
                        flex-wrap: wrap;
                        margin-top: 15px;
                    }
                    .article-images img {
                        max-width: 200px;
                        border-radius: 4px;
                    }
                    a {
                        color: #3498db;
                        text-decoration: none;
                    }
                    a:hover {
                        text-decoration: underline;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Article Summary</h1>
            """
            
            # Collect article information
            for article_dir in sorted(self.articles_dir.glob("*"), reverse=True):
                if not article_dir.is_dir():
                    continue
                
                metadata_path = article_dir / "metadata.json"
                article_path = article_dir / "article.md"
                
                if not metadata_path.exists() or not article_path.exists():
                    continue
                
                # Read metadata
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # Read article content
                with open(article_path, 'r', encoding='utf-8') as f:
                    article_content = f.read()
                
                # Create HTML for article
                html_content += f"""
                    <article class="article">
                        <h2>{metadata['title']}</h2>
                        <div class="article-meta">
                            <a href="{metadata['source_url']}" target="_blank">Original Source</a>
                            | Date: {metadata['timestamp']}
                        </div>
                        <div class="article-content">
                            {article_content[:500]}...
                        </div>
                """
                
                # Add images
                if metadata['images']:
                    html_content += '<div class="article-images">'
                    for image_path in metadata['images']:
                        if os.path.exists(image_path):
                            relative_path = os.path.relpath(image_path, str(self.base_dir))
                            html_content += f'<img src="{relative_path}" alt="Article Image">'
                    html_content += '</div>'
                
                html_content += """
                    </article>
                """
            
            html_content += """
                </div>
            </body>
            </html>
            """
            
            # Save HTML file
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return str(summary_path)
            
        except Exception as e:
            logger.error(f"Error generating HTML summary: {str(e)}")
            return ""

    async def download_image(self, image_url: str, output_dir: str, image_name: str = None) -> Optional[str]:
        """Download and save an image"""
        try:
            # Create safe filename if not provided
            if not image_name:
                image_name = os.path.basename(urlparse(image_url).path)
                if not image_name:
                    image_name = f"image_{hash(image_url)}"
            
            # Ensure the correct file extension
            if not image_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                image_name += '.jpg'  # Default to jpg if no valid extension
            
            output_path = os.path.join(output_dir, image_name)
            
            # Download image
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()  # Raise an error for bad responses
            
            # Save image
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error downloading image {image_url}: {str(e)}")
            return None 