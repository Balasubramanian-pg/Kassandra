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
        """
        Calls Gemini to extract structured info from the raw JD.
        """
        prompt = f"""
Analyze the following Job Description (JD) and extract details into a JSON object.
Do not invent or assume fields. Keep them empty or null if not found.

JSON keys to return:
- responsibilities (list of strings)
- required_skills (list of strings)
- preferred_skills (list of strings)
- technologies (list of strings)
- education_requirements (list of strings)
- certifications (list of strings)
- domain (string)
- remote_type (string, e.g. "remote", "hybrid", "onsite", "unknown")

JD Content:
---
{raw_jd}
---

Return ONLY raw JSON, starting with {{ and ending with }}. Do not wrap it in markdown code blocks.
"""
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            # Remove any possible markdown wrap
            text = response.text.strip()
            if text.startswith("```"):
                # strip code block formatting
                text = re.sub(r"^```[a-zA-Z]*\n", "", text)
                text = re.sub(r"\n```$", "", text)
                text = text.strip()
            return json.loads(text)
        except Exception as e:
            print(f"Gemini JD extraction failed: {e}")
            return {
                "responsibilities": [],
                "required_skills": [],
                "preferred_skills": [],
                "technologies": [],
                "education_requirements": [],
                "certifications": [],
                "domain": "Unknown",
                "remote_type": "unknown"
            }

    def process_and_normalize(self, job_filepath: str, page) -> bool:
        """
        Extracts JD, normalizes data, and updates the vault file.
        """
        fm, body = parse_markdown_file(job_filepath)
        url = fm.get("source_url")
        if not url:
            return False
            
        print(f"Scraping & extracting JD for {fm.get('job_id')}...")
        raw_jd = self.scrape_jd_content(page, url)
        if not raw_jd:
            return False
            
        # Get structured extraction from LLM
        extracted = self.extract_structured_jd(raw_jd)
        
        # Normalize fields
        normalized_company = self.normalize_term(fm.get("company", ""), self.skill_map) # can use specific taxonomy rules if needed
        normalized_title = self.normalize_term(fm.get("title", ""), self.title_map)
        
        normalized_skills = []
        for skill in extracted.get("required_skills", []):
            normalized_skills.append(self.normalize_term(skill, self.skill_map))
            
        normalized_pref_skills = []
        for skill in extracted.get("preferred_skills", []):
            normalized_pref_skills.append(self.normalize_term(skill, self.skill_map))

        # Update frontmatter
        fm["company"] = normalized_company
        fm["title"] = normalized_title
        fm["status"] = "qualified" # move status to qualified after successful extraction
        fm["remote_type"] = extracted.get("remote_type", "unknown")
        fm["domain"] = extracted.get("domain", "Unknown")
        fm["required_skills"] = normalized_skills
        fm["preferred_skills"] = normalized_pref_skills
        fm["technologies"] = extracted.get("technologies", [])
        fm["education_requirements"] = extracted.get("education_requirements", [])
        fm["certifications"] = extracted.get("certifications", [])
        fm["content_hash"] = hash(raw_jd)
        
        # Format updated body content
        new_body = f"""# {normalized_title}

## Company

{normalized_company}

## Location

{', '.join(fm.get('location', []))}

## Job Description

{raw_jd}

## Responsibilities

{chr(10).join(['- ' + r for r in extracted.get('responsibilities', [])])}

## Requirements

{chr(10).join(['- ' + req for req in extracted.get('education_requirements', []) + extracted.get('certifications', [])])}

## Skills

{chr(10).join(['- ' + s for s in normalized_skills + normalized_pref_skills])}

## Source

[{url}]({url})
"""
        write_markdown_file(job_filepath, fm, new_body)
        return True
