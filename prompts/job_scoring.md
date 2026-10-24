# Job Scoring Prompt Template

```markdown
Evaluate the fit between this Candidate Profile and the Job Description.
Compute individual category scores according to the weights. The total score must sum up to 100 max.

Category Weights:
- experience_match: {weights.experience_match}
- technical_skill_match: {weights.technical_skill_match}
- title_match: {weights.title_match}
- domain_match: {weights.domain_match}
- responsibility_match: {weights.responsibility_match}
- location_match: {weights.location_match}
- seniority_match: {weights.seniority_match}
- education_certification: {weights.education_certification}
- career_relevance: {weights.career_relevance}

Candidate Profile Body:
