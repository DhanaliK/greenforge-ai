"use client";

interface Props {
  score: number;
  size?: number;
}

export default function ScoreGauge({ score, size = 120 }: Props) {
  const pct = Math.max(0, Math.min(100, score));
  const color =
    pct >= 80 ? "#22c55e" :
    pct >= 60 ? "#eab308" :
    pct >= 40 ? "#f97316" : "#ef4444";

  const r = (size - 16) / 2;
  const circ = 2 * Math.PI * r;
  const dash = (pct / 100) * circ;

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="#1f2937" strokeWidth={12} />
        <circle
          cx={size/2} cy={size/2} r={r} fill="none"
          stroke={color} strokeWidth={12}
          strokeDasharray={`${dash} ${circ}`}
          strokeLinecap="round"
          style={{ transition: "stroke-dasharray 0.8s ease" }}
        />
      </svg>
      <div className="text-center -mt-2">
        <div className="text-2xl font-bold" style={{ color }}>{Math.round(pct)}</div>
        <div className="text-xs text-gray-500">/ 100</div>
      </div>
    </div>
  );
}
