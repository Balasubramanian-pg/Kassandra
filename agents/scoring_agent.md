# Scoring Agent Specification

## Responsibilities
1. Evaluate qualified jobs against the candidate profile using weighted criteria from `config/scoring_config.yaml`:
   - Technical Skill Match (25%)
   - Experience Match (20%)
   - Title Alignment (15%)
   - Domain Relevance (10%)
   - Responsibilities Match (10%)
   - Location Match (5%)
   - Seniority Tier (5%)
   - Education & Certifications (5%)
   - Career Trajectory Relevance (5%)
2. Generate transparent, explainable score reasoning in `## Fit Analysis`.
3. Select top daily candidates (default target: 30) ensuring portfolio diversification across role types.
