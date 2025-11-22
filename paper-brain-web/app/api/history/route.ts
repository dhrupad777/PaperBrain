import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const limit = parseInt(searchParams.get('limit') || '10');
    const offset = parseInt(searchParams.get('offset') || '0');

    // TODO: Fetch from database/storage
    // For now, return mock history
    const mockHistory = Array.from({ length: limit }, (_, i) => ({
      id: `inv_${Date.now() - i * 1000}`,
      filename: `invoice_${i + 1}.png`,
      uploaded_at: new Date(Date.now() - i * 1000).toISOString(),
      status: i % 3 === 0 ? 'processing' : 'completed',
      extracted_fields: {
        VENDOR: `Vendor ${i + 1}`,
        DATE: '12-Aug-25',
        TOTAL: `${(i + 1) * 1000}.00`
      }
    }));

    return NextResponse.json({
      items: mockHistory,
      total: 100, // Mock total
      limit,
      offset
    });
  } catch (error) {
    console.error('History fetch error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch history' },
      { status: 500 }
    );
  }
}

