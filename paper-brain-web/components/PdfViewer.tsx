'use client';

import { useState, useEffect } from 'react';

interface PdfViewerProps {
  fileId: string;
}

export default function PdfViewer({ fileId }: PdfViewerProps) {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // TODO: Fetch actual file URL from storage
    // For now, use a placeholder or mock image
    setLoading(false);
    // setImageUrl(`/api/files/${fileId}`);
  }, [fileId]);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="text-center">Loading document...</div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4">Document Preview</h2>
      <div className="border rounded-lg p-4 bg-gray-50 min-h-[400px] flex items-center justify-center">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt="Invoice preview"
            className="max-w-full max-h-[600px] object-contain"
          />
        ) : (
          <div className="text-gray-400 text-center">
            <p>Document preview will appear here</p>
            <p className="text-sm mt-2">File ID: {fileId}</p>
          </div>
        )}
      </div>
    </div>
  );
}

