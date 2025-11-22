'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import UploadDropzone from '@/components/UploadDropzone';

export default function UploadPage() {
  const router = useRouter();
  const [uploading, setUploading] = useState(false);

  const handleUpload = async (file: File) => {
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const uploadRes = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!uploadRes.ok) {
        throw new Error('Upload failed');
      }

      const { id } = await uploadRes.json();

      // Trigger analysis
      const analyzeRes = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fileId: id }),
      });

      if (!analyzeRes.ok) {
        throw new Error('Analysis failed');
      }

      const result = await analyzeRes.json();

      // Navigate to results page
      router.push(`/results/${id}`);
    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to upload and analyze invoice');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Upload Invoice</h1>
      <UploadDropzone onUpload={handleUpload} uploading={uploading} />
    </div>
  );
}

