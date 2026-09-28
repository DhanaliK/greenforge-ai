"use client";
import { useState, useEffect } from "react";
import { apiClient } from "@/lib/api";
import ScoreGauge from "@/components/ScoreGauge";
import { BenchmarkBar, MemoryBar } from "@/components/Charts";

export default function GreenAIPage() {
  const [workloads, setWorkloads] = useState<any[]>([]);
  const [selected, setSelected] = useState("sklearn_baseline");
  const [result, setResult] = useState<any>(null);
  const [comparing, setComparing] = useState(false);
  const [compareResults, setCompareResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    apiClient.mlWorkloads().then(d => setWorkloads(d.workloads || [])).catch(() => {});
  }, []);

  const analyze = async () => {
    setLoading(true); setError(""); setResult(null);
    try {
      const res = await apiClient.analyzeML(selected);
      setResult(res);
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  const compareAll = async () => {
    setComparing(true); setCompareResults([]);
    const ids = ["sklearn_baseline", "sklearn_optimized", "sklearn_small"];
    const results: any[] = [];
    for (const id of ids) {
      try {
        const r = await apiClient.analyzeML(id);
        results.push(r);
      } catch { results.push({ workload_id: id, error: true }); }
    }
    setCompareResults(results);
    setComparing(false);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-white">Green AI Lab</h1>
        <p className="text-gray-400 text-sm mt-1">Analyze ML workloads for computational efficiency. Compare models on accuracy, latency, memory and resource usage.</p>
      </div>

      {/* Controls */}
      <div className="card mb-6">
        <div className="flex gap-3 items-center flex-wrap">
          <select value={selected} onChange={e => setSelected(e.target.value)}
            className="bg-gray-800 border border-gray-700 text-gray-200 text-sm rounded-lg px-3 py-2">
            {workloads.map(w => <option key={w.id} value={w.id}>{w.name}</option>)}
          </select>
          <button onClick={analyze} disabled={loading} className="btn-primary">
            {loading ? "Analyzing…" : "Run ML Analysis"}
          </button>
          <button onClick={compareAll} disabled={comparing} className="btn-secondary">
            {comparing ? "Comparing…" : "Compare All Models"}
          </button>
        </div>
        {workloads.find(w => w.id === selected) && (
          <p className="text-xs text-gray-500 mt-2">{workloads.find(w => w.id === selected)?.description}</p>
        )}
      </div>

      {error && <div className="mb-4 p-3 bg-red-900/30 border border-red-700 rounded-lg text-red-300 text-sm">{error}</div>}

      {/* Single result */}
      {result && !compareResults.length && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {/* Metrics */}
          <div className="card">
            <div className="text-sm font-medium text-gray-200 mb-3">{result.workload_name}</div>
            <div className="space-y-2 text-sm">
              {[
                ["Framework", result.framework],
                ["Parameters", result.metrics?.num_parameters?.toLocaleString()],
                ["Model Size", result.metrics?.model_size_mb ? `${result.metrics.model_size_mb} MB` : "—"],
                ["Accuracy", result.metrics?.accuracy ? `${(result.metrics.accuracy * 100).toFixed(1)}%` : "—"],
                ["Batch Size", result.metrics?.batch_size],
                ["Latency", result.metrics?.inference_latency_ms ? `${result.metrics.inference_latency_ms} ms` : "—"],
                ["Memory", result.metrics?.memory_mb ? `${result.metrics.memory_mb?.toFixed(1)} MB` : "—"],
              ].map(([k, v]) => v && (
                <div key={k as string} className="flex justify-between">
                  <span className="text-gray-500">{k}</span>
                  <span className="text-gray-200 font-medium">{v}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Score */}
          <div className="card flex flex-col items-center">
            <div className="text-xs text-gray-400 mb-3">GreenForge Score</div>
            <ScoreGauge score={result.greenforge_score?.total ?? 0} size={110} />
            <div className="mt-3 text-xs text-gray-500 text-center">ML Efficiency: {result.greenforge_score?.ml_efficiency?.toFixed(0)}</div>
          </div>

          {/* Findings */}
          <div className="card">
            <div className="text-sm font-medium text-gray-200 mb-3">ML Findings ({result.findings?.length || 0})</div>
            <div className="space-y-2">
              {(result.findings || []).map((f: any, i: number) => (
                <div key={i} className="p-2 bg-gray-800 rounded text-xs">
                  <span className={`${f.severity === "High" || f.severity === "Critical" ? "badge-high" : "badge-medium"} mr-2`}>{f.severity}</span>
                  <span className="text-gray-200">{f.title}</span>
                  <p className="text-gray-500 mt-1">{f.explanation?.slice(0, 100)}…</p>
                </div>
              ))}
              {(result.findings || []).length === 0 && <p className="text-gray-500 text-xs">No major inefficiencies detected.</p>}
            </div>
            <div className="mt-3">
              <div className="text-xs text-gray-400 mb-1">Recommendations</div>
              {(result.recommendations || []).map((r: string, i: number) => (
                <div key={i} className="text-xs text-green-400 leading-5">• {r}</div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Sustainability */}
      {result?.sustainability && !compareResults.length && (
        <div className="card mb-6 border-green-900/40">
          <div className="text-sm font-medium text-gray-200 mb-2">Sustainability Estimate</div>
          <div className="text-xs text-yellow-400 mb-2">⚠ {result.sustainability.label || "Modeled estimate"}</div>
          <div className="grid grid-cols-3 gap-3 text-xs">
            <div className="p-2 bg-gray-800 rounded">
              <div className="text-gray-500">Runtime</div>
              <div className="text-white font-medium">{result.sustainability.runtime_seconds?.toFixed(4)}s</div>
            </div>
            <div className="p-2 bg-gray-800 rounded">
              <div className="text-gray-500">Est. Energy</div>
              <div className="text-white font-medium">{result.sustainability.estimated_energy_wh?.toFixed(8)} Wh</div>
            </div>
            <div className="p-2 bg-gray-800 rounded">
              <div className="text-gray-500">Est. Carbon</div>
              <div className="text-white font-medium">{result.sustainability.estimated_carbon_gco2e?.toFixed(8)} gCO2e</div>
            </div>
          </div>
          <p className="text-xs text-gray-600 mt-2">{result.sustainability.methodology_note}</p>
        </div>
      )}

      {/* Model Comparison Table */}
      {compareResults.length > 0 && (
        <div className="card">
          <div className="text-sm font-medium text-gray-200 mb-4">Model Comparison</div>
          <div className="text-xs text-gray-500 mb-3">
            ⚖ Accuracy vs efficiency trade-off. The lowest-latency model is not automatically the best choice — consider your accuracy requirements.
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-800">
                  {["Model", "Accuracy", "Latency (ms)", "Memory (MB)", "Batch Size", "GF Score", "Recommendation"].map(h => (
                    <th key={h} className="text-left py-2 px-3 text-xs text-gray-400 font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {compareResults.map((r: any) => (
                  <tr key={r.workload_id} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                    <td className="py-2 px-3 font-medium text-gray-200">{r.workload_name || r.workload_id}</td>
                    <td className="py-2 px-3 text-gray-300">{r.metrics?.accuracy ? `${(r.metrics.accuracy * 100).toFixed(1)}%` : "—"}</td>
                    <td className="py-2 px-3 text-gray-300">{r.metrics?.inference_latency_ms?.toFixed(1) || "—"}</td>
                    <td className="py-2 px-3 text-gray-300">{r.metrics?.memory_mb?.toFixed(1) || "—"}</td>
                    <td className="py-2 px-3 text-gray-300">{r.metrics?.batch_size || "—"}</td>
                    <td className="py-2 px-3">
                      <span className={`font-bold ${(r.greenforge_score?.total ?? 0) >= 70 ? "text-green-400" : "text-yellow-400"}`}>
                        {r.greenforge_score?.total?.toFixed(0) ?? "—"}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-xs text-green-400">{r.recommendations?.[0]?.slice(0, 50) || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-3 p-3 bg-blue-900/20 border border-blue-800 rounded text-xs text-blue-300">
            💡 The comparison shows accuracy vs. efficiency trade-offs. Choose based on your application's requirements. A smaller, faster model may be preferable if accuracy difference is acceptable.
          </div>
        </div>
      )}

      {!result && !compareResults.length && !loading && (
        <div className="card text-center py-12">
          <div className="text-4xl mb-3">🧠</div>
          <p className="text-gray-400">Select a demo ML workload and click <strong className="text-blue-400">Run ML Analysis</strong> to inspect model efficiency.</p>
        </div>
      )}
      {loading && (
        <div className="card text-center py-12">
          <p className="text-gray-400">Running ML workload benchmark… (this may take a few seconds)</p>
        </div>
      )}
    </div>
  );
}
