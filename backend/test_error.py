import asyncio
import os
import traceback
from agents.pipeline import analyze_contract

async def main():
    try:
        await analyze_contract(
            gemini_api_key=os.environ.get("GEMINI_API_KEY", ""),
            groq_api_key=os.environ.get("GROQ_API_KEY", ""),
            document_text="This is a test contract. All IP is owned by the Company.",
            model_name="llama-3.3-70b-versatile"
        )
    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
