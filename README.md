# CodePulse AI — PR Risk & Review Assistant

Live Demo: (paste your Streamlit link here)

## What it does
CodePulse AI is an internal-tool style app that analyzes PR diffs / code snippets and produces:
- Risk Score (0–100)
- Bug Likelihood (Low/Medium/High)
- Deployment Verdict (Safe / Needs Review / Block)
- Actionable Fixes + Operational Readiness Checklist

## Why it matters
Fast-moving teams need lightweight signals before merging and deploying changes. CodePulse AI simulates an Amazon-style engineering review assistant focused on reliability and operational excellence.

## Scoring signals
- TODO/FIXME count
- Deep nesting / complex logic
- Missing input validation
- Missing error handling
- Missing logging / observability

## Tech stack
- Python
- Streamlit
- GitHub (source)
- Streamlit Community Cloud (deployment)

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
