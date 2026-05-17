"""
LEXGUARD AI — Pydantic v2 Data Contracts
Type-safe schemas enforcing strict data integrity across the multi-agent pipeline.
"""

from __future__ import annotations

import uuid
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ClauseCategory(str, Enum):
    """Standardized taxonomy for contract clause classification."""
    DATA_PRIVACY = "DATA_PRIVACY"
    ARBITRATION = "ARBITRATION"
    IP_TRANSFER = "IP_TRANSFER"
    INDEMNIFICATION = "INDEMNIFICATION"
    LIMITATION_OF_LIABILITY = "LIMITATION_OF_LIABILITY"
    NON_COMPETE = "NON_COMPETE"
    TERMINATION = "TERMINATION"
    AUTO_RENEWAL = "AUTO_RENEWAL"
    CONFIDENTIALITY = "CONFIDENTIALITY"
    GOVERNING_LAW = "GOVERNING_LAW"
    FORCE_MAJEURE = "FORCE_MAJEURE"
    PAYMENT_TERMS = "PAYMENT_TERMS"
    WARRANTY = "WARRANTY"
    ASSIGNMENT = "ASSIGNMENT"
    SEVERABILITY = "SEVERABILITY"
    OTHER = "OTHER"


class ClauseExtraction(BaseModel):
    """Output from the Extractor Agent — a single identified clause."""
    clause_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    clause_category: ClauseCategory
    raw_text: str = Field(
        ...,
        min_length=10,
        description="The exact verbatim text extracted from the document."
    )
    section_title: Optional[str] = Field(
        None,
        description="The section heading or number the clause falls under."
    )


class DebateTranscript(BaseModel):
    """Output from the AMADA adversarial debate protocol."""
    clause_id: str
    vendor_argument: str = Field(
        ...,
        description="Pro-vendor defense: why this clause is standard and reasonable."
    )
    consumer_argument: str = Field(
        ...,
        description="Pro-consumer attack: hidden liabilities and exploitative terms."
    )


class BenchmarkResult(BaseModel):
    """Output from the Common Paper Benchmark Agent."""
    clause_id: str
    benchmark_deviation: bool = Field(
        ...,
        description="True if clause significantly deviates from Common Paper standards."
    )
    deviation_rationale: str = Field(
        "",
        description="One-sentence explanation of how/why it deviates."
    )
    matched_standard: Optional[str] = Field(
        None,
        description="Which Common Paper standard was used for comparison."
    )


class RiskAssessment(BaseModel):
    """Final output from the Arbitrator Synthesis Agent for a single clause."""
    clause_id: str
    clause_category: ClauseCategory
    section_title: Optional[str] = None
    raw_text: str
    risk_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Severity score: 0 = harmless, 100 = predatory."
    )
    risk_level: str = Field(
        ...,
        description="LOW, MEDIUM, HIGH, or CRITICAL"
    )
    plain_language_summary: str = Field(
        ...,
        description="Jargon-free explanation at ~6th-grade reading level."
    )
    consequence_simulation: str = Field(
        ...,
        description="Narrative real-world scenario of worst-case impact."
    )
    benchmark_deviation: bool = False
    deviation_rationale: str = ""
    vendor_argument: str = ""
    consumer_argument: str = ""


class TokenUsage(BaseModel):
    """Tracks cumulative AI token usage across the pipeline."""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    api_calls: int = 0


class AnalysisResult(BaseModel):
    """Top-level response wrapping the full contract analysis."""
    document_title: str = "Uploaded Contract"
    overall_risk_score: int = Field(..., ge=0, le=100)
    overall_risk_level: str = "MEDIUM"
    total_clauses_analyzed: int = 0
    high_risk_count: int = 0
    medium_risk_count: int = 0
    low_risk_count: int = 0
    executive_summary: str = ""
    clauses: list[RiskAssessment] = []
    token_usage: TokenUsage = Field(default_factory=TokenUsage)


class SanitizationResult(BaseModel):
    """Output from the anti-injection guard."""
    is_safe: bool
    threat_detected: Optional[str] = None
    sanitized_text: str = ""
