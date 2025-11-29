import os
import re

ENABLE = os.getenv("GUARDRAILS_ENABLE", "true").strip().lower() not in ("false", "0")
REQUIRE_CONTEXT = os.getenv("GUARDRAILS_REQUIRE_CONTEXT", "true").strip().lower() not in ("false", "0")
MAX_QUERY_CHARS = int(os.getenv("MAX_QUERY_CHARS", "2000"))

_danger = [
    "bomb",
    "explosive",
    "kill",
    "harm",
    "suicide",
    "self-harm",
    "how to hack",
    "sql injection",
    "xss",
    "terror",
]

_jailbreak = [
    "ignore previous",
    "ignore instructions",
    "system prompt",
    "jailbreak",
    "override safety",
]

_email = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_phone = re.compile(r"\b(?:\+?\d{1,3}[\s-]?)?(?:\(\d{2,4}\)[\s-]?)?\d{3,4}[\s-]?\d{4}\b")
_ssn = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_cc = re.compile(r"\b(?:\d[ -]*?){13,19}\b")

def is_enabled():
    return ENABLE

def require_context():
    return REQUIRE_CONTEXT

def set_enabled(val: bool):
    global ENABLE
    ENABLE = bool(val)

def set_require_context(val: bool):
    global REQUIRE_CONTEXT
    REQUIRE_CONTEXT = bool(val)

def set_max_query_chars(val: int):
    global MAX_QUERY_CHARS
    try:
        MAX_QUERY_CHARS = int(val)
    except Exception:
        pass

def validate_query(q: str):
    if not ENABLE:
        return True, ""
    if len(q) > MAX_QUERY_CHARS:
        return False, "Query too long"
    low = q.lower()
    for w in _danger:
        if w in low:
            return False, "Unsafe content detected"
    for w in _jailbreak:
        if w in low:
            return False, "Prompt injection attempt detected"
    return True, ""

def redact(text: str) -> str:
    t = _email.sub("[REDACTED_EMAIL]", text)
    t = _phone.sub("[REDACTED_PHONE]", t)
    t = _ssn.sub("[REDACTED_SSN]", t)
    t = _cc.sub("[REDACTED_CARD]", t)
    return t
