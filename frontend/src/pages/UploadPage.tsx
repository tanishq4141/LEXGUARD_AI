/* LEXGUARD AI — Upload Page
   Premium drag-and-drop upload zone with text paste option */

import { useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, Sparkles, Shield, Zap, BookOpen } from 'lucide-react';
import { analyzeText, uploadFile, getSampleContract } from '../api';
import type { AnalysisResult } from '../types';
import './UploadPage.css';

interface UploadPageProps {
  onAnalysisComplete: (result: AnalysisResult) => void;
}

const ANALYSIS_STEPS = [
  '🔐 Scanning for prompt injection threats...',
  '📄 Extracting contract clauses...',
  '📏 Benchmarking against Common Paper standards...',
  '⚔️ Running adversarial debate protocol...',
  '⚖️ Arbitrator synthesizing risk assessment...',
  '📊 Generating consequence simulations...',
];

export default function UploadPage({ onAnalysisComplete }: UploadPageProps) {
  const [selectedModel, setSelectedModel] = useState('gemini-3.1-pro-preview');
  const [userRole, setUserRole] = useState('recipient');
  const [contractType, setContractType] = useState('Commercial Terms');
  const [userContext, setUserContext] = useState('');
  const [textInput, setTextInput] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const runAnalysis = useCallback(async (analysisFn: () => Promise<AnalysisResult>) => {
    setIsAnalyzing(true);
    setError(null);
    setCurrentStep(0);

    // Simulate step progression
    const stepInterval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev < ANALYSIS_STEPS.length - 1) return prev + 1;
        return prev;
      });
    }, 3000);

    try {
      const result = await analysisFn();
      clearInterval(stepInterval);
      onAnalysisComplete(result);
      navigate('/analysis');
    } catch (err) {
      clearInterval(stepInterval);
      setError(err instanceof Error ? err.message : 'Analysis failed. Please try again.');
      setIsAnalyzing(false);
    }
  }, [navigate, onAnalysisComplete]);

  const handleTextAnalysis = useCallback(() => {
    if (!textInput.trim()) return;
    runAnalysis(() => analyzeText(textInput, selectedModel, userContext, userRole, contractType));
  }, [textInput, selectedModel, userContext, userRole, contractType, runAnalysis]);

  const handleFileUpload = useCallback((file: File) => {
    runAnalysis(() => uploadFile(file, selectedModel, userContext, userRole, contractType));
  }, [selectedModel, userContext, userRole, contractType, runAnalysis]);

  const handleFileDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFileUpload(file);
  }, [handleFileUpload]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFileUpload(file);
  }, [handleFileUpload]);

  const loadSampleContract = useCallback(async () => {
    try {
      const text = await getSampleContract();
      setTextInput(text);
    } catch {
      setError('Failed to load sample contract. Is the backend running?');
    }
  }, []);

  // Loading overlay
  if (isAnalyzing) {
    return (
      <div className="loading-overlay">
        <div className="loading-spinner" />
        <div className="loading-text">
          Analyzing your contract with AMADA Protocol
        </div>
        <div className="loading-step" key={currentStep}>
          {ANALYSIS_STEPS[currentStep]}
        </div>
        <div className="loading-progress-bar">
          <div
            className="loading-progress-fill"
            style={{ width: `${((currentStep + 1) / ANALYSIS_STEPS.length) * 100}%` }}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="upload-page">
      {/* Hero Section */}
      <section className="upload-hero">
        <div className="hero-badge animate-fade-in">
          <Sparkles size={14} />
          <span>AI-Powered Contract Intelligence</span>
        </div>
        <h1 className="hero-title animate-fade-in">
          Decode any contract<br />
          <span className="hero-gradient">before you sign.</span>
        </h1>
        <p className="hero-subtitle animate-fade-in">
          LEXGUARD AI uses adversarial multi-agent debate to surface hidden risks,
          benchmark against industry standards, and simulate real-world consequences
          — all in seconds.
        </p>

        {/* Feature pills */}
        <div className="hero-features animate-fade-in">
          <div className="feature-pill">
            <Shield size={16} />
            <span>AMADA Protocol</span>
          </div>
          <div className="feature-pill">
            <Zap size={16} />
            <span>Common Paper Benchmarks</span>
          </div>
          <div className="feature-pill">
            <BookOpen size={16} />
            <span>Consequence Simulation</span>
          </div>
        </div>
      </section>

      {/* Upload Area */}
      <section className="upload-area container animate-fade-in-up">
        {/* Personalization Configuration */}
        <div className="config-panel glass-card">
          <div className="config-header">
            <h3>⚙️ Analysis Configuration</h3>
            <div className="model-selector">
              <label htmlFor="model-select">AI Model:</label>
              <select 
                id="model-select" 
                value={selectedModel} 
                onChange={(e) => setSelectedModel(e.target.value)}
                className="config-dropdown"
              >
                <optgroup label="Google Gemini">
                  <option value="gemini-3.1-pro-preview">Gemini 3.1 Pro</option>
                  <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
                </optgroup>
                <optgroup label="Groq (Fast Open Source)">
                  <option value="llama-3.3-70b-versatile">Llama 3.3 70B (High Accuracy)</option>
                  <option value="meta-llama/llama-4-scout-17b-16e-instruct">Llama 4 Scout 17B (Balanced / Parallel)</option>
                  <option value="qwen/qwen3-32b">Qwen 3 32B (Strong Reasoning)</option>
                  <option value="llama-3.1-8b-instant">Llama 3.1 8B (High Speed)</option>
                </optgroup>
              </select>
            </div>
          </div>
          
          <div className="config-grid">
            <div className="config-field">
              <label htmlFor="contract-type">Document Type</label>
              <select 
                id="contract-type"
                value={contractType}
                onChange={(e) => setContractType(e.target.value)}
                className="config-dropdown"
              >
                <option value="Commercial Terms">Commercial Terms / Vendor Agmt</option>
                <option value="Non-Disclosure Agreement">Non-Disclosure Agreement (NDA)</option>
                <option value="Employment Contract">Employment Contract</option>
                <option value="Constitution/Bylaws">Constitution / Bylaws</option>
                <option value="Real Estate/Lease">Real Estate / Lease</option>
                <option value="Privacy Policy/TOS">Privacy Policy / TOS</option>
                <option value="General Legal Contract">General Legal Contract</option>
              </select>
            </div>

            <div className="config-field">
              <label>My Role in this Contract</label>
              <div className="role-toggle" role="group" aria-label="Select your role in the contract">
                <button 
                  className={`role-btn ${userRole === 'recipient' ? 'active' : ''}`}
                  onClick={() => setUserRole('recipient')}
                  aria-pressed={userRole === 'recipient'}
                  aria-label="I am the recipient of this contract"
                >
                  For Me (Recipient)
                </button>
                <button 
                  className={`role-btn ${userRole === 'drafter' ? 'active' : ''}`}
                  onClick={() => setUserRole('drafter')}
                  aria-pressed={userRole === 'drafter'}
                  aria-label="I am the drafter of this contract"
                >
                  From Me (Drafter)
                </button>
              </div>
            </div>
          </div>

          <div className="config-field full-width">
            <label htmlFor="user-context">My Information (Optional Context)</label>
            <textarea
              id="user-context"
              placeholder="E.g., I am a freelance designer... / We are a Series A startup..."
              value={userContext}
              onChange={(e) => setUserContext(e.target.value)}
              className="context-textarea"
              rows={2}
            />
          </div>
        </div>

        {/* Drag & Drop Zone */}
        <div
          className={`drop-zone glass-card ${isDragging ? 'drop-zone-active' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleFileDrop}
          onClick={() => fileInputRef.current?.click()}
          id="file-drop-zone"
          role="button"
          tabIndex={0}
          aria-label="Drop your contract here or click to browse files"
          onKeyDown={(e) => { if(e.key === 'Enter' || e.key === ' ') fileInputRef.current?.click(); }}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt"
            style={{ display: 'none' }}
            onChange={handleFileSelect}
            id="file-input"
          />
          <div className="drop-zone-icon">
            <Upload size={32} />
          </div>
          <h3>Drop your contract here</h3>
          <p>or click to browse · PDF, DOCX, TXT</p>
        </div>

        <div className="upload-divider">
          <span>or paste text below</span>
        </div>

        {/* Text Input */}
        <div className="text-input-area glass-card">
          <textarea
            className="text-input"
            placeholder="Paste your contract text here..."
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            rows={12}
            id="text-input"
          />
          <div className="text-input-footer">
            <button
              className="btn btn-ghost"
              onClick={loadSampleContract}
              id="load-sample-btn"
            >
              <FileText size={16} />
              Load Sample Contract
            </button>
            <div className="text-input-actions">
              {textInput && (
                <span className="char-count">
                  {textInput.length.toLocaleString()} chars
                </span>
              )}
              <button
                className="btn btn-primary"
                disabled={!textInput.trim()}
                onClick={handleTextAnalysis}
                id="analyze-btn"
              >
                <Sparkles size={16} />
                Analyze Contract
              </button>
            </div>
          </div>
        </div>

        {error && (
          <div className="upload-error animate-fade-in" id="upload-error">
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        )}
      </section>
    </div>
  );
}
