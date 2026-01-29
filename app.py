import re

def score_risk(code: str):
    lines = code.splitlines()
    text = code

    todo = len(re.findall(r"\b(TODO|FIXME)\b", text, flags=re.I))
    nesting = max([len(re.findall(r"^\s+", l))[0:0].__len__() for l in lines] + [0])  # safe fallback
    deep_nesting = sum(1 for l in lines if len(re.match(r"^\s*", l).group(0)) >= 12)

    has_try = bool(re.search(r"\btry\b|\bexcept\b|\bcatch\b", text))
    has_logging = bool(re.search(r"\blogger\b|\blogging\b|\bconsole\.log\b|\bprint\(", text))
    has_validation = bool(re.search(r"\bvalidate\b|\bassert\b|\bisinstance\b|\bif\s+\w+\s*==\s*None\b|\bnull\b", text, flags=re.I))

    long_lines = sum(1 for l in lines if len(l) > 120)

    risk = 20
    risk += todo * 8
    risk += min(deep_nesting, 8) * 6
    risk += min(long_lines, 10) * 2
    risk += 10 if not has_try else 0
    risk += 10 if not has_validation else 0
    risk -= 5 if has_logging else 0

    risk = max(0, min(100, risk))
    bug = "High" if risk > 70 else "Medium" if risk > 40 else "Low"
    verdict = "Block ❌" if risk > 75 else "Needs Review ⚠️" if risk >= 50 else "Safe ✅"

    fixes = []
    if todo: fixes.append("Resolve TODO/FIXME items before merge.")
    if not has_try: fixes.append("Add error handling (try/except or safe fallbacks).")
    if not has_validation: fixes.append("Add input validation + boundary checks.")
    if long_lines > 0: fixes.append("Break long lines / simplify complex expressions.")
    if deep_nesting > 3: fixes.append("Refactor deeply nested logic into smaller functions.")
    if not has_logging: fixes.append("Add structured logging for observability.")

    ops = [
        "Add metrics: latency, error rate, throughput",
        "Add alarms for 5xx + timeouts",
        "Add retry/backoff for downstream calls",
        "Add unit tests for edge cases",
    ]

    return risk, bug, verdict, fixes, ops
