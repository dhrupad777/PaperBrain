'use client';

import { useState } from 'react';
import UploadDropzone from '@/components/UploadDropzone';
import ResultCards from '@/components/ResultCards';

export default function Page() {
  const [data, setData] = useState<any>(null);

  return (
    <main className="min-h-screen bg-white text-slate-900 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold">Paper Brain — Invoice Intelligence</h1>
        <p className="text-sm text-slate-700 mt-1">
          Upload an invoice to extract fields, detect anomalies, and forecast spend.
        </p>

        <div className="mt-6">
          <UploadDropzone onDone={setData} />
        </div>

        {data?.result && <ResultCards result={data.result} />}

        {data?.result?.ocr_text && (
          <section className="mt-6 rounded-xl bg-white p-4 border border-slate-200 shadow">
            <h2 className="font-semibold mb-2 text-slate-900">OCR Debug</h2>
            <pre className="text-xs whitespace-pre-wrap max-h-64 overflow-auto text-slate-700 bg-slate-50 p-3 rounded border">
              {data.result.ocr_text}
            </pre>
          </section>
        )}
      </div>
    </main>
  );
}
