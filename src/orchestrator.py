import os
import sys
import datetime
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.browser.browser_manager import BrowserManager
from src.jobs.discovery import DiscoveryAgent, get_next_job_id
from src.jobs.extraction import ExtractionAgent
from src.jobs.qualification import QualificationAgent, ScoringAgent
from src.resumes.generator import EvidenceAgent, ResumeAgent, ATSValidationAgent
from src.vault.parser import parse_markdown_file, write_markdown_file

def log_event(message: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"{timestamp} {message}"
    print(log_line)
    
    # Write to vault log
    log_dir = "vault/99 - System/Logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{datetime.date.today().isoformat()}.log")
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_line + "\n")

def run_daily_workflow():
    load_dotenv()
    
    if not os.environ.get("GEMINI_API_KEY"):
        log_event("ERROR: GEMINI_API_KEY not found in environment. Please add it to your .env file.")
        return
        
    log_event("WORKFLOW: Daily job application engine run started.")
    
    # Initialize Browser Manager
    bm = BrowserManager()
    page = bm.start()
    
    # 1. Discovery Phase
    log_event("DISCOVERY: Start scanning job sources.")
    discovery = DiscoveryAgent()
    discovered_jobs = discovery.discover_jobs(page)
    log_event(f"DISCOVERY: Found {len(discovered_jobs)} raw jobs.")
    
    # Save newly discovered jobs
    new_jobs_count = discovery.save_jobs(discovered_jobs)
    log_event(f"DISCOVERY: Saved {new_jobs_count} new job listings to vault.")
    
    # Retrieve all active/discovered jobs for processing
    # Traverse vault to find all jobs with status == "discovered"
    jobs_to_process = []
    jobs_dir = "vault/01 - Jobs"
    for root, _, files in os.walk(jobs_dir):
        for f in files:
            if f.endswith(".md"):
                filepath = os.path.join(root, f)
                fm, _ = parse_markdown_file(filepath)
                if fm.get("status") == "discovered":
                    jobs_to_process.append(filepath)
                    
    log_event(f"PIPELINE: Found {len(jobs_to_process)} discovered jobs to process.")
    
    extraction = ExtractionAgent()
    qualification = QualificationAgent()
    scoring = ScoringAgent()
    evidence_agent = EvidenceAgent()
    resume_agent = ResumeAgent()
    ats_agent = ATSValidationAgent()
    
    # 2. Extraction & Qualification Loop
    shortlisted_count = 0
    for filepath in jobs_to_process:
        # a. JD Extraction
        success = extraction.process_and_normalize(filepath, page)
        if not success:
            log_event(f"PIPELINE: Extraction failed/skipped for {filepath}")
            continue
            
        # b. Qualification Filters
        qualified = qualification.qualify_job(filepath)
        if not qualified:
            log_event(f"PIPELINE: Job disqualified {filepath}")
            continue
            
        # c. Scoring
        log_event(f"PIPELINE: Scoring job {filepath}")
        scoring_res = scoring.score_job(filepath)
        fit_score = scoring_res.get("total_score", 0)
        
        # d. Shortlisting for resume tailoring
        if fit_score >= 80:
            log_event(f"PIPELINE: Shortlisted job {filepath} with score {fit_score}")
            
