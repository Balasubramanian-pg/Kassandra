import os
import json
import re
import yaml
import google.generativeai as genai
from src.vault.parser import parse_markdown_file, write_markdown_file

class ExtractionAgent:
    def __init__(self, vault_path: str = "vault"):
        self.vault_path = vault_path
        # Setup Gemini
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
        
        # Load Taxonomy
        self.taxonomy_path = os.path.join(vault_path, "99 - System", "Taxonomy.md")
        self.load_taxonomy()

    def load_taxonomy(self):
        self.skill_map = {}
        self.title_map = {}
        self.loc_map = {}
        
        if not os.path.exists(self.taxonomy_path):
            return
            
        _, body = parse_markdown_file(self.taxonomy_path)
        
        # Simple markdown table parser for Taxonomy.md
        sections = body.split("## ")
        for sec in sections:
            if sec.startswith("Skill Normalization"):
                self.skill_map = self.parse_table(sec)
            elif sec.startswith("Title Normalization"):
                self.title_map = self.parse_table(sec)
            elif sec.startswith("Location Normalization"):
                self.loc_map = self.parse_table(sec)

    def parse_table(self, text: str) -> dict:
        mapping = {}
        lines = text.strip().split("\n")
        for line in lines:
            if "|" in line and "Raw Term" not in line and "---" not in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 4:
                    raw = parts[1]
                    canonical = parts[2]
                    mapping[raw.lower()] = canonical
        return mapping

    def normalize_term(self, term: str, mapping: dict) -> str:
        return mapping.get(term.lower(), term)

    def scrape_jd_content(self, page, url: str) -> str:
        """
        Scrapes job description text using Playwright.
        """
        try:
            page.goto(url)
            page.wait_for_timeout(3000)
            
            # Select common JD containers in Naukri
            jd_selectors = [
                ".job-desc", 
                "section.job-desc", 
                ".clearanceCard", 
                "#jobDescription",
                "article",
                "body"
            ]
            
            for selector in jd_selectors:
                el = page.query_selector(selector)
                if el:
                    text = el.inner_text().strip()
                    if len(text) > 100:
                        return text
            return ""
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            # Create extraction error markdown
            self.log_extraction_error(url, str(e))
            return ""

    def log_extraction_error(self, url: str, error_msg: str):
        errors_dir = os.path.join(self.vault_path, "99 - System", "Errors")
        os.makedirs(errors_dir, exist_ok=True)
        safe_url = "".join([c if c.isalnum() else "_" for c in url[-20:]])
        filepath = os.path.join(errors_dir, f"error_{safe_url}.md")
        
        frontmatter = {
            "type": "extraction_error",
            "source": "naukri",
            "date": datetime.date.today().isoformat() if hasattr(datetime, 'date') else "2026-08-28"
        }
        body = f"# Extraction Failure\n\n## URL\n\n{url}\n\n## Failure\n\n{error_msg}\n\n## Action\n\nRequires manual review.\n"
        write_markdown_file(filepath, frontmatter, body)

    def extract_structured_jd(self, raw_jd: str) -> dict:
