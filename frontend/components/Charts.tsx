"use client";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, LineChart, Line, RadarChart, Radar,
  PolarGrid, PolarAngleAxis, PolarRadiusAxis
} from "recharts";

export function BenchmarkBar({ before, after }: { before: number; after: number }) {
  const data = [
    { name: "Runtime (s)", Before: before, After: after },
  ];
  return (
    <ResponsiveContainer width="100%" height={160}>
      <BarChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
        <XAxis dataKey="name" tick={{ fill: "#9ca3af", fontSize: 12 }} />
        <YAxis tick={{ fill: "#9ca3af", fontSize: 12 }} />
        <Tooltip
          contentStyle={{ background: "#111827", border: "1px solid #374151", borderRadius: 8 }}
          labelStyle={{ color: "#f3f4f6" }}
        />
        <Bar dataKey="Before" fill="#ef4444" radius={[4,4,0,0]} />
        <Bar dataKey="After"  fill="#22c55e" radius={[4,4,0,0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function MemoryBar({ before, after }: { before: number; after: number }) {
  const data = [{ name: "Memory (MB)", Before: before, After: after }];
  return (
    <ResponsiveContainer width="100%" height={160}>
      <BarChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
        <XAxis dataKey="name" tick={{ fill: "#9ca3af", fontSize: 12 }} />
        <YAxis tick={{ fill: "#9ca3af", fontSize: 12 }} />
        <Tooltip
          contentStyle={{ background: "#111827", border: "1px solid #374151", borderRadius: 8 }}
        />
        <Bar dataKey="Before" fill="#f97316" radius={[4,4,0,0]} />
        <Bar dataKey="After"  fill="#3b82f6" radius={[4,4,0,0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function ScoreRadar({ breakdown }: { breakdown: Record<string, number> }) {
  const data = Object.entries(breakdown)
    .filter(([k]) => k !== "total" && k !== "methodology_note")
    .map(([k, v]) => ({
      subject: k.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase()),
      value: Math.round(v as number),
    }));
  return (
    <ResponsiveContainer width="100%" height={220}>
      <RadarChart data={data}>
        <PolarGrid stroke="#1f2937" />
        <PolarAngleAxis dataKey="subject" tick={{ fill: "#9ca3af", fontSize: 10 }} />
        <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: "#6b7280", fontSize: 9 }} />
        <Radar dataKey="value" stroke="#22c55e" fill="#22c55e" fillOpacity={0.25} />
        <Tooltip
          contentStyle={{ background: "#111827", border: "1px solid #374151", borderRadius: 8 }}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
}

export function SeverityBar({ findings }: { findings: any[] }) {
  const counts: Record<string, number> = { Critical: 0, High: 0, Medium: 0, Low: 0 };
  findings.forEach(f => { if (counts[f.severity] !== undefined) counts[f.severity]++; });
  const data = Object.entries(counts).map(([name, value]) => ({ name, value }));
  const colors: Record<string, string> = { Critical: "#ef4444", High: "#f97316", Medium: "#eab308", Low: "#3b82f6" };
  return (
    <ResponsiveContainer width="100%" height={160}>
      <BarChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
        <XAxis dataKey="name" tick={{ fill: "#9ca3af", fontSize: 12 }} />
        <YAxis allowDecimals={false} tick={{ fill: "#9ca3af", fontSize: 12 }} />
        <Tooltip contentStyle={{ background: "#111827", border: "1px solid #374151", borderRadius: 8 }} />
        {data.map(d => (
          <Bar key={d.name} dataKey="value" fill={colors[d.name] || "#6b7280"} radius={[4,4,0,0]} />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}
