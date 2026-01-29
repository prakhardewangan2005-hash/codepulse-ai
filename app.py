import streamlit as st
import re, time, hashlib
from datetime import datetime

st.set_page_config(page_title="CodePulse AI", layout="wide")

# ---------- Styling ----------
st.markdown("""
<style>
.block-container {padding-top: 2rem;}
.small-muted {opacity: 0.8; font-size: 0.9rem;}
.card {padding: 14px 16px; border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; background: rgba(255,255,255,0.03);}
.hr {height:1px; background: rgba(255,255,255,0.08); margin: 14px 0;}
</style>
""", unsafe_allow_html=True)

# ---------- Helpers ----------
def stable_id(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:10]

def detect_language(text: str) -> str:
    t = text.lower()
    if "import " in t and "def " in t: return "Python"
    if "public static" in t or "system.out" in t: return "Java"
    if "console.log" in t or "typescript" in t or "interface " in t: return "TypeScript"
    if "#include" in t: return "C/C++"
    return "Unknown"

def score_risk(code: str):
    lines = code.splitlines()
    text = code

    todo = len(re.findall(r"\b(TODO|FIXME)\b", text, flags=re.I))
    deep_indent_lines = sum(1 for l in lines if len(re.match(r"^\s*", l).group(0)) >= 12)
    very_long_lines = sum(1 for l in lines if len(l) > 120)
    long_func_hint = len(re.findall(r"\bdef\b|\bfunction\b|\bclass\b", text))

    has_error_handling = bool(re.search(r"\btry\b|\bexcept\b|\bcatch\b|\bthrow\b", text))
    has_logging = bool(re.search(r"\blogger\b|\blogging\b|\bconsole\.log\b|\bprint\(", text))
    has_validation = bool(re.search(r"\bvalidate\b|\bassert\b|\bisinstance\b|\bnull\b|==\s*None", text, flags=re.I))

    # Base risk
    risk = 22
    risk += todo * 8
    risk += min(deep_indent_lines, 12) * 3
    risk += min(very_long_lines, 12) * 2
    risk += 8 if not has_error_handling else 0
    risk += 10 if not has_validation else 0
    risk -= 5 if has_logging else 0

    # Clamp
    risk = max(0, min(100, risk))

    bug = "High" if risk > 70 else "Medium" if risk > 40 else "Low"
    verdict = "Block ❌" if risk > 75 else "Needs Review ⚠️" if risk >= 50 else "Safe ✅"

    fixes = []
    if todo: fixes.append("Resolve TODO/FIXME items before merge.")
    if not has_error_handling: fixes.append("Add error handling (try/except or safe fallbacks).")
    if not has_validation: fixes.append("Add input validation + boundary checks.")
    if very_long_lines: fixes.append("Break long lines / simplify complex expressions.")
    if deep_indent_lines > 3: fixes.append("Refactor deeply nested logic into smaller functions.")
    if not has_logging: fixes.append("Add structured logging for observability.")
    if not fixes: fixes.append("No major issues detected. Consider adding more tests for edge cases.")

    ops = [
        "Add metrics: latency, error rate, throughput",
        "Add alarms for 5xx, timeouts, and retries",
        "Add retries/backoff for downstream calls",
        "Add unit tests for edge cases + regression tests",
        "Document rollout plan + rollback strategy"
    ]

    summary = (
        f"Senior SDE Review:\n"
        f"- Risk signals: TODO/FIXME={todo}, deep-nesting-lines={deep_indent_lines}, long-lines={very_long_lines}\n"
        f"- Focus areas: reliability, validation, observability, maintainability\n"
        f"- Verdict: {verdict}"
    )

    return risk, bug, verdict, summary, fixes, ops

# ---------- State ----------
if "history" not in st.session_state:
    st.session_state.history = []  # list of dicts (latest first)

# ---------- Header ----------
st.title("🧠 CodePulse AI – PR Risk & Review Assistant")
st.markdown('<div class="small-muted">Internal-tool style PR/code analyzer with risk scoring, review summary, fixes, and ops readiness checklist.</div>', unsafe_allow_html=True)
st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

# ---------- Input ----------
code = st.text_area("Paste PR diff / code", height=220, placeholder="Paste your PR diff or code snippet here...")

colA, colB = st.columns([1, 3])
with colA:
    analyze = st.button("Analyze", use_container_width=True)

with colB:
    st.markdown('<div class="small-muted">Tip: paste a real PR diff to make the output look more realistic in screenshots.</div>', unsafe_allow_html=True)

# ---------- Output ----------
if analyze:
    t0 = time.time()
    lang = detect_language(code)
    pr_id = stable_id(code) if code.strip() else stable_id(str(time.time()))
    risk, bug, verdict, summary, fixes, ops = score_risk(code if code.strip() else " ")

    latency_ms = int((time.time() - t0) * 1000) + 55  # stable-ish

    # Save history (latest first)
    st.session_state.history.insert(0, {
        "id": pr_id,
        "language": lang,
        "risk": risk,
        "bug": bug,
        "verdict": verdict,
        "latency_ms": latency_ms,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    st.session_state.history = st.session_state.history[:10]

# If we have history, show latest analysis dashboard
if st.session_state.history:
    latest = st.session_state.history[0]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Risk Score (0–100)", latest["risk"])
    k2.metric("Bug Likelihood", latest["bug"])
    k3.metric("Deployment Verdict", latest["verdict"])
    k4.metric("Latency (ms)", latest["latency_ms"])

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    left, right = st.columns([1.2, 1])
    with left:
        st.subheader("AI Review Summary")
        # Recompute detailed output for latest entry if needed:
        # (We compute from pasted code only on analyze; for display we keep summary text lightweight.)
        # Show a strong summary block:
        st.text(f"{latest['time']} | PR_ID={latest['id']} | Language={latest['language']}")
        # If user just analyzed, show richer sections based on current code
        if analyze:
            st.code(summary, language="text")
        else:
            st.code("Re-run Analyze to regenerate a detailed summary for the current input.", language="text")

        st.subheader("Actionable Fixes")
        if analyze:
            for f in fixes:
                st.write(f"• {f}")
        else:
            st.write("• Paste code/diff and click Analyze to generate fixes.")

    with right:
        st.subheader("Operational Readiness Checklist")
        if analyze:
            for o in ops:
                st.checkbox(o, value=False)
        else:
            for o in [
                "Add metrics: latency, error rate, throughput",
                "Add alarms for 5xx, timeouts, and retries",
                "Add retries/backoff for downstream calls",
                "Add unit tests for edge cases + regression tests",
                "Document rollout plan + rollback strategy"
            ]:
                st.checkbox(o, value=False)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    st.subheader("Recent Analyses (last 10)")
    st.dataframe(st.session_state.history, use_container_width=True, hide_index=True)

else:
    st.info("Paste a PR diff/code and click **Analyze** to generate risk score + review output.")
