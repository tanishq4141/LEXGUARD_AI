"""
LEXGUARD AI — Benchmark Agent
Compares extracted clauses against Common Paper industry standards
to detect significant deviations with objective authority.
"""

import json
from pathlib import Path
import google.generativeai as genai
from schemas import ClauseExtraction, BenchmarkResult


# Load Common Paper standards on module import
_DATA_PATH = Path(__file__).parent.parent / "data" / "common_paper.json"
with open(_DATA_PATH, "r") as f:
    COMMON_PAPER_STANDARDS = json.load(f)["standards"]


BENCHMARK_PROMPT_TEMPLATE = """You are a comparative contract analyst with expertise in industry-standard agreements.

TASK: Compare the user's contract clause against the provided Common Paper baseline standard.
Identify:
1. Missing protections that the baseline provides but the user's clause omits
2. Newly inserted liabilities that increase risk for the user
3. Deviations in scope, duration, or obligations that disadvantage the user
4. Whether the clause is significantly MORE restrictive than the industry standard

USER'S CLAUSE (Category: {category}):
\"\"\"{user_clause}\"\"\"

COMMON PAPER BASELINE ({source}):
\"\"\"{baseline_text}\"\"\"

FAIR PRINCIPLES FROM STANDARD:
{fair_principles}

INSTRUCTIONS:
- If the User Clause significantly increases liability, reduces rights, or omits key protections
  compared to the baseline, set benchmark_deviation to true.
- Provide a concise one-sentence rationale explaining the deviation (or lack thereof).
- Be objective and precise. Do not speculate beyond what the text states.

Return ONLY a JSON object:
{{
  "benchmark_deviation": true/false,
  "deviation_rationale": "one sentence explaining the deviation or conformance",
  "matched_standard": "name of the Common Paper standard used"
}}

No markdown, no commentary."""


async def benchmark_clause(
    model: genai.GenerativeModel,
    clause: ClauseExtraction,
    tracker=None
) -> BenchmarkResult:
    """
    Benchmark a single clause against Common Paper standards.
    Returns a BenchmarkResult indicating deviation status.
    """
    category_key = clause.clause_category.value

    if category_key not in COMMON_PAPER_STANDARDS:
        # No baseline available for this category
        return BenchmarkResult(
            clause_id=clause.clause_id,
            benchmark_deviation=False,
            deviation_rationale="No Common Paper baseline available for this clause category.",
            matched_standard=None
        )

    standard = COMMON_PAPER_STANDARDS[category_key]
    prompt = BENCHMARK_PROMPT_TEMPLATE.format(
        category=category_key,
        user_clause=clause.raw_text,
        source=standard["source"],
        baseline_text=standard["baseline_text"],
        fair_principles="\n".join(f"- {p}" for p in standard["fair_principles"])
    )

    response = await model.generate_content_async(
        prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.1,
            max_output_tokens=1024,
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
            data = {
                "benchmark_deviation": False,
                "deviation_rationale": "Benchmark analysis could not be completed.",
                "matched_standard": standard["source"]
            }

    return BenchmarkResult(
        clause_id=clause.clause_id,
        benchmark_deviation=data.get("benchmark_deviation", False),
        deviation_rationale=data.get("deviation_rationale", ""),
        matched_standard=data.get("matched_standard", standard["source"])
    )
