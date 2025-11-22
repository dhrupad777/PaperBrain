import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  const form = await req.formData();
  const file = form.get('file') as File;

  if (!file) {
    return NextResponse.json({ error: 'No file' }, { status: 400 });
  }

  // Forward to Python API
  const pyForm = new FormData();
  pyForm.append('file', file);

  try {
    const r = await fetch('http://localhost:8000/analyze', {
      method: 'POST',
      body: pyForm,
    });

    if (!r.ok) {
      const errorText = await r.text();
      console.error('Python API error:', errorText);
      return NextResponse.json(
        { error: 'Python API failed', details: errorText },
        { status: r.status }
      );
    }

    const data = await r.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Upload error:', error);
    return NextResponse.json(
      { error: 'Failed to connect to Python API', details: String(error) },
      { status: 500 }
    );
  }
}

