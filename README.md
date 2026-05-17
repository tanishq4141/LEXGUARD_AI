# ⚖️ LEXGUARD AI
**The AI-Powered Contract Intelligence Pipeline**

LEXGUARD AI is an advanced, multi-agent contract analysis platform designed to protect individuals and businesses from predatory contract terms. It moves beyond simple "summarization" by employing a custom **Adversarial Multi-Agent Debate Architecture (AMADA)** to analyze contracts strictly from your perspective.

![LEXGUARD AI](frontend/src/assets/hero.png) *(Note: Add hero image if available)*

---

## 🧠 The AMADA Protocol
LEXGUARD AI doesn't rely on a single AI prompt to determine risk. Instead, it simulates a legal courtroom in the background.

For every single clause extracted from your uploaded contract, the system spins up four independent agents:

1. **The Extractor**: Parses the raw document and classifies all legally binding clauses (e.g., Data Privacy, Arbitration, Auto-Renewal).
2. **The Benchmarker**: Compares the clause against standard industry baselines (via Common Paper).
3. **The Debate Agents**:
   - 🛡️ **Vendor Counsel**: An aggressive AI agent instructed to vigorously *defend* the clause and explain why it is standard business practice.
   - ⚔️ **Consumer Advocate**: A zealous AI agent instructed to relentlessly *attack* the clause and expose how it harms the recipient.
4. **The Arbitrator**: A final judge agent that reviews the debate transcripts, the benchmark data, and **your specific background context** to calculate a final Risk Score (0-100) and generate a personalized consequence simulation.

## 🚀 Key Features
* **Role-Based Risk Inversion**: The AI knows if you are the *Drafter* or the *Recipient*. A clause that aggressively protects the drafter is flagged as "CRITICAL RISK" for the recipient, but "LOW RISK" for the drafter.
* **Hyper-Personalization**: Provide your own background context (e.g., "I am a freelance designer") and the Arbitrator will weave it into visceral, real-world "Worst-Case Scenario" simulations.
* **Multi-Provider Support**: Choose between high-accuracy models (Google Gemini 3.1 Pro) or blazing-fast open-source models (Groq Llama 4 Scout 17B, Qwen 3 32B).
* **Token Telemetry**: Built-in tracking shows you exactly how many tokens the AI debate consumed per contract.

---

## 🛠️ Tech Stack
* **Frontend**: React + TypeScript + Vite + CSS (Custom Glassmorphism UI)
* **Backend**: FastAPI + Python 3.13 + `asyncio`
* **AI Providers**: Google Generative AI SDK (`gemini-3.1-pro-preview`), Groq API (`llama-4-scout-17b`, `qwen3-32b`)

---

## ⚙️ Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/tanishq4141/LEXGUARD_AI.git
cd LEXGUARD_AI
```

### 2. Backend Setup
```bash
cd backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API Keys
cp .env.example .env
```
Open `.env` and add your API keys:
- `GEMINI_API_KEY`: Get from [Google AI Studio](https://aistudio.google.com/)
- `GROQ_API_KEY`: Get from [Groq Console](https://console.groq.com/)

**Start the Backend Server:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Setup
Open a new terminal window:
```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

Navigate to `http://localhost:5173` in your browser.

---

## 📝 Usage Guide
1. Open the web interface.
2. Select your **AI Model** (e.g., Llama 4 Scout 17B for fast, parallel multi-agent debate).
3. Set your **Document Type** (e.g., Commercial Terms).
4. Select your **Role** (Are you receiving this contract, or did you draft it?).
5. Enter your **Background Context** (The more specific you are, the better the consequence simulations will be).
6. Upload a PDF/DOCX or Paste your contract text.
7. Review the generated Risk Score, Plain Language Summaries, and the raw Debate Transcripts between the AI agents!

---

## ⚠️ Important Note on API Limits
Because the AMADA protocol runs multiple agents concurrently for *every single clause*, it consumes tokens very rapidly. 
- Using Groq's `llama-3.3-70b-versatile` on the Free Tier is not recommended for large contracts, as it hits the 12,000 TPM (Tokens Per Minute) limit almost instantly.
- **Recommended**: Use `meta-llama/llama-4-scout-17b-16e-instruct` (30K TPM limit) or `gemini-3.1-pro-preview` for the best balance of context window and rate limits.

---

## 🏆 Hackathon Evaluation Criteria

LEXGUARD AI was architected from the ground up to meet the following evaluation criteria:

1. **Code Quality**: The Python backend uses strict typing (Pydantic models) and comprehensive Google-style docstrings. The frontend is built with React + TypeScript, ensuring type safety across the entire stack.
2. **Security**: We utilize `CORSMiddleware` to prevent cross-origin attacks, enforce strict 10MB payload size limits on the `/api/analyze` endpoint, sanitize all API error responses so internal stack traces never leak to the frontend, and rigorously protect against prompt injection via our `agents/guard.py` layer.
3. **Efficiency**: The AMADA protocol utilizes `asyncio.Semaphore` and fully asynchronous HTTP calls to process multiple AI agents concurrently. This turns a complex, multi-stage debate into a lightning-fast pipeline that aggressively maximizes throughput while respecting rate limits.
4. **Testing**: The backend features a robust `pytest` suite testing API endpoints and mocking asynchronous LLM agent pipelines to ensure deterministic CI/CD behavior.
5. **Accessibility**: The frontend UI is fully equipped with ARIA roles (`role="meter"`, `aria-valuenow`), keyboard-navigable tabs (`tabIndex={0}`), and semantic ARIA labels for screen readers, ensuring the glassmorphism design is accessible to all users.
6. **Google Services**: The entire backend intelligence is powered by Google's Generative AI SDK using the cutting-edge `gemini-3.1-pro-preview` model. The full-stack application is containerized into a single-container architecture and deployed on **Google Cloud Run** using Google Cloud Build for continuous deployment.

---
*Disclaimer: LEXGUARD AI is an experimental AI tool. It does not provide certified legal advice. Always consult a qualified attorney for legally binding decisions.*
