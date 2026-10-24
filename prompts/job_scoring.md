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
---
{candidate_profile_body}
---

Job Title: {job_title}
Job Company: {job_company}
Job Location: {job_location}
Job Description:
---
{job_description}
---

Calculate scores and write a brief explanation for each category.
Return a JSON object containing:
- total_score (0-100 integer)
- analysis (markdown content for the '## Fit Analysis' section, detailing category breakdown, matched/missing skills, and short reasons)

Return ONLY raw JSON, starting with { and ending with }. Do not wrap it in markdown code blocks.
```
