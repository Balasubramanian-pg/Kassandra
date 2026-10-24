import os
import json
import re
import datetime
import google.generativeai as genai
import yaml
from src.vault.parser import parse_markdown_file, write_markdown_file

class QualificationAgent:
    def __init__(self, vault_path: str = "vault"):
        self.vault_path = vault_path
        # Load search configuration
        config_file = os.path.join(vault_path, "08 - Search Configuration/Search Configuration.md")
        self.config, _ = parse_markdown_file(config_file)

    def qualify_job(self, job_filepath: str) -> bool:
        """
        Applies hard filters to a job. Returns True if qualified, False if rejected.
        Updates status and rejection_reason if rejected.
        """
        fm, body = parse_markdown_file(job_filepath)
        if fm.get("status") == "rejected":
            return False
            
        experience_min = fm.get("experience_min")
        experience_max = fm.get("experience_max")
        title = fm.get("title", "")
        locations = fm.get("location", [])
        
        # 1. Experience filter
        conf_exp_max = self.config.get("experience_max", 5)
        if experience_min is not None and experience_min > conf_exp_max:
            self.reject_job(job_filepath, fm, body, "experience_requirement")
            return False
            
        # 2. Title filter
        target_titles = [t.lower() for t in self.config.get("target_titles", [])]
        title_lower = title.lower()
        title_matched = any(target in title_lower or title_lower in target for target in target_titles)
        if not title_matched:
            # Let's check if there is any word overlap
            words = set(title_lower.split())
            target_words = set([w for t in target_titles for w in t.split()])
            if not words.intersection(target_words):
                self.reject_job(job_filepath, fm, body, "outside_target_roles")
                return False
                
        # 3. Location filter
        conf_locs = [l.lower() for l in self.config.get("locations", [])]
        # Check if remote or if any location matches
        loc_matched = False
        for loc in locations:
            loc_l = loc.lower()
            if "remote" in loc_l or any(cl in loc_l for cl in conf_locs):
                loc_matched = True
                break
        if not loc_matched and conf_locs:
            self.reject_job(job_filepath, fm, body, "location_incompatible")
            return False
            
        return True

    def reject_job(self, filepath: str, fm: dict, body: str, reason: str):
        fm["status"] = "rejected"
        fm["rejection_reason"] = reason
        # Keep track of history transition
        self.log_history_transition(body, "discovered", "rejected", f"Hard filtered out: {reason}")
        write_markdown_file(filepath, fm, body)

    def log_history_transition(self, body: str, old_status: str, new_status: str, note: str) -> str:
        # History table helper
        today = datetime.date.today().isoformat()
        row = f"| {today} | {old_status} | {new_status} | {note} |\n"
        
        if "## Status History" in body:
            return body.replace("## Status History\n", f"## Status History\n{row}")
        else:
            return body + f"\n\n## Status History\n\n| Date | Old Status | New Status | Note |\n|---|---|---|---|\n{row}"


class ScoringAgent:
    def __init__(self, vault_path: str = "vault", scoring_config_path: str = "config/scoring_config.yaml"):
        self.vault_path = vault_path
        with open(scoring_config_path, 'r') as f:
            self.scoring_config = yaml.safe_load(f)
        
        # Setup Gemini
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            
        # Load Candidate Profile
        profile_path = os.path.join(vault_path, "05 - Candidate Profile/Profile.md")
        self.profile_fm, self.profile_body = parse_markdown_file(profile_path)

    def score_job(self, job_filepath: str) -> dict:
        """
        Uses Gemini to evaluate job fit against candidate profile.
        Returns a dictionary containing fit_score and structured analysis.
        """
        fm, body = parse_markdown_file(job_filepath)
        
        # Prepare inputs for scoring prompt
        weights = self.scoring_config.get("weights", {})
        
        prompt = f"""
Evaluate the fit between this Candidate Profile and the Job Description.
Compute individual category scores according to the weights. The total score must sum up to 100 max.

Category Weights:
- experience_match: {weights.get('experience_match', 20)}
- technical_skill_match: {weights.get('technical_skill_match', 25)}
- title_match: {weights.get('title_match', 15)}
- domain_match: {weights.get('domain_match', 10)}
- responsibility_match: {weights.get('responsibility_match', 10)}
- location_match: {weights.get('location_match', 5)}
- seniority_match: {weights.get('seniority_match', 5)}
- education_certification: {weights.get('education_certification', 5)}
- career_relevance: {weights.get('career_relevance', 5)}

Candidate Profile Body:
---
{self.profile_body}
---

Job Title: {fm.get('title')}
Job Company: {fm.get('company')}
Job Location: {', '.join(fm.get('location', []))}
Job Description:
---
{body}
---

Calculate scores and write a brief explanation for each category.
Return a JSON object containing:
- total_score (0-100 integer)
- analysis (markdown content for the '## Fit Analysis' section, detailing category breakdown, matched/missing skills, and short reasons)

Return ONLY raw JSON, starting with {{ and ending with }}. Do not wrap it in markdown code blocks.
"""
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith("```"):
                text = re.sub(r"^```[a-zA-Z]*\n", "", text)
                text = re.sub(r"\n```$", "", text)
                text = text.strip()
            res = json.loads(text)
            
            # Update job file
            fm["fit_score"] = res["total_score"]
            fm["status"] = "shortlisted"
            
            # Log transition
            history_helper = QualificationAgent()
            new_body = history_helper.log_history_transition(body, "qualified", "shortlisted", f"Scored: {res['total_score']}/100")
            
            # Append fit analysis section
            if "## Fit Analysis" in new_body:
                new_body = new_body.split("## Fit Analysis")[0]
            new_body = new_body + f"\n\n## Fit Analysis\n\n{res['analysis']}"
            
            write_markdown_file(job_filepath, fm, new_body)
            return res
        except Exception as e:
            print(f"Gemini job scoring failed: {e}")
            return {"total_score": 0, "analysis": "Scoring failed due to API error."}
