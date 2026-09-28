"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/lib/api";
import ScoreGauge from "@/components/ScoreGauge";
import { ScoreRadar, SeverityBar } from "@/components/Charts";

export default function DashboardPage() {
  const [health, setHealth] = useState<any>(null);
  const [demos, setDemos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [demoRunning, setDemoRunning] = useState(false);
  const [demoResult, setDemoResult] = useState<any>(null);
  const [selectedDemo, setSelectedDemo] = useState("nested_loop");

  useEffect(() => {
    apiClient.health().then(setHealth).catch(() => {});
    apiClient.demoProjects()
      .then(d => setDemos(d.projects || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const runDemo = async () => {
    setDemoRunning(true);
    setDemoResult(null);
    try {
      const res = await apiClient.runDemo(selectedDemo);
      setDemoResult(res);
    } catch (e: any) {
      setDemoResult({ error: e.message });
    } finally {
      setDemoRunning(false);
    }
  };

  const score = demoResult?.analysis?.score?.total ?? null;
  const findings = demoResult?.analysis?.findings ?? [];

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Hero */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-500 to-emerald-700 flex items-center justify-center text-white font-bold">GF</div>
          <div>
            <h1 className="text-2xl font-bold text-white">GreenForge AI</h1>
            <p className="text-green-400 text-sm">Agentic AI for Sustainable Software &amp; Machine Learning</p>
          </div>
          {health && (
            <span className={`ml-auto text-xs px-3 py-1 rounded-full border ${health.ai_provider_available ? "bg-green-900/30 text-green-400 border-green-700" : "bg-yellow-900/30 text-yellow-400 border-yellow-700"}`}>
              {health.ai_provider_available ? `● ${health.ai_provider}` : "● Local fallback mode"}
            </span>
          )}
        </div>
        <p className="text-gray-400 text-sm mt-1">Make computational efficiency visible. Analyze, optimize, benchmark and understand the sustainability impact of your software and AI workloads.</p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: "GreenForge Score", value: score !== null ? `${Math.round(score)}/100` : "—", color: "text-green-400", sub: "After analysis" },
          { label: "Issues Detected", value: findings.length || "—", color: "text-orange-400", sub: "From last run" },
          { label: "Demo Mode", value: "Active", color: "text-blue-400", sub: "No IBM creds needed" },
          { label: "Status", value: health ? "Online" : "—", color: "text-emerald-400", sub: "Backend API" },
        ].map(c => (
          <div key={c.label} className="card">
            <div className="text-xs text-gray-500 mb-1">{c.label}</div>
            <div className={`text-2xl font-bold ${c.color}`}>{c.value}</div>
            <div className="text-xs text-gray-600 mt-1">{c.sub}</div>
          </div>
        ))}
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
        <Link href="/green-code" className="card hover:border-green-700 transition-colors cursor-pointer text-center">
          <div className="text-2xl mb-2">⟨⟩</div>
          <div className="font-semibold text-sm text-green-300">Analyze Code</div>
          <div className="text-xs text-gray-500 mt-1">Paste or upload source code</div>
        </Link>
        <Link href="/green-ai" className="card hover:border-blue-700 transition-colors cursor-pointer text-center">
          <div className="text-2xl mb-2">🧠</div>
          <div className="font-semibold text-sm text-blue-300">Green AI Lab</div>
          <div className="text-xs text-gray-500 mt-1">ML workload analysis</div>
        </Link>
        <Link href="/benchmarks" className="card hover:border-yellow-700 transition-colors cursor-pointer text-center">
          <div className="text-2xl mb-2">⏱</div>
          <div className="font-semibold text-sm text-yellow-300">Run Benchmark</div>
          <div className="text-xs text-gray-500 mt-1">Before vs after comparison</div>
        </Link>
        <button onClick={runDemo} disabled={demoRunning} className="card hover:border-purple-700 transition-colors cursor-pointer text-center disabled:opacity-60">
          <div className="text-2xl mb-2">▶</div>
          <div className="font-semibold text-sm text-purple-300">{demoRunning ? "Running…" : "View Demo"}</div>
          <div className="text-xs text-gray-500 mt-1">Full demo workflow</div>
        </button>
      </div>

      {/* Demo selector */}
      <div className="card mb-6">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold text-white">Analyze Demo Code</h2>
          <div className="flex gap-2 items-center">
            <select
              value={selectedDemo}
              onChange={e => setSelectedDemo(e.target.value)}
              className="bg-gray-800 border border-gray-700 text-gray-200 text-sm rounded-lg px-3 py-1.5"
            >
              {demos.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
            </select>
            <button onClick={runDemo} disabled={demoRunning} className="btn-primary btn-sm">
              {demoRunning ? "Running…" : "Run Demo"}
            </button>
          </div>
        </div>
        {loading && <p className="text-gray-500 text-sm">Loading demos…</p>}
        {!loading && demos.length === 0 && <p className="text-gray-500 text-sm">Could not load demos. Is the backend running?</p>}
        {demos.length > 0 && (
          <p className="text-sm text-gray-400">
            {demos.find(d => d.id === selectedDemo)?.description}
          </p>
        )}
      </div>

      {/* Demo results */}
      {demoResult && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {/* Score */}
          <div className="card flex flex-col items-center">
            <div className="text-sm text-gray-400 mb-3">GreenForge Score</div>
            <ScoreGauge score={score ?? 0} />
            {demoResult?.analysis?.score && (
              <div className="mt-3 w-full">
                <ScoreRadar breakdown={demoResult.analysis.score} />
              </div>
            )}
          </div>
          {/* Findings */}
          <div className="card">
            <div className="text-sm text-gray-400 mb-3">Issues Detected ({findings.length})</div>
            {findings.length > 0
              ? <SeverityBar findings={findings} />
              : <p className="text-gray-500 text-sm">No issues detected.</p>
            }
            <div className="mt-3 space-y-2 max-h-40 overflow-y-auto">
              {findings.slice(0, 5).map((f: any, i: number) => (
                <div key={i} className="text-xs p-2 rounded bg-gray-800 border-l-2 border-orange-600">
                  <span className={`badge-${f.severity?.toLowerCase() === "critical" ? "critical" : f.severity?.toLowerCase() === "high" ? "high" : "medium"} mr-2`}>
                    {f.severity}
                  </span>
                  {f.title}
                </div>
              ))}
            </div>
          </div>
          {/* Benchmark */}
          <div className="card">
            <div className="text-sm text-gray-400 mb-3">Benchmark Comparison</div>
            {demoResult?.optimization?.comparison ? (
              <div className="space-y-3">
                <div className="p-3 rounded bg-red-900/20 border border-red-800">
                  <div className="text-xs text-gray-400">Before</div>
                  <div className="text-lg font-bold text-red-300">
                    {demoResult.optimization.before_benchmark?.mean_runtime?.toFixed(4)}s
                  </div>
                  <div className="text-xs text-gray-500">{demoResult.optimization.before_benchmark?.peak_memory_mb?.toFixed(1)} MB peak</div>
                </div>
                <div className="p-3 rounded bg-green-900/20 border border-green-800">
                  <div className="text-xs text-gray-400">After</div>
                  <div className="text-lg font-bold text-green-300">
                    {demoResult.optimization.after_benchmark?.mean_runtime?.toFixed(4)}s
                  </div>
                  <div className="text-xs text-gray-500">{demoResult.optimization.after_benchmark?.peak_memory_mb?.toFixed(1)} MB peak</div>
                </div>
                <div className="text-xs text-green-400 font-medium">
                  {demoResult.optimization.comparison?.improvement_label}
                </div>
              </div>
            ) : (
              <p className="text-gray-500 text-sm">Run the demo to see benchmark results.</p>
            )}
          </div>
        </div>
      )}

      {/* SDG Banner */}
      <div className="card border-green-900/50 bg-green-950/20">
        <div className="flex flex-wrap gap-4 items-center">
          <div>
            <div className="text-xs text-green-500 font-semibold uppercase tracking-wider mb-1">SDG Alignment</div>
            <div className="flex gap-2 flex-wrap">
              {["SDG 12 — Responsible Consumption", "SDG 13 — Climate Action", "SDG 9 — Innovation & Infrastructure"].map(s => (
                <span key={s} className="text-xs bg-green-900/40 text-green-300 border border-green-800 px-2 py-0.5 rounded-full">{s}</span>
              ))}
            </div>
          </div>
          <div className="ml-auto text-xs text-gray-500 text-right">
            <div>Sustainability estimates are modeled — not validated measurements.</div>
            <div>GreenForge Score is a prototype indicator, not an industry certification.</div>
          </div>
        </div>
      </div>
    </div>
  );
}
