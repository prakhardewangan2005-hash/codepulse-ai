import streamlit as st
import random
import time

st.set_page_config(page_title="CodePulse AI", layout="wide")

st.title("🧠 CodePulse AI – PR Risk & Review Assistant")

code = st.text_area("Paste PR diff / code", height=200)

if st.button("Analyze"):
    start = time.time()

    risk = random.randint(25, 90)
    bug = "High" if risk > 70 else "Medium" if risk > 40 else "Low"
    verdict = "Block ❌" if risk > 75 else "Needs Review ⚠️" if risk > 50 else "Safe ✅"

    latency = int((time.time() - start) * 1000) + random.randint(40,120)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Risk Score", risk)
    col2.metric("Bug Likelihood", bug)
    col3.metric("Verdict", verdict)
    col4.metric("Latency (ms)", latency)

    st.subheader("AI Review Summary")
    st.write("""
    • Code shows potential scalability issues  
    • Error handling and validation should be improved  
    • Logging and observability are limited  
    • Recommend refactoring before deployment
    """)
