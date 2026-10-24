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
                                    "title": text,
                                    "company": "Unknown",
                                    "location": [loc],
                                    "source": "naukri",
                                    "posted_date": datetime.date.today().isoformat()
                                })
                        continue
                    
                    for card in cards:
                        # Extract title and link
                        title_el = card.query_selector("a.title, a[href*='/job-description-']")
                        if not title_el:
                            continue
                        
                        href = title_el.get_attribute("href")
                        if not href or is_duplicate_url(self.vault_path, href):
                            continue
                            
                        title_text = title_el.inner_text().strip()
                        
                        # Company
                        company_el = card.query_selector("a.comp-name, .companyInfo a, .comp-info-header a")
                        company_text = company_el.inner_text().strip() if company_el else "Unknown"
                        
                        # Location
                        loc_el = card.query_selector(".location, li.location, span.locWdth")
                        loc_text = loc_el.inner_text().strip() if loc_el else loc
                        
                        # Experience
                        exp_el = card.query_selector(".experience, li.experience, span.exp")
                        exp_text = exp_el.inner_text().strip() if exp_el else "Unknown"
                        
                        # Parse exp range e.g. "2-5 Yrs"
                        exp_min, exp_max = 0, 99
                        if exp_el:
                            match = re.search(r"(\d+)\s*-\s*(\d+)", exp_text)
                            if match:
                                exp_min = int(match.group(1))
                                exp_max = int(match.group(2))
                        
                        # Posted date
                        posted_el = card.query_selector(".postedVal, .day-txt")
                        posted_text = posted_el.inner_text().strip() if posted_el else ""
                        
                        discovered.append({
                            "source_url": href,
                            "title": title_text,
                            "company": company_text,
                            "location": [l.strip() for l in loc_text.split(",")] if loc_text else [loc],
                            "experience_min": exp_min,
                            "experience_max": exp_max,
                            "posted_text": posted_text,
                            "source": "naukri",
                            "discovered_date": datetime.date.today().isoformat()
                        })
                        
                except Exception as e:
                    print(f"Error searching Naukri for '{title}' in '{loc}': {e}")
                    
        return discovered

    def save_jobs(self, jobs: list[dict]) -> int:
        count = 0
        today = datetime.date.today()
        year_str = today.strftime("%Y")
        month_str = today.strftime("%m - %B")
        date_str = today.strftime("%Y-%m-%d")
        
        for job in jobs:
            next_id = get_next_job_id(self.vault_path)
            
            # Clean company name and title for file name
            safe_company = "".join([c if c.isalnum() else "_" for c in job["company"]])
            safe_title = "".join([c if c.isalnum() else "_" for c in job["title"]])
            filename = f"{next_id} - {safe_company} - {safe_title}.md"
            
            # Create full path
            job_dir = os.path.join(self.vault_path, "01 - Jobs", year_str, month_str, date_str)
            os.makedirs(job_dir, exist_ok=True)
            filepath = os.path.join(job_dir, filename)
            
            # Prepare frontmatter
            frontmatter = {
                "type": "job",
                "job_id": next_id,
                "source": job["source"],
                "source_job_id": job["source_url"].split("-")[-1].replace(".html", ""),
                "source_url": job["source_url"],
                "company": job["company"],
                "title": job["title"],
                "location": job["location"],
                "posted_date": job["discovered_date"],
                "discovered_date": job["discovered_date"],
                "experience_min": job.get("experience_min"),
                "experience_max": job.get("experience_max"),
                "status": "discovered",
                "fit_score": None,
                "priority": None,
                "resume_status": "pending",
                "ats_status": "pending",
                "application_status": "not_applied",
                "tags": ["job", job["source"]]
            }
            
            body = f"# {job['title']}\n\n## Company\n\n{job['company']}\n\n## Location\n\n{', '.join(job['location'])}\n\n## Source\n\n[{job['source_url']}]({job['source_url']})\n"
            
            write_markdown_file(filepath, frontmatter, body)
            count += 1
            
        return count
