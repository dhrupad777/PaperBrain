export interface InvoiceAnalysis {
  id: string;
  filename: string;
  uploaded_at: string;
  status: 'processing' | 'completed' | 'failed';
  extracted_fields: {
    VENDOR?: string;
    DATE?: string;
    TOTAL?: string;
    INVOICE_NO?: string;
  };
  anomaly?: {
    score: number;
    is_anomaly: boolean;
    recon_error: number;
    threshold: number;
  };
  tokens?: string[];
  tags?: string[];
}

export interface ForecastData {
  date: string;
  value: number;
}

export interface HistoryResponse {
  items: InvoiceAnalysis[];
  total: number;
  limit: number;
  offset: number;
}

