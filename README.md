# CodePulse AI — Pull Request (PR) Risk & Review Assistant

🚀 **Live Demo:** https://codepulse-ai-ctbwcsz2lvf4nussfnrqpd.streamlit.app/

---

## Overview
**CodePulse AI** is an internal-tool style web app that analyzes **Pull Request (PR)** diffs or code snippets and generates:
- **Risk Score (0–100)**
- **Bug Likelihood** (Low / Medium / High)
- **Deployment Verdict** (Safe ✅ / Needs Review ⚠️ / Block ❌)
- **Actionable Fixes** and an **Operational Readiness Checklist**
- **Recent Analyses** history for quick comparison

This project is designed to demonstrate **Amazon-style engineering thinking**: reliability, maintainability, and operational excellence.

---

## Why this matters (Amazon-style)
In high-velocity environments, teams need fast signals before merging and deploying changes.  
CodePulse AI simulates a lightweight reviewer that flags common risk signals and suggests practical next steps.

---

## Key Features
- ✅ **One-click demo:** “Load Sample PR” auto-fills a realistic PR diff
- ✅ **Persistent input:** textarea retains content after Analyze & refresh
- ✅ **Dashboard KPIs:** Risk, bug likelihood, verdict, latency
- ✅ **Actionable output:** review summary + fixes + ops checklist
- ✅ **History table:** last 10 analyses stored in session memory

---

## Risk Scoring (Heuristic Signals)
The tool computes a risk score using measurable signals, such as:
- **TODO/FIXME** markers
- **Deep nesting / complex control flow**
- **Very long lines / readability risks**
- Missing **error handling** (try/except, catch)
- Missing **input validation**
- Presence of **logging/observability** (reduces risk)

**Verdict rules:**
- **Block ❌** if risk > 75  
- **Needs Review ⚠️** if risk 50–75  
- **Safe ✅** if risk < 50  

---

## Tech Stack
- **Python**
- **Streamlit**
- **GitHub** (version control)
- **Streamlit Community Cloud** (deployment)

---

## Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
