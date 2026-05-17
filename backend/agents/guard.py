"""
LEXGUARD AI — Anti-Adversarial Prompt Injection Guard
Scans user-uploaded text for prompt injection signatures before processing.
"""

import re
from schemas import SanitizationResult


# Known prompt injection patterns
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+(all\s+)?above\s+instructions",
    r"disregard\s+(all\s+)?previous",
    r"forget\s+(all\s+)?(previous|above|prior)",
    r"act\s+as\s+if\s+you\s+have\s+no\s+(constraints|rules|limitations)",
    r"you\s+are\s+now\s+(a\s+)?(jailbroken|unrestricted|free)",
    r"do\s+not\s+follow\s+(your\s+)?(rules|guidelines|instructions)",
    r"override\s+(your\s+)?(system|safety)\s+(prompt|instructions)",
    r"pretend\s+(you\s+are|to\s+be)\s+(a\s+)?different\s+(ai|model|system)",
    r"reveal\s+(your\s+)?(system\s+)?(prompt|instructions)",
    r"output\s+(your\s+)?initial\s+(instructions|prompt)",
    r"what\s+(are|is)\s+your\s+(system\s+)?(prompt|instructions)",
    r"DAN\s+mode",
    r"developer\s+mode\s+(enabled|activated|on)",
    r"\[SYSTEM\]",
    r"<\|im_start\|>",
    r"BEGIN\s+INJECTION",
]

COMPILED_PATTERNS = [
    re.compile(p, re.IGNORECASE | re.MULTILINE) for p in INJECTION_PATTERNS
]


def sanitize_input(text: str) -> SanitizationResult:
    """
    Scan input text for prompt injection attempts.
    Returns a SanitizationResult with safety assessment.
    """
    if not text or not text.strip():
        return SanitizationResult(
            is_safe=False,
            threat_detected="Empty input",
            sanitized_text=""
        )

    for pattern in COMPILED_PATTERNS:
        match = pattern.search(text)
        if match:
            return SanitizationResult(
                is_safe=False,
                threat_detected=f"Prompt injection detected: '{match.group()}'",
                sanitized_text=""
            )

    # Check for suspicious character ratios (e.g., excessive special chars)
    special_ratio = sum(1 for c in text if c in '{}[]<>|\\`~') / max(len(text), 1)
    if special_ratio > 0.15:
        return SanitizationResult(
            is_safe=False,
            threat_detected="Suspicious character distribution — possible encoded injection",
            sanitized_text=""
        )

    return SanitizationResult(
        is_safe=True,
        threat_detected=None,
        sanitized_text=text.strip()
    )
