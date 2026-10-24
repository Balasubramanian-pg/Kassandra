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
            
            # e. Evidence Mapping
            log_event(f"PIPELINE: Mapping evidence...")
            evidence_map_path = evidence_agent.map_evidence(filepath)
            
            # f. Tailored Resume Generation & Revision Loop
            log_event(f"PIPELINE: Generating tailored resume...")
            resume_path = resume_agent.generate_resume(filepath, evidence_map_path)
            
            # g. ATS Validation
            log_event(f"PIPELINE: Running ATS validation...")
            ats_res = ats_agent.validate_resume(filepath, resume_path, evidence_map_path)
            
            # Revision Loop if needed (up to 1 revision)
            if ats_res.get("revision_needed") and ats_res.get("application_match_score", 0) < 85:
                log_event("PIPELINE: Revision required. Regenerating...")
                resume_path = resume_agent.generate_resume(filepath, evidence_map_path)
                ats_res = ats_agent.validate_resume(filepath, resume_path, evidence_map_path)
                
            # Create application record
            create_application_record(filepath, resume_path, ats_res.get("application_match_score", 0))
            shortlisted_count += 1
            
    bm.close()
    log_event(f"WORKFLOW: Daily run completed. Shortlisted {shortlisted_count} jobs.")
    
    # Generate daily summary report in vault
    generate_daily_summary_report(new_jobs_count, shortlisted_count)

def create_application_record(job_filepath: str, resume_filepath: str, match_score: int):
    fm, _ = parse_markdown_file(job_filepath)
    job_id = fm.get("job_id")
    
    app_dir = "vault/03 - Applications"
    os.makedirs(app_dir, exist_ok=True)
    
    safe_company = "".join([c if c.isalnum() else "_" for c in fm.get("company", "")])
    safe_title = "".join([c if c.isalnum() else "_" for c in fm.get("title", "")])
    app_filename = f"{job_id} - {safe_company} - {safe_title}.md"
    app_filepath = os.path.join(app_dir, app_filename)
    
    app_fm = {
        "type": "application",
        "job_id": job_id,
        "status": "ready_to_apply",
        "resume_id": f"RESUME-{job_id}",
        "prepared_date": datetime.date.today().isoformat(),
        "applied_date": None,
        "application_method": fm.get("source", "naukri"),
        "interview_stage": "none",
        "response_status": "pending"
    }
    
    body = f"""# Application

## Job

[[{os.path.basename(job_filepath).replace('.md', '')}]]

## Resume

[[03 - Resume.md]]

## Status

Ready to Apply

## Application URL

[{fm.get('source_url')}]({fm.get('source_url')})

## Notes

Match score: {match_score}/100.
"""
    write_markdown_file(app_filepath, app_fm, body)
    
    # Update Job File to point to resume
    fm["resume_status"] = "cv_generated"
    fm["ats_status"] = "cv_validated"
    fm["application_status"] = "ready_to_apply"
    _, job_body = parse_markdown_file(job_filepath)
    write_markdown_file(job_filepath, fm, job_body)

def generate_daily_summary_report(discovered: int, shortlisted: int):
    today = datetime.date.today().isoformat()
    daily_dir = "vault/00 - Dashboard/Daily"
    os.makedirs(daily_dir, exist_ok=True)
    report_filepath = os.path.join(daily_dir, f"{today}.md")
    
    fm = {
        "type": "daily_job_search",
        "date": today,
        "jobs_discovered": discovered,
        "jobs_qualified": discovered,
        "jobs_shortlisted": shortlisted,
        "resumes_generated": shortlisted,
        "resumes_validated": shortlisted,
        "applications_submitted": 0
    }
    
    body = f"""# Daily Job Search - {today}

## Summary

- Jobs discovered: {discovered}
- Jobs qualified: {discovered}
- Jobs shortlisted: {shortlisted}
- CVs generated: {shortlisted}
- CVs validated: {shortlisted}

## Next Action

Review the ready-to-apply queue in the dashboard.
"""
    write_markdown_file(report_filepath, fm, body)

if __name__ == "__main__":
    run_daily_workflow()
