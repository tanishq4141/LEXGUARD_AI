"""
LEXGUARD AI — Arbitrator Synthesis Agent
The impartial judicial authority that weighs vendor/consumer arguments,
factors in benchmark deviations, and produces the final risk assessment
with plain-language explanation and consequence simulation.
"""

import json
import google.generativeai as genai
from schemas import (
    ClauseExtraction,
    DebateTranscript,
    BenchmarkResult,
    RiskAssessment,
)


ARBITRATOR_SYSTEM_PROMPT = """You are an impartial legal arbitrator with 30 years of experience in contract law.
You must produce a fair, balanced, and mathematically grounded risk assessment TAILORED SPECIFICALLY TO THE USER.

USER CONTEXT:
- Role in Contract: {user_role} (Are they drafting/issuing it, or receiving/signing it?)
- Background/Details: {user_context}

CHAIN-OF-THOUGHT PROTOCOL — Follow these steps precisely:

Step 1: REVIEW the Vendor's defense argument and the Consumer's attack argument.
Step 2: FACTOR in whether the clause deviates from Common Paper industry standards.
Step 3: CALCULATE a risk severity score from 0 to 100 SPECIFICALLY FOR THE USER:
  - If the user is the 'drafter' (From Me): A clause that heavily protects the drafter is LOW risk. A clause that exposes the drafter to liability or strips their rights is HIGH risk.
  - If the user is the 'recipient' (For Me): A clause that heavily protects the drafter is HIGH/CRITICAL risk to the user. A balanced or pro-recipient clause is LOW risk.
  - Score mapping: 
    - 0-20: LOW risk — safe, standard, or highly protective of the user
    - 21-45: MEDIUM risk — some imbalance but within acceptable range
    - 46-70: HIGH risk — significant exposure for the user
    - 71-100: CRITICAL risk — predatory, exploitative, or severely dangerous to the user
Step 4: DETERMINE the risk_level as one of: LOW, MEDIUM, HIGH, CRITICAL
Step 5: WRITE a plain-language summary (2-3 sentences, 6th-grade reading level)
  explaining what this clause means in everyday language for the user. NO legal jargon.
Step 6: GENERATE a concrete "Consequence Simulation" — a specific, relatable
  real-world narrative (3-4 sentences) showing the WORST-CASE scenario if
  the user accepts this clause. Incorporate the user's Background/Details to make it highly personalized.
  Make it visceral and specific (e.g., dollar amounts, timeframes).

INPUT DATA:
- Clause Category: {category}
- Section: {section}
- Original Clause Text: \"\"\"{clause_text}\"\"\"
- Vendor Defense (Pro-Drafter): \"\"\"{vendor_argument}\"\"\"
- Consumer Attack (Pro-Recipient): \"\"\"{consumer_argument}\"\"\"
- Benchmark Deviation: {benchmark_deviation}
- Deviation Rationale: {deviation_rationale}

Return ONLY a JSON object with this exact structure:
{{
  "risk_score": <integer 0-100>,
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "plain_language_summary": "...",
  "consequence_simulation": "..."
}}

No markdown, no commentary, no code fences. Just the JSON object."""


async def synthesize_assessment(
    model: genai.GenerativeModel,
    clause: ClauseExtraction,
    debate: DebateTranscript,
    benchmark: BenchmarkResult,
    user_context: str = "",
    user_role: str = "recipient",
    tracker=None,
) -> RiskAssessment:
    """
    The Arbitrator Agent synthesizes all pipeline inputs into a final,
    structured RiskAssessment with score, summary, and consequence simulation.
    """
    prompt = ARBITRATOR_SYSTEM_PROMPT.format(
        category=clause.clause_category.value,
        section=clause.section_title or "Not specified",
        clause_text=clause.raw_text,
        vendor_argument=debate.vendor_argument,
        consumer_argument=debate.consumer_argument,
        benchmark_deviation=benchmark.benchmark_deviation,
        deviation_rationale=benchmark.deviation_rationale or "N/A",
        user_role=user_role,
        user_context=user_context or "Not provided"
    )

    response = await model.generate_content_async(
        prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.3,
            max_output_tokens=2048,
        )
    )

    if tracker:
        tracker.record(response)

    raw = response.text.strip()

    # Strip code fences
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(raw[start:end])
        else:
            # Fallback with reasonable defaults
            data = {
                "risk_score": 50,
                "risk_level": "MEDIUM",
                "plain_language_summary": "This clause could not be fully analyzed. Please review it carefully with a legal professional.",
                "consequence_simulation": "Without a complete analysis, the potential consequences of this clause remain uncertain. We recommend professional legal review."
            }

    # Clamp risk_score to valid range
    risk_score = max(0, min(100, int(data.get("risk_score", 50))))

    # Derive risk_level if not provided correctly
    risk_level = data.get("risk_level", "MEDIUM").upper()
    if risk_level not in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
        if risk_score <= 20:
            risk_level = "LOW"
        elif risk_score <= 45:
            risk_level = "MEDIUM"
        elif risk_score <= 70:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"

    return RiskAssessment(
        clause_id=clause.clause_id,
        clause_category=clause.clause_category,
        section_title=clause.section_title,
        raw_text=clause.raw_text,
        risk_score=risk_score,
        risk_level=risk_level,
        plain_language_summary=data.get("plain_language_summary", ""),
        consequence_simulation=data.get("consequence_simulation", ""),
        benchmark_deviation=benchmark.benchmark_deviation,
        deviation_rationale=benchmark.deviation_rationale,
        vendor_argument=debate.vendor_argument,
        consumer_argument=debate.consumer_argument,
    )
