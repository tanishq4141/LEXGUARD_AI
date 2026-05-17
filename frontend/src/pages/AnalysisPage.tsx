/* LEXGUARD AI — Analysis Dashboard Page
   Master-detail view: gauge + clause table + detail panel */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  AlertTriangle,
  ShieldCheck,
  TrendingUp,
  ChevronDown,
  ChevronUp,
  Download,
} from 'lucide-react';
import type { AnalysisResult, RiskAssessment } from '../types';
import RiskGauge from '../components/RiskGauge';
import ClauseTable from '../components/ClauseTable';
import DebateTrace from '../components/DebateTrace';
import './AnalysisPage.css';

interface AnalysisPageProps {
  result: AnalysisResult | null;
}

export default function AnalysisPage({ result }: AnalysisPageProps) {
  const [selectedClause, setSelectedClause] = useState<RiskAssessment | null>(null);
  const [showDetails, setShowDetails] = useState(true);
  const navigate = useNavigate();

  if (!result) {
    return (
      <div className="analysis-empty container">
        <h2>No analysis results</h2>
        <p>Upload a contract to get started.</p>
        <button className="btn btn-primary" onClick={() => navigate('/')}>
          <ArrowLeft size={16} /> Go Back
        </button>
      </div>
    );
  }

  const handleExport = () => {
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'lexguard-analysis.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="analysis-page container">
      {/* Top bar */}
      <div className="analysis-topbar animate-fade-in">
        <button className="btn btn-ghost" onClick={() => navigate('/')}>
          <ArrowLeft size={16} />
          New Analysis
        </button>
        <button className="btn btn-secondary" onClick={handleExport} id="export-btn">
          <Download size={16} />
          Export JSON
        </button>
      </div>

      {/* Summary Cards Row */}
      <div className="analysis-summary animate-fade-in-up">
        {/* Gauge */}
        <div className="summary-gauge glass-card">
          <RiskGauge
            score={result.overall_risk_score}
            level={result.overall_risk_level}
            size={200}
          />
        </div>

        {/* Stats */}
        <div className="summary-stats">
          <div className="stat-card glass-card">
            <div className="stat-icon stat-icon-total">
              <ShieldCheck size={20} />
            </div>
            <div className="stat-content">
              <div className="stat-value">{result.total_clauses_analyzed}</div>
              <div className="stat-label">Clauses Analyzed</div>
            </div>
          </div>
          <div className="stat-card glass-card">
            <div className="stat-icon stat-icon-high">
              <AlertTriangle size={20} />
            </div>
            <div className="stat-content">
              <div className="stat-value" style={{ color: 'var(--risk-high)' }}>
                {result.high_risk_count}
              </div>
              <div className="stat-label">High/Critical Risk</div>
            </div>
          </div>
          <div className="stat-card glass-card">
            <div className="stat-icon stat-icon-medium">
              <TrendingUp size={20} />
            </div>
            <div className="stat-content">
              <div className="stat-value" style={{ color: 'var(--risk-medium)' }}>
                {result.medium_risk_count}
              </div>
              <div className="stat-label">Medium Risk</div>
            </div>
          </div>
        </div>
      </div>

      {/* Executive Summary */}
      <div className="exec-summary glass-card animate-fade-in-up" id="exec-summary">
        <h3>📋 Executive Summary</h3>
        <p>{result.executive_summary}</p>
      </div>

      {/* Token Usage */}
      {result.token_usage && (
        <div className="token-usage glass-card animate-fade-in-up" id="token-usage">
          <h4>🔢 AI Token Usage</h4>
          <div className="token-grid">
            <div className="token-item">
              <span className="token-label">Input Tokens</span>
              <span className="token-value token-input">{result.token_usage.input_tokens.toLocaleString()}</span>
            </div>
            <div className="token-item">
              <span className="token-label">Output Tokens</span>
              <span className="token-value token-output">{result.token_usage.output_tokens.toLocaleString()}</span>
            </div>
            <div className="token-item">
              <span className="token-label">Total Tokens</span>
              <span className="token-value token-total">{result.token_usage.total_tokens.toLocaleString()}</span>
            </div>
            <div className="token-item">
              <span className="token-label">API Calls</span>
              <span className="token-value token-calls">{result.token_usage.api_calls}</span>
            </div>
          </div>
        </div>
      )}

      {/* Clause Table */}
      <div className="clause-section animate-fade-in-up">
        <div className="section-header">
          <h3>Identified Clauses</h3>
          <span className="clause-count">{result.clauses.length} clauses</span>
        </div>
        <ClauseTable
          clauses={result.clauses}
          selectedId={selectedClause?.clause_id ?? null}
          onSelect={(clause) => {
            setSelectedClause(
              selectedClause?.clause_id === clause.clause_id ? null : clause
            );
            setShowDetails(true);
          }}
        />
      </div>

      {/* Detail Panel */}
      {selectedClause && (
        <div className="detail-section animate-fade-in-up" id="clause-detail-panel">
          <div className="section-header">
            <h3>Clause Deep Dive</h3>
            <button
              className="btn btn-ghost"
              onClick={() => setShowDetails(!showDetails)}
            >
              {showDetails ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
              {showDetails ? 'Collapse' : 'Expand'}
            </button>
          </div>
          {showDetails && <DebateTrace clause={selectedClause} />}
        </div>
      )}

      {/* Footer disclaimer */}
      <div className="analysis-footer">
        <p>
          ⚠️ LEXGUARD AI provides informational analysis only and does not constitute legal advice.
          Always consult a qualified attorney before signing any contract.
        </p>
      </div>
    </div>
  );
}
