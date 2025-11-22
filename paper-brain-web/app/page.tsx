'use client';

import { useState } from 'react';
import UploadDropzone from '@/components/UploadDropzone';
import ResultCards from '@/components/ResultCards';

export default function Page() {
  const [data, setData] = useState<any>(null);

  return (
    <main className="min-h-screen bg-slate-50 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold">Paper Brain — Invoice Intelligence</h1>
        <p className="text-sm opacity-70 mt-1">
          Upload an invoice to extract fields, detect anomalies, and forecast spend.
        </p>

        <div className="mt-6">
          <UploadDropzone onDone={setData} />
        </div>

        {data?.result && <ResultCards result={data.result} />}
      </div>
    </main>
  );
}
