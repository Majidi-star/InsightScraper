import os
from pathlib import Path
import json
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import markdown

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileManager:
    def __init__(self, base_dir: str = "output"):
        self.base_dir = Path(base_dir)
        self.articles_dir = self.base_dir / "articles"
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure required directories exist"""
        self.articles_dir.mkdir(parents=True, exist_ok=True)
    
    def save_article(self, title: str, content: str, url: str) -> str:
        """Save article and its metadata without images"""
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
            
            # Save metadata without images
            metadata = {
                'title': title,
                'source_url': url,
                'timestamp': timestamp,
                'images': []  # No images to save
            }
            
            metadata_path = article_dir / "metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            return str(article_dir)
            
        except Exception as e:
            logger.error(f"Error saving article {title}: {str(e)}")
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
                        text-align: center;
                    }
                    .container {
                        max-width: 800px;
                        margin: 0 auto;
                    }
                    .article {
                        display: none; /* Hide all articles by default */
                        background: white;
                        border-radius: 8px;
                        padding: 20px;
                        margin-bottom: 20px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        text-align: left;
                    }
                    .article.active {
                        display: block; /* Show the active article */
                    }
                    button {
                        padding: 10px 20px;
                        margin: 5px;
                        border: none;
                        border-radius: 5px;
                        background-color: #3498db;
                        color: white;
                        cursor: pointer;
                    }
                    button:hover {
                        background-color: #2980b9;
                    }
                    .article-number {
                        margin: 20px 0;
                        font-size: 1.2em;
                    }
                    .article-content {
                        margin-top: 20px;
                    }
                    .article-content h1, .article-content h2, .article-content h3 {
                        color: #2c3e50;
                    }
                    .article-content ul, .article-content ol {
                        padding-left: 20px;
                    }
                    .article-content a {
                        color: #3498db;
                        text-decoration: none;
                    }
                    .article-content a:hover {
                        text-decoration: underline;
                    }
                    .article-content blockquote {
                        border-left: 4px solid #3498db;
                        padding-left: 15px;
                        margin-left: 0;
                        color: #7f8c8d;
                    }
                    .article-content code {
                        background-color: #f0f0f0;
                        padding: 2px 4px;
                        border-radius: 3px;
                    }
                    .article-content pre {
                        background-color: #f0f0f0;
                        padding: 10px;
                        border-radius: 5px;
                        overflow-x: auto;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Article Summary</h1>
                    <div class="article-number" id="articleNumber"></div>
                    <div id="articles">
            """
            
            # Collect article information
            articles = []
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
                
                # Convert markdown to HTML
                html_content_converted = markdown.markdown(article_content, extensions=['extra'])
                
                # Prepare HTML for each article
                article_html = f"""
                    <div class="article" id="article-{len(articles)}">
                        <h2>{metadata['title']}</h2>
                        <div class="article-content">
                            {html_content_converted}
                        </div>
                    </div>
                """
                articles.append(article_html)
            
            # Add articles to the HTML content
            for article_html in articles:
                html_content += article_html
            
            # Add navigation buttons and script
            html_content += """
                    <button id="prevBtn" onclick="changeArticle(-1)">Previous</button>
                    <button id="nextBtn" onclick="changeArticle(1)">Next</button>
                </div>
                <script>
                    let currentArticle = 0;
                    const articles = document.querySelectorAll('.article');
                    const totalArticles = articles.length;
                    articles[currentArticle].classList.add('active'); // Show the first article
                    updateArticleNumber();

                    function changeArticle(direction) {
                        articles[currentArticle].classList.remove('active'); // Hide current article
                        currentArticle += direction; // Change the current article index
                        if (currentArticle < 0) currentArticle = totalArticles - 1; // Loop to last article
                        if (currentArticle >= totalArticles) currentArticle = 0; // Loop to first article
                        articles[currentArticle].classList.add('active'); // Show new current article
                        updateArticleNumber();
                    }

                    function updateArticleNumber() {
                        document.getElementById('articleNumber').innerText = 
                            `This is the ${currentArticle + 1} of ${totalArticles} posts`;
                    }
                </script>
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