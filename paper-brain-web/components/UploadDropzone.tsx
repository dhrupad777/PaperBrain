'use client';

import { useState } from 'react';

export default function UploadDropzone({ onDone }: { onDone: (data: any) => void }) {
  const [loading, setLoading] = useState(false);

  async function handleFile(f: File) {
    setLoading(true);
    const form = new FormData();
    form.append('file', f);

    try {
      const r = await fetch('/api/upload', { method: 'POST', body: form });
      const data = await r.json();
      setLoading(false);
      onDone(data);
    } catch (error) {
      console.error('Upload error:', error);
      setLoading(false);
      onDone({ error: 'Upload failed' });
    }
  }

  return (
    <div className="border-2 border-dashed border-slate-300 rounded-xl p-8 text-center bg-slate-50">
      <input
        type="file"
        accept="image/*,application/pdf"
        onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
        className="hidden"
        id="fileInput"
      />
      <label htmlFor="fileInput" className="cursor-pointer">
        <div className="text-lg font-semibold text-slate-900">Upload Invoice</div>
        <div className="text-sm text-slate-700 mt-1">PNG/JPG/PDF supported</div>
      </label>
      {loading && <div className="mt-4 text-sm text-slate-700">Analyzing…</div>}
    </div>
  );
}

