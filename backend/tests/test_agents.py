import pytest
from unittest.mock import AsyncMock, patch
from schemas import AnalysisResult
from agents.pipeline import analyze_contract

@pytest.fixture
def mock_gemini():
    """Mock the Google GenerativeAI API."""
    with patch("agents.pipeline.genai.GenerativeModel") as MockModel:
        instance = MockModel.return_value
        
        # We need to mock generate_content_async to return structured JSON
        async def mock_generate(*args, **kwargs):
            class MockResponse:
                def __init__(self, text):
                    self.text = text
                    self.usage_metadata = type('obj', (object,), {'prompt_token_count': 10, 'candidates_token_count': 10})()
            
            prompt = args[0]
            if "forensic legal data" in prompt:
                # Mock Extractor
                return MockResponse('[{"raw_text": "No competition.", "clause_category": "Non_Compete", "section_title": "1"}]')
            elif "BENCHMARK ANALYSIS" in prompt:
                # Mock Benchmarker
                return MockResponse("This is non-standard.")
            elif "VENDOR COUNSEL" in prompt:
                # Mock Vendor
                return MockResponse("This protects our IP.")
            elif "CONSUMER ADVOCATE" in prompt:
                # Mock Consumer
                return MockResponse("This destroys the contractor's career.")
            else:
                # Mock Arbitrator fallback
                return MockResponse('{"risk_score": 85, "explanation": "High risk.", "consequence_simulation": "You will be sued."}')
                
        instance.generate_content_async = AsyncMock(side_effect=mock_generate)
        yield instance

@pytest.mark.asyncio
async def test_analyze_contract_pipeline(mock_gemini):
    """Test the full AMADA pipeline with mocked LLMs."""
    result = await analyze_contract(
        gemini_api_key="fake",
        groq_api_key="",
        document_text="Contractor shall not compete.",
        model_name="gemini-3.1-pro-preview",
        user_context="I am a developer",
        user_role="recipient",
        contract_type="Employment"
    )
    
    assert isinstance(result, AnalysisResult)
    assert len(result.clauses) == 1
    assert result.clauses[0].clause_category.value == "NON_COMPETE"
    assert result.clauses[0].risk_score == 85
    assert result.token_usage.total_tokens > 0
    assert "You will be sued." in result.clauses[0].consequence_simulation
