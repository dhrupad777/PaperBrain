# Paper Brain Web

Next.js frontend for the Paper Brain ANN invoice intelligence system.

## Structure

```
paper-brain-web/
├── app/
│   ├── page.tsx              # Dashboard (main page)
│   ├── upload/page.tsx      # Upload screen
│   ├── results/[id]/page.tsx # Results viewer
│   └── api/
│       ├── upload/route.ts   # File upload API
│       ├── analyze/route.ts   # Analysis API
│       └── history/route.ts   # History API
├── components/
│   ├── UploadDropzone.tsx     # File upload component
│   ├── ResultCards.tsx       # Results display
│   ├── PdfViewer.tsx         # Document preview
│   └── ForecastChart.tsx     # Forecasting visualization
├── lib/
│   ├── types.ts              # TypeScript types
│   ├── fetcher.ts            # API client helpers
│   └── gcs.ts                # GCS client (future)
└── public/
    └── sample-invoices/      # Sample files
```

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env.local` (optional):
```env
NEXT_PUBLIC_API_URL=/api
# Add GCS config when ready
```

3. Run development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000)

## Features

- **Dashboard**: Overview of processed invoices
- **Upload**: Drag-and-drop invoice upload
- **Results**: View extracted fields, anomaly detection, and OCR results
- **History**: Browse past analyses

## API Routes

All API routes are in `app/api/`:
- `POST /api/upload` - Upload invoice file
- `POST /api/analyze` - Analyze invoice (calls Python pipeline)
- `GET /api/history` - Get analysis history

## Next Steps

1. Connect API routes to Python pipeline backend
2. Implement file storage (local/GCS)
3. Add authentication
4. Enhance UI/UX
5. Add forecasting visualization
