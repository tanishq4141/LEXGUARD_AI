/* LEXGUARD AI — DebateTrace Component
   Two-column adversarial debate transcript viewer */

import type { RiskAssessment } from '../types';
import { CATEGORY_LABELS, CATEGORY_ICONS } from '../types';
import './DebateTrace.css';

interface DebateTraceProps {
  clause: RiskAssessment;
}

export default function DebateTrace({ clause }: DebateTraceProps) {
  return (
    <div className="debate-trace animate-fade-in" id="debate-trace-panel">
      {/* Clause Header */}
      <div className="dt-header">
        <div className="dt-header-left">
          <span className="dt-icon">{CATEGORY_ICONS[clause.clause_category]}</span>
          <div>
            <h3 className="dt-title">{CATEGORY_LABELS[clause.clause_category]}</h3>
            {clause.section_title && (
              <span className="dt-section">{clause.section_title}</span>
            )}
          </div>
        </div>
        <div className="dt-score-badge" data-level={clause.risk_level.toLowerCase()}>
          <span className="dt-score-num">{clause.risk_score}</span>
          <span className="dt-score-label">{clause.risk_level}</span>
        </div>
      </div>

      {/* Original vs Plain Language */}
      <div className="dt-comparison">
        <div className="dt-comp-col">
          <div className="dt-comp-label">📜 Original Legal Text</div>
          <div className="dt-comp-content dt-original">
            {clause.raw_text}
          </div>
        </div>
        <div className="dt-comp-col">
          <div className="dt-comp-label">💬 Plain Language</div>
          <div className="dt-comp-content dt-plain">
            {clause.plain_language_summary}
          </div>
        </div>
      </div>

      {/* Consequence Simulation */}
      <div className="dt-consequence">
        <div className="dt-consequence-header">
          <span>🎯</span>
          <span>Consequence Simulation</span>
        </div>
        <p className="dt-consequence-text">{clause.consequence_simulation}</p>
      </div>

      {/* Benchmark Status */}
      {clause.benchmark_deviation && (
        <div className="dt-benchmark-alert">
          <div className="dt-benchmark-header">
            <span>📏</span>
            <span>Common Paper Benchmark Deviation</span>
          </div>
          <p className="dt-benchmark-text">{clause.deviation_rationale}</p>
        </div>
      )}

      {/* Adversarial Debate */}
      <div className="dt-debate-section">
        <h4 className="dt-debate-title">⚔️ AI Reasoning Trace — Adversarial Debate</h4>
        <div className="dt-debate-grid">
          <div className="dt-debate-col dt-vendor">
            <div className="dt-debate-label">
              <span className="dt-persona-dot dt-persona-vendor" />
              Vendor Counsel Defense
            </div>
            <div className="dt-debate-content">
              {clause.vendor_argument}
            </div>
          </div>
          <div className="dt-debate-divider" />
          <div className="dt-debate-col dt-consumer">
            <div className="dt-debate-label">
              <span className="dt-persona-dot dt-persona-consumer" />
              Consumer Advocate Attack
            </div>
            <div className="dt-debate-content">
              {clause.consumer_argument}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
