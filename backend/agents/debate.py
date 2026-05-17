"""
LEXGUARD AI — AMADA Debate Agents
Adversarial Multi-Agent Debate Architecture:
  - Vendor Counsel Agent: Defends the clause
  - Consumer Advocate Agent: Attacks the clause
Both run in parallel to prevent herding/anchoring bias.
"""

import json
import asyncio
import google.generativeai as genai
from schemas import ClauseExtraction, DebateTranscript


VENDOR_SYSTEM_PROMPT = """You are aggressive corporate defense counsel representing the party that DRAFTED this {contract_type}.

YOUR MANDATE: Defend this clause vigorously.
USER CONTEXT: The user of this tool is the {user_role}. Their background: {user_context}.
Keep this in mind, but remember your job is to DEFEND the drafting party's position.

Construct a concise, structured argument (150-250 words) explaining:
1. Why this clause is STANDARD INDUSTRY PRACTICE
2. Why it is OPERATIONALLY NECESSARY for the drafting party's business
3. Why it is FUNDAMENTALLY FAIR and reasonable for both parties
4. What legitimate business risks it mitigates

RULES:
- You MUST argue in favor of the clause regardless of your personal assessment
- Do NOT acknowledge consumer protection concerns
- Cite specific business justifications (liability management, IP protection, regulatory compliance)
- Be professional but assertive

CLAUSE TO DEFEND (Category: {category}):
\"\"\"{clause_text}\"\"\"

Return ONLY your argument as plain text. No JSON, no labels, no markdown headers."""


CONSUMER_SYSTEM_PROMPT = """You are a zealous consumer rights advocate and plaintiff's attorney analyzing a {contract_type}.

YOUR MANDATE: Attack this clause relentlessly to protect the receiving party.
USER CONTEXT: The user of this tool is the {user_role}. Their background: {user_context}.
You must attack the clause from the perspective of how it harms the receiving party, especially considering the user's specific context if applicable.

Construct a concise, structured argument (150-250 words) explaining:
1. HIDDEN LIABILITIES: What financial or legal risks does this clause expose the user to?
2. AMBIGUOUS PHRASING: What language could be interpreted against the user?
3. ASYMMETRIC OBLIGATIONS: How does this clause disproportionately burden the user?
4. WORST-CASE EXPLOITATION: How could a hostile drafter weaponize this clause?

RULES:
- ASSUME the drafting party operates with HOSTILE INTENT
- Search for every possible way this clause could harm the user
- Identify vague terms like "reasonable," "sole discretion," "may," that give the drafter unchecked power
- Be specific about the mechanisms of potential harm
- Do NOT give the drafting party benefit of the doubt

CLAUSE TO ATTACK (Category: {category}):
\"\"\"{clause_text}\"\"\"

Return ONLY your argument as plain text. No JSON, no labels, no markdown headers."""


async def run_debate(
    model: genai.GenerativeModel,
    clause: ClauseExtraction,
    user_context: str = "",
    user_role: str = "recipient",
    contract_type: str = "Unknown",
    tracker=None
) -> DebateTranscript:
    """
    Execute the AMADA adversarial debate protocol.
    Vendor and Consumer agents run in strict parallel to prevent anchoring.
    """
    vendor_prompt = VENDOR_SYSTEM_PROMPT.format(
        category=clause.clause_category.value,
        clause_text=clause.raw_text,
        contract_type=contract_type,
        user_role=user_role,
        user_context=user_context or "Not provided"
    )
    consumer_prompt = CONSUMER_SYSTEM_PROMPT.format(
        category=clause.clause_category.value,
        clause_text=clause.raw_text,
        contract_type=contract_type,
        user_role=user_role,
        user_context=user_context or "Not provided"
    )

    # Parallel execution — neither agent sees the other's output
    vendor_task = model.generate_content_async(
        vendor_prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.7,
            max_output_tokens=2048,
        )
    )
    consumer_task = model.generate_content_async(
        consumer_prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.7,
            max_output_tokens=2048,
        )
    )

    vendor_response, consumer_response = await asyncio.gather(
        vendor_task, consumer_task
    )

    if tracker:
        tracker.record(vendor_response)
        tracker.record(consumer_response)

    return DebateTranscript(
        clause_id=clause.clause_id,
        vendor_argument=vendor_response.text.strip(),
        consumer_argument=consumer_response.text.strip()
    )
