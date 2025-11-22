'use client';

import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import ResultCards from '@/components/ResultCards';
import PdfViewer from '@/components/PdfViewer';

interface AnalysisResult {
  id: string;
  extracted_fields: Record<string, string>;
  anomaly?: {
    score: number;
    is_anomaly: boolean;
    recon_error: number;
    threshold: number;
  };
  tokens?: string[];
  tags?: string[];
  timestamp?: string;
}

export default function ResultsPage() {
  const params = useParams();
  const id = params.id as string;
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchResult = async () => {
      try {
        const res = await fetch(`/api/analyze`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ fileId: id }),
        });

        if (!res.ok) {
          throw new Error('Failed to fetch results');
        }

        const data = await res.json();
        setResult(data);
      } catch (error) {
        console.error('Fetch error:', error);
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchResult();
    }
  }, [id]);

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">Loading results...</div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center text-red-500">Failed to load results</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Analysis Results</h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <ResultCards result={result} />
        </div>
        <div>
          <PdfViewer fileId={id} />
        </div>
      </div>
    </div>
  );
}

