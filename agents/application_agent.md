# Application Agent Specification

## Responsibilities
1. Initialize application record in `vault/03 - Applications/`.
2. Launch browser automation to navigate to candidate application URL.
3. Auto-populate standard non-sensitive fields from candidate profile.
4. Stage the generated tailored resume file (`.pdf` or `.docx`).
5. **HUMAN GATE**: Never click the final "Submit" button automatically.
6. Await explicit human verification and confirmation.
7. Record submission timestamp, resume version, and status update upon human completion.
