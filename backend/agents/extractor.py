"""
LEXGUARD AI — Extractor Agent
Parses raw contract text and identifies individual clauses with category classification.
Uses Google Gemini with strict JSON schema enforcement.
"""

import json
import google.generativeai as genai
from schemas import ClauseExtraction, ClauseCategory


EXTRACTOR_SYSTEM_PROMPT = """You are a forensic legal data parsing system specialized in contract analysis.
Your mandate is absolute precision in clause identification and classification.

TASK: Analyze the following {contract_type} document text. Identify and extract EVERY clause
that dictates or relates to any of the following categories:

- DATA_PRIVACY: Data collection, processing, sharing, retention, breach notification
- ARBITRATION: Dispute resolution, mandatory arbitration, class action waivers
- IP_TRANSFER: Intellectual property assignment, licensing, work-for-hire, ownership transfers
- INDEMNIFICATION: Hold harmless provisions, defense obligations, third-party claims
- LIMITATION_OF_LIABILITY: Liability caps, damage exclusions, warranty disclaimers
- NON_COMPETE: Non-competition, non-solicitation, restrictive covenants
- TERMINATION: Termination rights, notice periods, cure periods, post-termination obligations
- AUTO_RENEWAL: Automatic renewal, rollover terms, opt-out requirements
- CONFIDENTIALITY: NDA provisions, confidentiality obligations, information handling
- GOVERNING_LAW: Choice of law, jurisdiction, venue selection
- FORCE_MAJEURE: Force majeure events, excuse of performance
- PAYMENT_TERMS: Payment schedules, late fees, interest, pricing changes
- WARRANTY: Representations, warranties, warranty disclaimers
- ASSIGNMENT: Assignment rights, change of control, delegation
- SEVERABILITY: Severability provisions
- OTHER: Any other legally significant clause not in the above categories

RULES:
1. Extract the EXACT verbatim text of each clause — do NOT paraphrase or summarize.
2. Assign each clause to the CLOSEST matching category from the enum above.
3. If a clause spans multiple categories, classify by the PRIMARY obligation.
4. Include the section title/number if present in the document.
5. Do NOT skip any legally significant clause. Be thorough.

Return a JSON array of objects with this exact structure:
[
  {{
    "clause_category": "CATEGORY_NAME",
    "raw_text": "exact verbatim clause text here",
    "section_title": "Section X.X"
  }}
]

Return ONLY the JSON array. No markdown, no commentary, no code fences."""


async def extract_clauses(model: genai.GenerativeModel, document_text: str, contract_type: str = "Unknown", tracker=None) -> list[ClauseExtraction]:
    """
    Extract and classify all legally significant clauses from a document.

    Args:
        model (genai.GenerativeModel): The generative AI model to use.
        document_text (str): The raw text of the contract.
        contract_type (str, optional): The type of contract. Defaults to "Unknown".
        tracker (TokenTracker, optional): Tracker for API telemetry. Defaults to None.

    Returns:
        list[ClauseExtraction]: A list of structured clauses extracted from the document.
        
    Raises:
        ValueError: If the API fails to return a parseable JSON array.
    """
    prompt = EXTRACTOR_SYSTEM_PROMPT.format(contract_type=contract_type)
    response = await model.generate_content_async(
        f"{prompt}\n\n---DOCUMENT START---\n{document_text}\n---DOCUMENT END---",
        generation_config=genai.GenerationConfig(
            temperature=0.1,
            max_output_tokens=8192,
        )
    )

    if tracker:
        tracker.record(response)

    raw_text = response.text.strip()

    # Strip markdown code fences if present
    if raw_text.startswith("```"):
        lines = raw_text.split("\n")
        raw_text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    try:
        clauses_data = json.loads(raw_text)
    except json.JSONDecodeError:
        # Attempt to find JSON array in response
        start = raw_text.find("[")
        end = raw_text.rfind("]") + 1
        if start >= 0 and end > start:
            clauses_data = json.loads(raw_text[start:end])
        else:
            raise ValueError(f"Extractor failed to return valid JSON: {raw_text[:200]}")

    clauses = []
    for item in clauses_data:
        cat_str = item.get("clause_category", "OTHER").upper()
        try:
            category = ClauseCategory(cat_str)
        except ValueError:
            category = ClauseCategory.OTHER

        clause = ClauseExtraction(
            clause_category=category,
            raw_text=item.get("raw_text", ""),
            section_title=item.get("section_title")
        )
        clauses.append(clause)

    return clauses
