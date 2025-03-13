import ollama
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image
import io
import base64
import logging
import traceback


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIAgent:
    def __init__(self, model_config: Dict[str, Any]):
        self.model_config = model_config
        self.content_model = model_config['models']['content']['name']
        self.links_model = model_config['models']['links']['name']
        self.prompts = model_config['prompts']
    
    async def evaluate_link(self, url: str, topics: List[str]) -> float:
        """Evaluate the importance of a link based on topics"""
        try:
            prompt = self.prompts['link_evaluation'].format(
                topics="\n".join(topics),
                url=url
            )
            
            response = ollama.chat(
                model=self.links_model,
                messages=[{'role': 'user', 'content': prompt}]
            )
            
            # Extract score from response
            try:
                score = float(response['message']['content'].strip())
                return max(0.0, min(1.0, score))  # Limit score between 0 and 1
            except ValueError:
                logger.warning( f"Could not extract a valid score from response: {response}")
                return 0.0
            
        except Exception as e:
            logger.error(f"Error evaluating link {url}: {str(e)}")
            print("this one")
            traceback.print_exc()
            return 0.0
    
    async def evaluate_content(self, content: str, topics: List[str]) -> Tuple[bool, Any]:
        """Evaluate the value of the content"""
        try:
            prompt = self.prompts['content_evaluation'].format(
                topics="\n".join(topics),
                content=content[:1000]  # Limit content length
            )
            
            response = ollama.chat(
                model=self.content_model,
                messages=[{'role': 'user', 'content': prompt}]
            )
            
            response_text = response['message']['content'].lower()
            is_valuable = 'yes' in response_text
            return is_valuable, response['message']['content']
            
        except Exception as e:
            logger.error(f"Error evaluating content: {str(e)}")
            return False, str(e)
    
    async def generate_article(self, content: str, topics: List[str]) -> Optional[str]:
        """Generate an article from raw content"""
        try:
            prompt = self.prompts['article_generation'].format(
                content=content,
                topics=", ".join(topics)
            )
            
            response = ollama.chat(
                model=self.content_model,
                messages=[{'role': 'user', 'content': prompt}]
            )
            
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"Error generating article: {str(e)}")
            return None
    
    async def evaluate_image(self, image_path: str, content: str) -> Tuple[bool, float]:
        """Evaluating the image"""
        try:
            response = ollama.chat(
                model='llama3.2-vision',
                messages=[{
                    'role': 'user',
                    'content': f'Evaluate the visual quality and relevance of this image for the provided article content. Respond with "suitable" or "not suitable" and include a confidence score (between 0.0 and 1.0) indicating the suitability of the image.: \n\n Content :\n{content}',
                    'images': [image_path]
                }]
            )
            response_text = response['message']['content'].lower()
            is_suitable = 'suitable' in response_text or 'yes' in response_text
            
            # استخراج یک امتیاز تقریبی از پاسخ
            score = 0.7 if is_suitable else 0.3 
            
            return is_suitable, score
            
        except Exception as e:
            logger.error(f"خطا در ارزیابی تصویر {image_path}: {str(e)}")
            return False, 0.0 
    
    async def evaluate_links(self, links: List[str], topics: List[str], content: str) -> List[Tuple[str, float]]:
        """Evaluate multiple links based on the content and topics"""
        try:
            prompt = self.prompts['link_evaluation_multiple'].format(
                topics="\n".join(topics),
                content=content,
                links="\n".join(links)
            )
            
            response = ollama.chat(
                model=self.links_model,
                messages=[{'role': 'user', 'content': prompt}]
            )
            
            # Log the response for debugging
            logger.info(f"Response from AI model (LINK EVALUATION): {response}")

            # Assuming the response contains a list of links with their scores
            link_scores = []
            if 'message' in response and 'content' in response['message']:
                for line in response['message']['content'].strip().split(","):
                    try:
                        # Ensure the line contains a valid URL format
                        if ':' in line:
                            link, score = line.split(':', 1)  # Split only on the first colon
                            link_scores.append((link.strip(), float(score.strip())))
                        else:
                            logger.warning(f"Line does not contain a valid format: {line}")
                    except ValueError:
                        logger.warning(f"Could not parse line: {line}")
            else:
                logger.error("Response does not contain expected keys: 'message' or 'content'")

            return link_scores
            
        except Exception as e:
            logger.error(f"Error evaluating links: {str(e)}")
            traceback.print_exc()
            return []