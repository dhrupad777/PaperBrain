export default function ResultCards({ result }: { result: any }) {
  if (!result) return null;

  const fields = result.extracted_fields || {};
  const anomaly = result.anomaly || {};
  const forecast = result.forecast_next_total;

  return (
    <div className="grid md:grid-cols-3 gap-4 mt-6">
      <div className="rounded-xl bg-slate-50 p-4 shadow border border-slate-200">
        <div className="font-semibold mb-2 text-slate-900">Extracted Fields</div>
        <pre className="text-xs whitespace-pre-wrap text-slate-700">
          {JSON.stringify(fields, null, 2)}
        </pre>
      </div>

      <div className="rounded-xl bg-slate-50 p-4 shadow border border-slate-200">
        <div className="font-semibold mb-2 text-slate-900">Anomaly Detection</div>
        <div className="text-sm text-slate-700">Score: {anomaly.score?.toFixed?.(3) ?? 'n/a'}</div>
        <div className="text-sm text-slate-700">
          Flagged: {String(anomaly.is_anomaly ?? false)}
        </div>
        {anomaly.threshold && (
          <div className="text-xs text-slate-600 mt-2">
            Threshold: {anomaly.threshold.toFixed(4)}
          </div>
        )}
      </div>

      <div className="rounded-xl bg-slate-50 p-4 shadow border border-slate-200">
        <div className="font-semibold mb-2 text-slate-900">Forecast</div>
        <div className="text-sm text-slate-700">
          Next Expected Total: {forecast ?? 'n/a'}
        </div>
      </div>
    </div>
  );
}

