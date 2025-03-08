import yaml
from pathlib import Path
from typing import List, Dict, Any

class ConfigLoader:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        
    def load_websites(self) -> List[str]:
        """Load the list of websites from the configuration file"""
        websites = []
        websites_file = self.config_dir / "websites.txt"
        
        with open(websites_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    websites.append(line)
        return websites
    
    def load_topics(self) -> List[str]:
        """Load the list of topics from the configuration file"""
        topics = []
        topics_file = self.config_dir / "topics.txt"
        
        with open(topics_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    topics.append(line)
        return topics
    
    def load_exclusions(self) -> List[str]:
        """Load the list of excluded URLs"""
        exclusions = []
        exclusions_file = self.config_dir / "exclusions.txt"
        
        with open(exclusions_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    exclusions.append(line)
        return exclusions
    
    def load_model_config(self) -> Dict[str, Any]:
        """Load AI model settings"""
        model_config_file = self.config_dir / "model_config.yaml"
        
        with open(model_config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def load_limits(self) -> Dict[str, Any]:
        """Load scraping limits"""
        limits_file = self.config_dir / "limits.yaml"
        
        with open(limits_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def load_all(self) -> Dict[str, Any]:
        """Load all settings"""
        return {
            'websites': self.load_websites(),
            'topics': self.load_topics(),
            'exclusions': self.load_exclusions(),
            'model_config': self.load_model_config(),
            'limits': self.load_limits()
        } 