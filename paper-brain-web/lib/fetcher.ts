import { InvoiceAnalysis, HistoryResponse } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api';

export async function uploadFile(file: File): Promise<{ id: string; filename: string }> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    throw new Error('Upload failed');
  }

  return res.json();
}

export async function analyzeInvoice(fileId: string): Promise<InvoiceAnalysis> {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ fileId }),
  });

  if (!res.ok) {
    throw new Error('Analysis failed');
  }

  return res.json();
}

export async function getHistory(
  limit = 10,
  offset = 0
): Promise<HistoryResponse> {
  const res = await fetch(
    `${API_BASE}/history?limit=${limit}&offset=${offset}`
  );

  if (!res.ok) {
    throw new Error('Failed to fetch history');
  }

  return res.json();
}

