import os
import re
import time
import datetime
from urllib.parse import quote
from src.vault.parser import parse_markdown_file, write_markdown_file
from src.browser.browser_manager import BrowserManager

def get_next_job_id(vault_path: str) -> str:
    jobs_dir = os.path.join(vault_path, "01 - Jobs")
    max_id = 0
    if not os.path.exists(jobs_dir):
        return "JOB-000001"
    
    for root, _, files in os.walk(jobs_dir):
        for f in files:
            if f.startswith("JOB-") and f.endswith(".md"):
                match = re.match(r"^JOB-(\d+)", f)
                if match:
                    val = int(match.group(1))
                    if val > max_id:
                        max_id = val
    return f"JOB-{max_id + 1:06d}"

def is_duplicate_url(vault_path: str, url: str) -> bool:
    # Remove query parameters for strict canonical comparison
    canonical_url = url.split("?")[0]
    jobs_dir = os.path.join(vault_path, "01 - Jobs")
    if not os.path.exists(jobs_dir):
        return False
        
    for root, _, files in os.walk(jobs_dir):
        for f in files:
            if f.endswith(".md"):
                filepath = os.path.join(root, f)
                fm, _ = parse_markdown_file(filepath)
                existing_url = fm.get("source_url", "") or fm.get("url", "")
                if existing_url and existing_url.split("?")[0] == canonical_url:
                    return True
    return False

class DiscoveryAgent:
    def __init__(self, vault_path: str = "vault"):
        self.vault_path = vault_path
        # Load configuration
        config_file = os.path.join(vault_path, "08 - Search Configuration/Search Configuration.md")
        self.config, _ = parse_markdown_file(config_file)
        if not self.config:
            self.config = {
                "sources": ["naukri"],
                "target_titles": ["Business Intelligence Developer"],
                "locations": ["Pune"]
            }

    def discover_jobs(self, page) -> list[dict]:
        discovered = []
        target_titles = self.config.get("target_titles", [])
        locations = self.config.get("locations", [])
        
        for title in target_titles:
            for loc in locations:
                print(f"Searching for '{title}' in '{loc}'...")
                query = quote(title)
                location_query = quote(loc)
                # Build Naukri SRP URL
                url = f"https://www.naukri.com/jobs-in-{location_query}?k={query}"
                
                try:
                    page.goto(url)
                    page.wait_for_timeout(3000) # Wait for page load
                    
                    # Scroll down to load more dynamically
                    for _ in range(3):
                        page.evaluate("window.scrollBy(0, 1000)")
                        page.wait_for_timeout(1000)
                        
                    # Extract job card links and info
                    # Naukri wraps job details in articles/divs
                    cards = page.query_selector_all("article.jobTuple, div.srp-job-tuple")
                    
                    if not cards:
                        # Fallback to general link scraping
                        links = page.query_selector_all("a[href*='/job-description-']")
                        for l in links:
                            href = l.get_attribute("href")
                            if href and not is_duplicate_url(self.vault_path, href):
                                # Gather basic metadata if we can find parent card
                                text = l.inner_text()
                                discovered.append({
                                    "source_url": href,
