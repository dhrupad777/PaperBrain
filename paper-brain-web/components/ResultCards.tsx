export default function ResultCards({ result }: { result: any }) {
  if (!result) return null;

  const fields = result.extracted_fields || {};
  const anomaly = result.anomaly || {};
  const forecast = result.forecast_next_total;

  return (
    <div className="grid md:grid-cols-3 gap-4 mt-6">
      <div className="rounded-xl bg-white p-4 shadow">
        <div className="font-semibold mb-2">Extracted Fields</div>
        <pre className="text-xs whitespace-pre-wrap">
          {JSON.stringify(fields, null, 2)}
        </pre>
      </div>

      <div className="rounded-xl bg-white p-4 shadow">
        <div className="font-semibold mb-2">Anomaly Detection</div>
        <div className="text-sm">Score: {anomaly.score?.toFixed?.(3) ?? 'n/a'}</div>
        <div className="text-sm">
          Flagged: {String(anomaly.is_anomaly ?? false)}
        </div>
        {anomaly.threshold && (
          <div className="text-xs opacity-70 mt-2">
            Threshold: {anomaly.threshold.toFixed(4)}
          </div>
        )}
      </div>

      <div className="rounded-xl bg-white p-4 shadow">
        <div className="font-semibold mb-2">Forecast</div>
        <div className="text-sm">
          Next Expected Total: {forecast ?? 'n/a'}
        </div>
      </div>
    </div>
  );
}

