# Orchestrator Agent Specification

## Role
Coordinates the sequential execution of specialized subagents across discovery, extraction, qualification, scoring, evidence mapping, resume generation, ATS validation, and application recording.

## Input
- `config/system_config.yaml`
- `config/scoring_config.yaml`
- `vault/08 - Search Configuration/Search Configuration.md`

## Pipeline Flow
1. **Discovery**: Spawns Discovery Agent to retrieve fresh job URLs.
