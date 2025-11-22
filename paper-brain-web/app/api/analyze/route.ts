import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { fileId, filePath } = await request.json();

    if (!fileId) {
      return NextResponse.json(
        { error: 'File ID required' },
        { status: 400 }
      );
    }

    // TODO: Call Python pipeline API or run pipeline directly
    // For now, return mock analysis results
    const mockResults = {
      id: fileId,
      extracted_fields: {
        VENDOR: 'Sample Vendor Name',
        DATE: '12-Aug-25',
        TOTAL: '15,000.00'
      },
      anomaly: {
        score: 0.15,
        is_anomaly: false,
        recon_error: 0.002,
        threshold: 0.05
      },
      tokens: ['Sample', 'tokens', 'from', 'OCR'],
      tags: ['O', 'B-VENDOR', 'I-VENDOR', 'O'],
      timestamp: new Date().toISOString()
    };

    return NextResponse.json(mockResults);
  } catch (error) {
    console.error('Analysis error:', error);
    return NextResponse.json(
      { error: 'Failed to analyze invoice' },
      { status: 500 }
    );
  }
}

