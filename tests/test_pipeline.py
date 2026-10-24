import os
import unittest
from unittest.mock import MagicMock, patch
from src.vault.parser import parse_markdown_file, write_markdown_file
from src.jobs.qualification import QualificationAgent
from src.resumes.generator import ResumeAgent

class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.vault_path = "vault"
        os.makedirs(os.path.join(self.vault_path, "05 - Candidate Profile"), exist_ok=True)
        
    def test_qualification_filters(self):
        agent = QualificationAgent(vault_path=self.vault_path)
        # Create a mock job file
        job_file = os.path.join(self.vault_path, "01 - Jobs", "test_job.md")
        os.makedirs(os.path.dirname(job_file), exist_ok=True)
        
        fm = {
            "type": "job",
            "job_id": "JOB-999999",
            "experience_min": 10,  # clearly above max config of 5
            "title": "Director of Analytics",
            "location": ["Pune"],
            "status": "discovered"
        }
        write_markdown_file(job_file, fm, "# Test Job")
        
        qualified = agent.qualify_job(job_file)
        self.assertFalse(qualified)
        
        # Cleanup
        if os.path.exists(job_file):
            os.remove(job_file)

if __name__ == "__main__":
    unittest.main()
