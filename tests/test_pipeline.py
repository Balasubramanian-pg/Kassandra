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
