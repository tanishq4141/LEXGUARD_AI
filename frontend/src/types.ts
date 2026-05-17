/* LEXGUARD AI — TypeScript Types */

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type ClauseCategory =
  | 'DATA_PRIVACY'
  | 'ARBITRATION'
  | 'IP_TRANSFER'
  | 'INDEMNIFICATION'
  | 'LIMITATION_OF_LIABILITY'
  | 'NON_COMPETE'
  | 'TERMINATION'
  | 'AUTO_RENEWAL'
  | 'CONFIDENTIALITY'
  | 'GOVERNING_LAW'
  | 'FORCE_MAJEURE'
  | 'PAYMENT_TERMS'
  | 'WARRANTY'
  | 'ASSIGNMENT'
  | 'SEVERABILITY'
  | 'OTHER';

export interface RiskAssessment {
  clause_id: string;
  clause_category: ClauseCategory;
  section_title: string | null;
  raw_text: string;
  risk_score: number;
  risk_level: RiskLevel;
  plain_language_summary: string;
  consequence_simulation: string;
  benchmark_deviation: boolean;
  deviation_rationale: string;
  vendor_argument: string;
  consumer_argument: string;
}

export interface TokenUsage {
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  api_calls: number;
}

export interface AnalysisResult {
  document_title: string;
  overall_risk_score: number;
  overall_risk_level: RiskLevel;
  total_clauses_analyzed: number;
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
  executive_summary: string;
  clauses: RiskAssessment[];
  token_usage: TokenUsage;
}

export const CATEGORY_LABELS: Record<ClauseCategory, string> = {
  DATA_PRIVACY: 'Data Privacy',
  ARBITRATION: 'Arbitration',
  IP_TRANSFER: 'IP Transfer',
  INDEMNIFICATION: 'Indemnification',
  LIMITATION_OF_LIABILITY: 'Liability Limitation',
  NON_COMPETE: 'Non-Compete',
  TERMINATION: 'Termination',
  AUTO_RENEWAL: 'Auto Renewal',
  CONFIDENTIALITY: 'Confidentiality',
  GOVERNING_LAW: 'Governing Law',
  FORCE_MAJEURE: 'Force Majeure',
  PAYMENT_TERMS: 'Payment Terms',
  WARRANTY: 'Warranty',
  ASSIGNMENT: 'Assignment',
  SEVERABILITY: 'Severability',
  OTHER: 'Other',
};

export const CATEGORY_ICONS: Record<ClauseCategory, string> = {
  DATA_PRIVACY: '🔐',
  ARBITRATION: '⚖️',
  IP_TRANSFER: '💡',
  INDEMNIFICATION: '🛡️',
  LIMITATION_OF_LIABILITY: '📊',
  NON_COMPETE: '🚫',
  TERMINATION: '🔚',
  AUTO_RENEWAL: '🔄',
  CONFIDENTIALITY: '🤫',
  GOVERNING_LAW: '🏛️',
  FORCE_MAJEURE: '🌪️',
  PAYMENT_TERMS: '💰',
  WARRANTY: '✅',
  ASSIGNMENT: '📋',
  SEVERABILITY: '✂️',
  OTHER: '📄',
};
