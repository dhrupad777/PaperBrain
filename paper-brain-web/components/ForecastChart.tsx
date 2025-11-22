'use client';

import { useEffect, useRef } from 'react';

interface ForecastChartProps {
  data: Array<{ date: string; value: number }>;
  forecast?: Array<{ date: string; value: number }>;
}

export default function ForecastChart({ data, forecast }: ForecastChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Simple line chart rendering
    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height);

    const allData = [...data, ...(forecast || [])];
    if (allData.length === 0) return;

    const values = allData.map(d => d.value);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const range = max - min || 1;

    const padding = 40;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;

    // Draw axes
    ctx.strokeStyle = '#e5e7eb';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();

    // Draw historical data
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 2;
    ctx.beginPath();
    data.forEach((point, idx) => {
      const x = padding + (idx / (allData.length - 1)) * chartWidth;
      const y = height - padding - ((point.value - min) / range) * chartHeight;
      if (idx === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.stroke();

    // Draw forecast data
    if (forecast && forecast.length > 0) {
      ctx.strokeStyle = '#ef4444';
      ctx.setLineDash([5, 5]);
      ctx.beginPath();
      const startIdx = data.length;
      allData.slice(startIdx).forEach((point, idx) => {
        const x = padding + ((startIdx + idx) / (allData.length - 1)) * chartWidth;
        const y = height - padding - ((point.value - min) / range) * chartHeight;
        if (idx === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      });
      ctx.stroke();
      ctx.setLineDash([]);
    }

    // Draw points
    data.forEach((point, idx) => {
      const x = padding + (idx / (allData.length - 1)) * chartWidth;
      const y = height - padding - ((point.value - min) / range) * chartHeight;
      ctx.fillStyle = '#3b82f6';
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, 2 * Math.PI);
      ctx.fill();
    });
  }, [data, forecast]);

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4">Forecast Chart</h2>
      <canvas
        ref={canvasRef}
        width={600}
        height={300}
        className="w-full border rounded"
      />
      <div className="mt-4 flex gap-4 justify-center">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-blue-500"></div>
          <span className="text-sm">Historical</span>
        </div>
        {forecast && (
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-red-500"></div>
            <span className="text-sm">Forecast</span>
          </div>
        )}
      </div>
    </div>
  );
}

