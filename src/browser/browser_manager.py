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
        
        headless = self.config['browser'].get('headless', True)
        
        # Launch persistent context to reuse logins and cookies
        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=headless,
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Set default timeout
        timeout = self.config['browser'].get('timeout_ms', 30000)
        self.context.set_default_timeout(timeout)
        
        page = self.context.pages[0] if self.context.pages else self.context.new_page()
        return page

    def close(self):
        if self.context:
            self.context.close()
        if self.playwright:
            self.playwright.stop()
