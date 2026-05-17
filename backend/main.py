"""
LEXGUARD AI — FastAPI Application
Endpoints for contract upload, analysis, and health check.
"""

import os
import io
import asyncio
import uuid
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional

try:
    from google.cloud import storage
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from schemas import AnalysisResult
from agents.pipeline import analyze_contract

# Load environment
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    if not GEMINI_API_KEY:
        print("⚠️  WARNING: GEMINI_API_KEY not set in .env file!")
    if not GROQ_API_KEY:
        print("⚠️  WARNING: GROQ_API_KEY not set in .env file! (Required for Groq models)")
    if GEMINI_API_KEY or GROQ_API_KEY:
        print("✅ LEXGUARD AI — Backend ready")
    yield
    print("🛑 LEXGUARD AI — Shutting down")


app = FastAPI(
    title="LEXGUARD AI",
    description="AI-Powered Contract Intelligence Agent with Adversarial Multi-Agent Debate",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for frontend (Hackathon config, consider restricting for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # NOTE: Set to specific domains in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "LEXGUARD AI",
        "gemini_api_key_configured": bool(GEMINI_API_KEY),
        "groq_api_key_configured": bool(GROQ_API_KEY),
    }


@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze_text(
    text: str = Form(...),
    model: str = Form("gemini-3.1-pro-preview"),
    user_context: str = Form(""),
    user_role: str = Form("recipient"),
    contract_type: str = Form("Unknown"),
):
    """
    Analyze raw contract text through the full AMADA pipeline.
    """
    is_groq = not model.startswith("gemini")
    
    if not is_groq and not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY not configured. Add it to the .env file."
        )
    if is_groq and not GROQ_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY not configured. Add it to the .env file."
        )

    if not text.strip():
        raise HTTPException(status_code=400, detail="No text provided.")

    if len(text) > 200_000:
        raise HTTPException(
            status_code=400,
            detail="Document too large. Maximum 200,000 characters."
        )

    try:
        result = await analyze_contract(
            gemini_api_key=GEMINI_API_KEY,
            groq_api_key=GROQ_API_KEY,
            document_text=text, 
            model_name=model,
            user_context=user_context,
            user_role=user_role,
            contract_type=contract_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


def upload_to_gcs_background(text: str, ext: str):
    """Background task to upload contract text to Google Cloud Storage (Hackathon Integration)."""
    if not GCS_AVAILABLE:
        return
    try:
        client = storage.Client()
        bucket = client.bucket("lexguard-contracts-bucket")
        blob = bucket.blob(f"upload_{uuid.uuid4()}{ext}")
        blob.upload_from_string(text)
    except Exception as e:
        print(f"GCS Upload failed (expected if not configured): {e}")

@app.post("/api/upload", response_model=AnalysisResult)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    model: str = Form("gemini-3.1-pro-preview"),
    user_context: str = Form(""),
    user_role: str = Form("recipient"),
    contract_type: str = Form("Unknown"),
):
    """
    Upload a PDF or DOCX file for analysis.
    Extracts text and runs the full AMADA pipeline.
    """
    is_groq = not model.startswith("gemini")

    if not is_groq and not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY not configured. Add it to the .env file."
        )
    if is_groq and not GROQ_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY not configured. Add it to the .env file."
        )

    filename = file.filename or ""
    ext = Path(filename).suffix.lower()

    if ext not in (".pdf", ".docx", ".txt"):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a PDF, DOCX, or TXT file."
        )

    content = await file.read()
    
    # Security: 10MB file size limit
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="File too large. Maximum size is 10MB."
        )

    try:
        if ext == ".pdf":
            import pdfplumber
            text_parts = []
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            document_text = "\n\n".join(text_parts)

        elif ext == ".docx":
            import docx
            doc = docx.Document(io.BytesIO(content))
            document_text = "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())

        elif ext == ".txt":
            document_text = content.decode("utf-8", errors="replace")

        else:
            raise HTTPException(status_code=400, detail="Unsupported format.")

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to extract text from file: {str(e)}"
        )

    # Trigger GCS background upload for Hackathon points
    background_tasks.add_task(upload_to_gcs_background, document_text, ext)

    if not document_text.strip():
        raise HTTPException(
            status_code=400,
            detail="No text could be extracted from the uploaded file."
        )

    if len(document_text) > 200_000:
        raise HTTPException(
            status_code=400,
            detail="Extracted text too large. Maximum 200,000 characters."
        )

    try:
        result = await analyze_contract(
            gemini_api_key=GEMINI_API_KEY,
            groq_api_key=GROQ_API_KEY,
            document_text=document_text, 
            model_name=model,
            user_context=user_context,
            user_role=user_role,
            contract_type=contract_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# Sample contract for demo/testing
SAMPLE_CONTRACT = """
INDEPENDENT CONTRACTOR AGREEMENT

1. INTELLECTUAL PROPERTY ASSIGNMENT
All Work Product, including but not limited to all inventions, discoveries, designs, code, algorithms,
documentation, and any other materials created, conceived, or developed by Contractor during the term
of this Agreement, whether or not related to the services performed hereunder, shall be the sole and
exclusive property of the Company. Contractor hereby irrevocably assigns to the Company all right,
title, and interest in and to any and all Work Product, including all intellectual property rights therein.
This assignment includes any works created using Contractor's pre-existing tools, frameworks, or
methodologies. Contractor waives all moral rights in the Work Product to the fullest extent permitted by law.

2. NON-COMPETITION COVENANT
During the term of this Agreement and for a period of thirty-six (36) months following its termination
for any reason, Contractor agrees not to, directly or indirectly, engage in, consult for, or provide
services to any business, entity, or individual that competes with or is similar to the Company's
business, anywhere in the world. This restriction applies regardless of whether the Contractor
initiated the termination or whether the Company terminated without cause.

3. LIMITATION OF LIABILITY
Company's total aggregate liability under this Agreement shall not exceed the fees paid to Contractor
in the thirty (30) days immediately preceding the claim. IN NO EVENT SHALL THE COMPANY BE LIABLE
FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES OF ANY KIND.
Contractor's liability to the Company shall be unlimited and shall include all direct, indirect,
incidental, and consequential damages arising from Contractor's performance or failure to perform.

4. MANDATORY ARBITRATION AND DISPUTE RESOLUTION
Any dispute, claim, or controversy arising out of or relating to this Agreement shall be resolved
exclusively through binding arbitration administered by an arbitration body selected solely by the
Company, conducted in a location determined solely by the Company. The Contractor shall bear all
arbitration costs, including filing fees, arbitrator compensation, and the Company's legal fees.
The Contractor waives any right to participate in a class action, class arbitration, or any
consolidated or representative proceeding. The arbitration proceedings and all related documents
shall remain strictly confidential.

5. DATA COLLECTION AND PRIVACY
Contractor acknowledges and agrees that the Company may collect, store, process, and share
Contractor's personal data, including but not limited to biometric data, location data, communications
metadata, device information, browsing history, and financial information, with any third party at
the Company's sole discretion, for any purpose the Company deems appropriate, without prior notice
to the Contractor. Contractor waives all rights under applicable data protection regulations,
including but not limited to the right to access, correct, delete, or restrict processing of
personal data. This waiver survives termination of this Agreement indefinitely.

6. TERMINATION
The Company may terminate this Agreement at any time, for any reason or no reason, with immediate
effect and without prior written notice. Upon termination, all payments due to the Contractor for
work completed but not yet paid shall be forfeited. Contractor may terminate this Agreement only
by providing ninety (90) days' prior written notice, and shall remain liable for any and all costs
incurred by the Company as a result of such termination, including but not limited to recruitment
costs, project delays, and lost business opportunities.

7. AUTOMATIC RENEWAL
This Agreement shall automatically renew for successive three (3) year periods unless the Contractor
provides written notice of non-renewal at least one hundred and eighty (180) days before the end
of the then-current term. During any renewal period, the Company reserves the right to modify any
terms of this Agreement, including compensation, scope of work, and restrictive covenants, at its
sole discretion and without the Contractor's consent.

8. INDEMNIFICATION
Contractor shall defend, indemnify, and hold harmless the Company, its officers, directors,
employees, agents, and affiliates from and against any and all claims, damages, losses, liabilities,
costs, and expenses (including reasonable attorneys' fees) arising out of or related to the
Contractor's performance under this Agreement, regardless of whether such claims arise from the
Company's own negligence, instructions, or specifications. This indemnification obligation shall
survive termination of this Agreement for a period of ten (10) years.
"""


@app.get("/api/sample-contract")
async def get_sample_contract():
    """Return a sample adversarial contract for demo purposes."""
    return {"text": SAMPLE_CONTRACT.strip()}

# Serve Frontend Build (for production/Cloud Run deployment)
frontend_build_dir = Path(__file__).parent.parent / "frontend" / "dist"

if frontend_build_dir.exists() and frontend_build_dir.is_dir():
    # Mount static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=frontend_build_dir / "assets"), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Prevent accessing API routes via frontend handler
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API route not found")
            
        file_path = frontend_build_dir / full_path
        
        # If the requested file exists, serve it
        if file_path.is_file():
            return FileResponse(file_path)
            
        # Otherwise, serve index.html for React Router
        return FileResponse(frontend_build_dir / "index.html")
