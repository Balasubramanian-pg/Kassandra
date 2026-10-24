import os
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
import yaml

class BrowserManager:
    def __init__(self, config_path: str = "config/system_config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.playwright = None
        self.browser = None
        self.context = None

    def start(self) -> Page:
        self.playwright = sync_playwright().start()
        
        user_data_dir = self.config['browser'].get('user_data_dir', '.auth/user_data')
        os.makedirs(user_data_dir, exist_ok=True)
