"""
LEXGUARD AI — Full Analysis Pipeline Orchestrator
Coordinates the end-to-end AMADA pipeline:
  1. Guard → 2. Extract → 3. Benchmark + Debate (parallel) → 4. Arbitrate
Includes cumulative token usage tracking across all API calls.
"""

import asyncio
import threading
import google.generativeai as genai
from schemas import AnalysisResult, RiskAssessment, TokenUsage
from agents.guard import sanitize_input
from agents.extractor import extract_clauses
from agents.benchmarker import benchmark_clause
from agents.debate import run_debate
from agents.arbitrator import synthesize_assessment
from agents.groq_wrapper import GroqModelWrapper


class TokenTracker:
    """Thread-safe cumulative token usage tracker."""

    def __init__(self):
        self._lock = threading.Lock()
        self.input_tokens = 0
        self.output_tokens = 0
        self.api_calls = 0

    def record(self, response):
        """Extract and accumulate token usage from a Gemini response."""
        try:
            meta = response.usage_metadata
            with self._lock:
                self.input_tokens += getattr(meta, 'prompt_token_count', 0) or 0
                self.output_tokens += getattr(meta, 'candidates_token_count', 0) or 0
                self.api_calls += 1
        except Exception:
            with self._lock:
                self.api_calls += 1

    def to_schema(self) -> TokenUsage:
        return TokenUsage(
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
            total_tokens=self.input_tokens + self.output_tokens,
            api_calls=self.api_calls,
        )


async def analyze_contract(
    gemini_api_key: str, 
    groq_api_key: str,
    document_text: str, 
    model_name: str = "gemini-3.1-pro-preview",
    user_context: str = "",
    user_role: str = "recipient",
    contract_type: str = "Unknown"
) -> AnalysisResult:
    """
    Run the full LEXGUARD analysis pipeline on a contract document.
    
    Pipeline:
      1. Anti-injection guard
      2. Clause extraction
      3. For each clause (in parallel):
         a. Common Paper benchmarking
         b. AMADA adversarial debate
      4. Arbitrator synthesis
      5. Aggregate into final AnalysisResult with token usage

    Args:
        gemini_api_key (str): The Google Gemini API key.
        groq_api_key (str): The Groq API key for Llama/Qwen models.
        document_text (str): The raw text of the uploaded contract.
        model_name (str, optional): The AI model to use. Defaults to "gemini-3.1-pro-preview".
        user_context (str, optional): Background info provided by the user. Defaults to "".
        user_role (str, optional): Whether the user is the drafter or recipient. Defaults to "recipient".
        contract_type (str, optional): The type of contract being analyzed. Defaults to "Unknown".

    Returns:
        AnalysisResult: The structured Pydantic object containing the overall risk score,
                        extracted clauses, debate transcripts, and token telemetry.
    """
    tracker = TokenTracker()

    # Step 1: Guard
    sanitization = sanitize_input(document_text)
    if not sanitization.is_safe:
        return AnalysisResult(
            document_title="⚠️ Security Alert",
            overall_risk_score=0,
            overall_risk_level="N/A",
            total_clauses_analyzed=0,
            executive_summary=f"Document rejected: {sanitization.threat_detected}. "
                              "The uploaded text contains patterns associated with prompt injection attacks. "
                              "Please upload a genuine legal document.",
            clauses=[]
        )

    clean_text = sanitization.sanitized_text

    # Configure Model Provider
    if model_name.startswith("gemini"):
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel(model_name)
    else:
        # Assumed Groq model
        model = GroqModelWrapper(model_name=model_name, api_key=groq_api_key)

    # Step 2: Extract clauses
    clauses = await extract_clauses(model, clean_text, contract_type, tracker)

    if not clauses:
        return AnalysisResult(
            document_title="Analysis Complete",
            overall_risk_score=0,
            overall_risk_level="LOW",
            total_clauses_analyzed=0,
            executive_summary="No legally significant clauses were identified in this document. "
                              "The text may not be a legal contract, or it may contain only standard boilerplate.",
            clauses=[],
            token_usage=tracker.to_schema()
        )

    # Step 3: For each clause, run benchmark + debate in parallel
    async def process_single_clause(clause):
        benchmark_result, debate_result = await asyncio.gather(
            benchmark_clause(model, clause, tracker),
            run_debate(model, clause, user_context, user_role, contract_type, tracker)
        )
        # Step 4: Arbitrate
        assessment = await synthesize_assessment(
            model, clause, debate_result, benchmark_result, user_context, user_role, tracker
        )
        return assessment

    # Process all clauses concurrently (with a semaphore to avoid rate limits)
    # Groq free tier has extremely strict TPM limits (12k for 70B), so we process 1 clause at a time.
    # Gemini can handle 3 at a time.
    max_concurrency = 1 if not model_name.startswith("gemini") else 3
    semaphore = asyncio.Semaphore(max_concurrency)

    async def throttled_process(clause):
        async with semaphore:
            return await process_single_clause(clause)

    assessments: list[RiskAssessment] = await asyncio.gather(
        *[throttled_process(c) for c in clauses]
    )

    # Sort by risk score descending
    assessments.sort(key=lambda a: a.risk_score, reverse=True)

    # Step 5: Aggregate results
    total = len(assessments)
    high_risk = sum(1 for a in assessments if a.risk_level in ("HIGH", "CRITICAL"))
    medium_risk = sum(1 for a in assessments if a.risk_level == "MEDIUM")
    low_risk = sum(1 for a in assessments if a.risk_level == "LOW")

    # Weighted overall score
    if assessments:
        overall_score = int(sum(a.risk_score for a in assessments) / total)
    else:
        overall_score = 0

    if overall_score <= 20:
        overall_level = "LOW"
    elif overall_score <= 45:
        overall_level = "MEDIUM"
    elif overall_score <= 70:
        overall_level = "HIGH"
    else:
        overall_level = "CRITICAL"

    # Generate executive summary
    if high_risk > 0:
        exec_summary = (
            f"⚠️ This contract contains {high_risk} high-risk clause(s) that require immediate attention. "
            f"Out of {total} clauses analyzed, {high_risk} pose significant legal, financial, or privacy risks. "
            "We strongly recommend consulting a legal professional before signing."
        )
    elif medium_risk > 0:
        exec_summary = (
            f"This contract contains {medium_risk} clause(s) with moderate risk. "
            f"While {total} clauses were analyzed and most appear standard, "
            "some terms deviate from industry norms and warrant careful review."
        )
    else:
        exec_summary = (
            f"This contract appears relatively standard. All {total} clauses analyzed "
            "fall within acceptable risk parameters based on Common Paper industry benchmarks."
        )

    return AnalysisResult(
        document_title="Contract Analysis Complete",
        overall_risk_score=overall_score,
        overall_risk_level=overall_level,
        total_clauses_analyzed=total,
        high_risk_count=high_risk,
        medium_risk_count=medium_risk,
        low_risk_count=low_risk,
        executive_summary=exec_summary,
        clauses=assessments,
        token_usage=tracker.to_schema()
    )
