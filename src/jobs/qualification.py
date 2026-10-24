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
