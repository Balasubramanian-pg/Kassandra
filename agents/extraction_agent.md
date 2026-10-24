# Extraction Agent Specification

## Responsibilities
1. Open discovered job URLs in Playwright browser session.
2. Extract the complete, uncompressed raw Job Description (JD) text.
3. Parse structured components via Gemini LLM into:
   - Responsibilities
   - Required skills
   - Preferred skills
   - Technology stack
   - Educational prerequisites
   - Domain classification
4. Calculate content hashes to prevent redundant processing.
5. Record failed page extractions into `vault/99 - System/Errors/`.
