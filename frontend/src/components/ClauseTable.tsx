/* LEXGUARD AI — ClauseTable Component
   Sortable, interactive clause risk table with severity badges */

import type { RiskAssessment } from '../types';
import { CATEGORY_LABELS, CATEGORY_ICONS } from '../types';
import './ClauseTable.css';

interface ClauseTableProps {
  clauses: RiskAssessment[];
  selectedId: string | null;
  onSelect: (clause: RiskAssessment) => void;
}

export default function ClauseTable({ clauses, selectedId, onSelect }: ClauseTableProps) {
  return (
    <div className="clause-table-wrapper">
      <table className="clause-table" id="clause-risk-table">
        <thead>
          <tr>
            <th scope="col" style={{ width: 52 }}>Risk</th>
            <th scope="col">Category</th>
            <th scope="col">Summary</th>
            <th scope="col" style={{ width: 80 }}>Score</th>
            <th scope="col" style={{ width: 100 }}>Benchmark</th>
          </tr>
        </thead>
        <tbody className="stagger-children">
          {clauses.map((clause) => (
            <tr
              key={clause.clause_id}
              className={`clause-row ${selectedId === clause.clause_id ? 'selected' : ''}`}
              onClick={() => onSelect(clause)}
              onKeyDown={(e) => { if(e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSelect(clause); } }}
              id={`clause-${clause.clause_id}`}
              tabIndex={0}
              role="button"
              aria-label={`View details for ${CATEGORY_LABELS[clause.clause_category]} clause. Risk score ${clause.risk_score}.`}
              aria-expanded={selectedId === clause.clause_id}
            >
              <td>
                <div className={`risk-dot risk-dot-${clause.risk_level.toLowerCase()}`} />
              </td>
              <td>
                <div className="clause-category">
                  <span className="clause-icon">
                    {CATEGORY_ICONS[clause.clause_category]}
                  </span>
                  <span>{CATEGORY_LABELS[clause.clause_category]}</span>
                </div>
              </td>
              <td>
                <div className="clause-summary-cell">
                  {clause.plain_language_summary.slice(0, 100)}
                  {clause.plain_language_summary.length > 100 ? '…' : ''}
                </div>
              </td>
              <td>
                <div className="score-cell">
                  <span
                    className="score-value"
                    style={{ color: getScoreColor(clause.risk_score) }}
                  >
                    {clause.risk_score}
                  </span>
                  <span className="score-max">/100</span>
                </div>
              </td>
              <td>
                {clause.benchmark_deviation ? (
                  <span className="badge badge-high" style={{ fontSize: '0.6875rem' }}>
                    ⚠ Deviates
                  </span>
                ) : (
                  <span className="badge badge-low" style={{ fontSize: '0.6875rem' }}>
                    ✓ Standard
                  </span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function getScoreColor(score: number): string {
  if (score <= 20) return 'var(--risk-low)';
  if (score <= 45) return 'var(--risk-medium)';
  if (score <= 70) return 'var(--risk-high)';
  return 'var(--risk-critical)';
}
