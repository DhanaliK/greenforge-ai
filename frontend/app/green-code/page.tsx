"use client";
import { useState, useRef } from "react";
import { apiClient } from "@/lib/api";
import CodeViewer from "@/components/CodeViewer";
import DiffViewer from "@/components/DiffViewer";
import ScoreGauge from "@/components/ScoreGauge";
import { ScoreRadar, SeverityBar, BenchmarkBar, MemoryBar } from "@/components/Charts";

const DEMO_CODE = `# Paste your Python code here, or load a demo below
def find_common_elements(list_a, list_b):
    common = []
    for a in list_a:
        for b in list_b:
            if a == b and a not in common:
                common.append(a)
    return common

data = list(range(1000))
result = find_common_elements(data[:500], data[300:])
print(f"Common: {len(result)}")
`;

export default function GreenCodePage() {
  const [code, setCode] = useState(DEMO_CODE);
  const [language, setLanguage] = useState("python");
  const [tab, setTab] = useState<"analyze"|"optimize"|"benchmark">("analyze");
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);
  const [optimization, setOptimization] = useState<any>(null);
  const [benchmark, setBenchmark] = useState<any>(null);
  const [error, setError] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  const analyze = async () => {
    setLoading(true); setError(""); setAnalysis(null);
    try {
      const res = await apiClient.analyzeCode(code, language);
      setAnalysis(res);
      setTab("analyze");
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  const optimize = async () => {
    if (!analysis) return analyze();
    setLoading(true); setError(""); setOptimization(null);
    try {
      const res = await apiClient.optimize(code, language, analysis.findings, analysis.analysis_id);
      setOptimization(res);
      setTab("optimize");
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  const runBenchmark = async () => {
    setLoading(true); setError(""); setBenchmark(null);
    try {
      const res = await apiClient.benchmark(code, "original", 5, analysis?.analysis_id);
      setBenchmark(res);
      setTab("benchmark");
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  const loadFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const text = await file.text();
    setCode(text);
    if (file.name.endsWith(".js") || file.name.endsWith(".ts")) setLanguage("javascript");
    else setLanguage("python");
  };

  const severityClass = (s: string) =>
    s === "Critical" ? "badge-critical" : s === "High" ? "badge-high" : s === "Medium" ? "badge-medium" : "badge-low";

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-white">Green Code Engine</h1>
        <p className="text-gray-400 text-sm mt-1">Analyze source code for computational inefficiencies and get AI-powered optimization recommendations.</p>
        <div className="mt-2 p-2 bg-yellow-900/20 border border-yellow-800 rounded-lg text-xs text-yellow-400">
          ⚠ Security: Run benchmark only on code you trust, in a local development environment.
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Code input */}
        <div className="space-y-4">
          <div className="card">
            <div className="flex items-center justify-between mb-3">
              <div className="flex gap-2 items-center">
                <select value={language} onChange={e => setLanguage(e.target.value)}
                  className="bg-gray-800 border border-gray-700 text-gray-200 text-sm rounded px-2 py-1">
                  <option value="python">Python</option>
                  <option value="javascript">JavaScript/TypeScript</option>
                </select>
                <button onClick={() => fileRef.current?.click()} className="btn-secondary btn-sm">📁 Upload</button>
                <input ref={fileRef} type="file" accept=".py,.js,.ts,.txt" className="hidden" onChange={loadFile} />
              </div>
              <div className="flex gap-2">
                <button onClick={analyze} disabled={loading} className="btn-primary btn-sm">
                  {loading ? "…" : "Analyze"}
                </button>
                <button onClick={optimize} disabled={loading} className="btn-secondary btn-sm">
                  Optimize
                </button>
                <button onClick={runBenchmark} disabled={loading} className="btn-secondary btn-sm">
                  Benchmark
                </button>
              </div>
            </div>
            <textarea
              value={code}
              onChange={e => setCode(e.target.value)}
              className="w-full bg-gray-950 border border-gray-800 rounded-lg p-3 font-mono text-xs text-gray-200 leading-5 resize-none focus:outline-none focus:border-green-700"
              rows={22}
              spellCheck={false}
              placeholder="Paste Python code here…"
            />
          </div>
        </div>

        {/* Right: Results */}
        <div>
          {error && <div className="mb-3 p-3 bg-red-900/30 border border-red-700 rounded-lg text-red-300 text-sm">{error}</div>}

          {/* Tabs */}
          <div className="flex gap-1 mb-4 bg-gray-900 border border-gray-800 p-1 rounded-lg">
            {(["analyze","optimize","benchmark"] as const).map(t => (
              <button key={t} onClick={() => setTab(t)}
                className={`flex-1 text-xs py-1.5 rounded-md font-medium capitalize transition-colors ${tab===t ? "bg-green-800 text-green-100" : "text-gray-400 hover:text-gray-200"}`}>
                {t}
              </button>
            ))}
          </div>

          {/* Analysis Tab */}
          {tab === "analyze" && analysis && (
            <div className="space-y-4">
              <div className="flex gap-4">
                <div className="card flex flex-col items-center flex-1">
                  <div className="text-xs text-gray-400 mb-2">GreenForge Score</div>
                  <ScoreGauge score={analysis.greenforge_score?.total ?? 0} size={100} />
                </div>
                <div className="card flex-1">
                  <div className="text-xs text-gray-400 mb-1">Complexity</div>
                  <div className="text-sm text-gray-300">{analysis.complexity?.summary}</div>
                  <div className="mt-2 grid grid-cols-2 gap-1 text-xs">
                    <div className="text-gray-500">Functions: <span className="text-white">{analysis.complexity?.total_functions}</span></div>
                    <div className="text-gray-500">Classes: <span className="text-white">{analysis.complexity?.total_classes}</span></div>
                    <div className="text-gray-500">Max depth: <span className="text-white">{analysis.complexity?.max_loop_depth}</span></div>
                    <div className="text-gray-500">AI: <span className="text-green-400 text-xs">{analysis.ai_provider?.includes("Local") ? "Local" : "Granite"}</span></div>
                  </div>
                </div>
              </div>

              {/* Score Radar */}
              {analysis.greenforge_score && (
                <div className="card">
                  <div className="text-xs text-gray-400 mb-2">Score Breakdown</div>
                  <ScoreRadar breakdown={analysis.greenforge_score} />
                  <details className="mt-2">
                    <summary className="text-xs text-gray-500 cursor-pointer">Score methodology</summary>
                    <p className="text-xs text-gray-600 mt-1 leading-5">{analysis.greenforge_score.methodology_note}</p>
                  </details>
                </div>
              )}

              {/* Findings */}
              <div className="card">
                <div className="text-sm text-gray-300 font-medium mb-3">
                  {analysis.findings?.length || 0} Issues Detected
                </div>
                {analysis.findings?.length > 0 && <SeverityBar findings={analysis.findings} />}
                <div className="mt-3 space-y-2 max-h-64 overflow-y-auto">
                  {(analysis.findings || []).map((f: any, i: number) => (
                    <details key={i} className="bg-gray-800 rounded-lg p-3 cursor-pointer">
                      <summary className="flex items-center gap-2">
                        <span className={severityClass(f.severity)}>{f.severity}</span>
                        <span className="text-sm text-gray-200 font-medium">{f.title}</span>
                        {f.line_start && <span className="text-xs text-gray-500 ml-auto">Line {f.line_start}</span>}
                      </summary>
                      <div className="mt-2 text-xs text-gray-400 leading-5">{f.explanation}</div>
                      {f.evidence && (
                        <pre className="mt-2 p-2 bg-gray-950 rounded text-xs text-gray-300 overflow-x-auto">{f.evidence.slice(0,300)}</pre>
                      )}
                      <div className="mt-2 text-xs text-green-400">💡 {f.recommendation}</div>
                      {f.estimated_complexity && (
                        <div className="mt-1 text-xs text-yellow-400">Complexity: {f.estimated_complexity}</div>
                      )}
                    </details>
                  ))}
                </div>
              </div>

              {/* Sustainability */}
              {analysis.sustainability_estimate && (
                <div className="card border-green-900/40">
                  <div className="text-xs text-gray-400 mb-2">Sustainability Estimate</div>
                  <div className="text-xs text-yellow-400 mb-1">⚠ {analysis.sustainability_estimate.label}</div>
                  {analysis.sustainability_estimate.estimated_energy_wh ? (
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="text-gray-500">Est. Energy: <span className="text-white">{analysis.sustainability_estimate.estimated_energy_wh?.toFixed(8)} Wh</span></div>
                      <div className="text-gray-500">Est. Carbon: <span className="text-white">{analysis.sustainability_estimate.estimated_carbon_gco2e?.toFixed(8)} gCO2e</span></div>
                    </div>
                  ) : (
                    <p className="text-xs text-gray-500">{analysis.sustainability_estimate.methodology_note}</p>
                  )}
                  <p className="text-xs text-gray-600 mt-2">{analysis.sustainability_estimate.methodology_note}</p>
                </div>
              )}
            </div>
          )}

          {/* Optimize Tab */}
          {tab === "optimize" && optimization && (
            <div className="space-y-4">
              <div className="card">
                <div className="flex items-center gap-2 mb-3">
                  <span className={`text-xs px-2 py-1 rounded-full ${optimization.validation_passed ? "bg-green-900/50 text-green-300" : "bg-red-900/50 text-red-300"}`}>
                    {optimization.validation_passed ? "✓ Validated" : "✗ Validation failed"}
                  </span>
                  <span className="text-xs text-gray-500">{optimization.ai_provider?.includes("Local") ? "Local AI mode" : "IBM Granite"}</span>
                </div>
                <div className="text-xs text-gray-300 leading-5 mb-3">{optimization.explanation}</div>
                {optimization.trade_offs && (
                  <div className="text-xs text-yellow-400 leading-5">⚖ Trade-offs: {optimization.trade_offs}</div>
                )}
              </div>

              {optimization.optimized_code && (
                <div className="card">
                  <div className="text-sm text-gray-300 font-medium mb-3">Code Diff</div>
                  <DiffViewer before={optimization.original_code || code} after={optimization.optimized_code} />
                  <div className="flex gap-2 mt-3">
                    <button onClick={() => setCode(optimization.optimized_code)} className="btn-primary btn-sm">Use Optimized Version</button>
                    <button onClick={() => setCode(optimization.original_code || code)} className="btn-secondary btn-sm">Keep Original</button>
                    <button onClick={runBenchmark} className="btn-secondary btn-sm">Run Benchmark</button>
                  </div>
                </div>
              )}

              {optimization.before_benchmark && optimization.after_benchmark && (
                <div className="card">
                  <div className="text-sm text-gray-300 font-medium mb-3">Benchmark Comparison</div>
                  <div className="grid grid-cols-2 gap-3">
                    <BenchmarkBar
                      before={optimization.before_benchmark.mean_runtime || 0}
                      after={optimization.after_benchmark.mean_runtime || 0}
                    />
                    <MemoryBar
                      before={optimization.before_benchmark.peak_memory_mb || 0}
                      after={optimization.after_benchmark.peak_memory_mb || 0}
                    />
                  </div>
                  <div className="mt-2 text-xs text-green-400 font-medium">
                    {optimization.comparison?.improvement_label}
                  </div>
                  {optimization.before_benchmark.sustainability && (
                    <div className="mt-2 text-xs text-gray-500">
                      Modeled sustainability — Before: {optimization.before_benchmark.sustainability?.estimated_energy_wh?.toFixed(8)} Wh |
                      After: {optimization.after_benchmark.sustainability?.estimated_energy_wh?.toFixed(8)} Wh
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Benchmark Tab */}
          {tab === "benchmark" && benchmark && (
            <div className="space-y-4">
              <div className="card">
                <div className="text-sm font-medium text-gray-200 mb-3">Benchmark Results — {benchmark.label}</div>
                {benchmark.success ? (
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    {[
                      ["Mean Runtime", `${benchmark.mean_runtime?.toFixed(4)}s`, "text-white"],
                      ["Median Runtime", `${benchmark.median_runtime?.toFixed(4)}s`, "text-white"],
                      ["Min / Max", `${benchmark.min_runtime?.toFixed(4)}s / ${benchmark.max_runtime?.toFixed(4)}s`, "text-gray-300"],
                      ["Peak Memory", `${benchmark.peak_memory_mb?.toFixed(2)} MB`, "text-blue-300"],
                      ["CPU Time", `${benchmark.cpu_time?.toFixed(4)}s`, "text-yellow-300"],
                      ["Runs", String(benchmark.runs), "text-gray-300"],
                    ].map(([k, v, c]) => (
                      <div key={k} className="p-2 bg-gray-800 rounded">
                        <div className="text-xs text-gray-500">{k}</div>
                        <div className={`font-semibold ${c}`}>{v}</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-red-400 text-sm">{benchmark.error_message}</div>
                )}
                {benchmark.sustainability && (
                  <div className="mt-3 p-3 bg-green-950/30 border border-green-900/50 rounded-lg">
                    <div className="text-xs text-yellow-400 mb-1">⚠ Modeled sustainability estimate</div>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="text-gray-500">Est. Energy: <span className="text-white">{benchmark.sustainability.estimated_energy_wh?.toFixed(8)} Wh</span></div>
                      <div className="text-gray-500">Est. Carbon: <span className="text-white">{benchmark.sustainability.estimated_carbon_gco2e?.toFixed(8)} gCO2e</span></div>
                    </div>
                    <p className="text-xs text-gray-600 mt-1">{benchmark.sustainability.methodology_note?.slice(0, 150)}…</p>
                  </div>
                )}
                {benchmark.output_sample && (
                  <div className="mt-3">
                    <div className="text-xs text-gray-500 mb-1">Output sample:</div>
                    <pre className="p-2 bg-gray-950 rounded text-xs text-gray-400">{benchmark.output_sample.slice(0,200)}</pre>
                  </div>
                )}
              </div>
            </div>
          )}

          {!analysis && !optimization && !benchmark && !loading && (
            <div className="card text-center py-12">
              <div className="text-4xl mb-3">⟨⟩</div>
              <p className="text-gray-400">Paste your code on the left and click <strong className="text-green-400">Analyze</strong> to detect computational inefficiencies.</p>
            </div>
          )}
          {loading && (
            <div className="card text-center py-12">
              <div className="text-2xl mb-3 animate-spin">⟳</div>
              <p className="text-gray-400">Running analysis…</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
