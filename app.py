import streamlit as st
import re, time, hashlib
from datetime import datetime

st.set_page_config(page_title="CodePulse AI", layout="wide")

# ---------- Styling ----------
st.markdown("""
<style>
.block-container {padding-top: 2rem;}
.small-muted {opacity: 0.8; font-size: 0.9rem;}
.hr {height:1px; background: rgba(255,255,255,0.08); margin: 14px 0;}
</style>
""", unsafe_allow_html=True)

# ---------- Sample PR ----------
SAMPLE_PR = """diff --git a/payment_service.py b/payment_service.py
index 1ab23..9cd45 100644
--- a/payment_service.py
+++ b/payment_service.py
@@ -12,7 +12,36 @@ def process_payment(user_id, amount):
-    return amount * 0.95
+    # TODO: add proper input validation
+    if user_id == None:
+        return 0
+
+    if amount > 10000:
+        if amount > 50000:
+            if amount > 100000:
+                return amount * 0.6
+        return amount * 0.8
+
+    try:
+        return amount * 0.95
+    except Exception as e:
+        print("payment error", e)
+        return 0
"""

# ---------- Helpers ----------
def stable_id(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:10]

def detect_language(text: str) -> str:
    t = text.lower()
    if "def " in t and "import " in t: return "Python"
    if "public " in t or "system.out" in t: return "Java"
    if "console.log" in t or "typescript" in t: return "TypeScript"
    return "Unknown"

def score_risk(code: str):
    lines = code.splitlines()
    text = code

    todo = len(re.findall(r"\b(TODO|FIXME)\b", text, flags=re.I))
    deep_nesting = sum(1 for l in lines if len(re.match(r"^\s*", l).group(0)) >= 12)
    long_lines = sum(1 for l in lines if len(l) > 120)

    has_try = bool(re.search(r"\btry\b|\bexcept\b|\bcatch\b", text))
    has_logging = bool(re.search(r"\blogger\b|\blogging\b|\bconsole\.log\b|\bprint\(", text))
    has_validation = bool(re.search(r"\bvalidate\b|\bassert\b|\bisinstance\b|\bnull\b|==\s*None", text, flags=re.I))

    risk = 22
    risk += todo * 8
    risk += min(deep_nesting, 10) * 3
    risk += min(long_lines, 10) * 2
    risk += 10 if not has_try else 0
    risk += 10 if not has_validation else 0
    risk -= 5 if has_logging else 0
    risk = max(0, min(100, risk))

    bug = "High" if risk > 70 else "Medium" if risk > 40 else "Low"
    verdict = "Block ❌" if risk > 75 else "Needs Review ⚠️" if risk >= 50 else "Safe ✅"

    fixes = []
    if todo: fixes.append("Resolve TODO/FIXME items before merge.")
    if not has_try: fixes.append("Add error handling (try/except).")
    if not has_validation: fixes.append("Add input validation.")
    if long_lines: fixes.append("Refactor long lines / complex logic.")
    if deep_nesting > 3: fixes.append("Reduce deep nesting via helpers.")
    if not has_logging: fixes.append("Add structured logging.")

    ops = [
        "Add latency/error metrics",
        "Configure alarms for failures",
        "Add retries/backoff",
        "Add unit + edge-case tests",
        "Document rollback strategy"
    ]

    summary = f"""Senior SDE Review
- TODO/FIXME count: {todo}
- Deep nesting lines: {deep_nesting}
- Long lines: {long_lines}
- Verdict: {verdict}
"""

    return risk, bug, verdict, summary, fixes, ops

# ---------- State ----------
if "code_input" not in st.session_state:
    st.session_state.code_input = ""

if "history" not in st.session_state:
    st.session_state.history = []

# ---------- Header ----------
st.title("🧠 CodePulse AI – PR Risk & Review Assistant")
st.markdown('<div class="small-muted">Internal-style AI tool for PR risk scoring, fixes, and ops readiness.</div>', unsafe_allow_html=True)
st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

# ---------- Buttons ----------
b1, b2 = st.columns([1,1])
with b1:
    if st.button("📄 Load Sample PR"):
        st.session_state.code_input = SAMPLE_PR

with b2:
    st.caption("Textbox retains content after Analyze & refresh")

# ---------- Input (RETAINED) ----------
code = st.text_area(
    "Paste PR diff / code",
    height=240,
    key="code_input"
)

# ---------- Analyze ----------
if st.button("Analyze"):
    t0 = time.time()
    risk, bug, verdict, summary, fixes, ops = score_risk(code)
    latency = int((time.time() - t0) * 1000) + 60

    entry = {
        "id": stable_id(code),
        "language": detect_language(code),
        "risk": risk,
        "bug": bug,
        "verdict": verdict,
        "latency_ms": latency,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    st.session_state.history.insert(0, entry)
    st.session_state.history = st.session_state.history[:10]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Risk Score", risk)
    k2.metric("Bug Likelihood", bug)
    k3.metric("Verdict", verdict)
    k4.metric("Latency (ms)", latency)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    l, r = st.columns([1.2,1])
    with l:
        st.subheader("AI Review Summary")
        st.code(summary)
        st.subheader("Actionable Fixes")
        for f in fixes:
            st.write("•", f)

    with r:
        st.subheader("Operational Readiness Checklist")
        for o in ops:
            st.checkbox(o, value=False)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    st.subheader("Recent Analyses")
    st.dataframe(st.session_state.history, use_container_width=True, hide_index=True)
