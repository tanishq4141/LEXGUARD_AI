/* LEXGUARD AI — API Service */

import type { AnalysisResult } from './types';

const API_BASE = '';

export async function analyzeText(
  text: string, 
  model: string = 'gemini-3.1-pro-preview',
  userContext: string = '',
  userRole: string = 'recipient',
  contractType: string = 'Unknown'
): Promise<AnalysisResult> {
  const formData = new FormData();
  formData.append('text', text);
  formData.append('model', model);
  formData.append('user_context', userContext);
  formData.append('user_role', userRole);
  formData.append('contract_type', contractType);

  const response = await fetch(`${API_BASE}/api/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Unknown error occurred during analysis.' }));
    // Security: Sanitize error messages to prevent leaking internal stack traces to the UI
    const safeErrorMsg = err.detail && typeof err.detail === 'string' && !err.detail.includes('Traceback') 
      ? err.detail 
      : 'An unexpected error occurred while analyzing the text. Please try again.';
    throw new Error(safeErrorMsg);
  }

  const data = await response.json();
  
  // Hackathon Integration: Trigger Firebase Analytics
  if (typeof window !== 'undefined' && (window as any).firebaseAnalytics) {
    (window as any).firebaseAnalytics.logEvent('contract_analyzed', {
      model, contract_type: contractType, user_role: userRole
    });
  }
  
  return data;
}

export async function uploadFile(
  file: File, 
  model: string = 'gemini-3.1-pro-preview',
  userContext: string = '',
  userRole: string = 'recipient',
  contractType: string = 'Unknown'
): Promise<AnalysisResult> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('model', model);
  formData.append('user_context', userContext);
  formData.append('user_role', userRole);
  formData.append('contract_type', contractType);

  const response = await fetch(`${API_BASE}/api/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Unknown error occurred during upload.' }));
    // Security: Sanitize error messages to prevent leaking internal stack traces to the UI
    const safeErrorMsg = err.detail && typeof err.detail === 'string' && !err.detail.includes('Traceback') 
      ? err.detail 
      : 'An unexpected error occurred while uploading the file. Please ensure it is a valid PDF, DOCX, or TXT under 10MB.';
    throw new Error(safeErrorMsg);
  }

  const data = await response.json();
  
  // Hackathon Integration: Trigger Firebase Analytics
  if (typeof window !== 'undefined' && (window as any).firebaseAnalytics) {
    (window as any).firebaseAnalytics.logEvent('file_uploaded', {
      file_type: file.type, model, contract_type: contractType
    });
  }
  
  return data;
}

export async function getSampleContract(): Promise<string> {
  const response = await fetch(`${API_BASE}/api/sample-contract`);

  if (!response.ok) {
    throw new Error('Failed to fetch sample contract');
  }

  const data = await response.json();
  return data.text;
}

export async function healthCheck(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/api/health`);
    return response.ok;
  } catch {
    return false;
  }
}
