"use client";
import { useState } from "react";
import { apiClient } from "@/lib/api";
import { BenchmarkBar, MemoryBar } from "@/components/Charts";

const SAMPLE = `import time
data = list(range(100000))
result = [x**2 for x in data if x % 2 == 0]
print(f"Done: {len(result)} items")
`;

export default function BenchmarksPage() {
  const [code, setCode] = useState(SAMPLE);
  const [runs, setRuns] = useState(5);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [history, setHistory] = useState<any[]>([]);

  const runBench = async () => {
    setLoading(true); setError("");
    try {
      const res = await apiClient.benchmark(code, `Run ${history.length + 1}`, runs);
      setResult(res);
      setHistory(h => [res, ...h].slice(0, 10));
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-white">Benchmarks</h1>
        <p className="text-gray-400 text-sm mt-1">Execute code and measure runtime, CPU time and memory. Safe subprocess execution with timeout.</p>
        <div className="mt-2 p-2 bg-yellow-900/20 border border-yellow-800 rounded-lg text-xs text-yellow-400">
          ⚠ Only run trusted code. Each benchmark runs in an isolated subprocess with a timeout.
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div className="card">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <label className="text-xs text-gray-400">Runs:</label>
                <input type="number" min={1} max={10} value={runs} onChange={e => setRuns(Number(e.target.value))}
                  className="w-16 bg-gray-800 border border-gray-700 text-gray-200 text-sm rounded px-2 py-1 text-center" />
              </div>
              <button onClick={runBench} disabled={loading} className="btn-primary">
                {loading ? "Running…" : "▶ Run Benchmark"}
              </button>
            </div>
            <textarea value={code} onChange={e => setCode(e.target.value)}
              className="w-full bg-gray-950 border border-gray-800 rounded-lg p-3 font-mono text-xs text-gray-200 leading-5 resize-none focus:outline-none"
              rows={18} spellCheck={false} />
          </div>
        </div>

        <div className="space-y-4">
          {error && <div className="p-3 bg-red-900/30 border border-red-700 rounded-lg text-red-300 text-sm">{error}</div>}
          {result ? (
            <>
              <div className="card">
                <div className="flex items-center gap-2 mb-3">
                  <span className={`text-xs px-2 py-1 rounded-full ${result.success ? "bg-green-900/50 text-green-300" : "bg-red-900/50 text-red-300"}`}>
                    {result.success ? "✓ Success" : "✗ Failed"}
                  </span>
                  <span className="text-xs text-gray-500">{result.runs} run(s)</span>
                </div>
                {result.success ? (
                  <div className="grid grid-cols-2 gap-3">
                    {[
                      ["Mean Runtime", `${result.mean_runtime?.toFixed(4)}s`, "text-white"],
                      ["Median Runtime", `${result.median_runtime?.toFixed(4)}s`, "text-gray-300"],
                      ["Min", `${result.min_runtime?.toFixed(4)}s`, "text-green-300"],
                      ["Max", `${result.max_runtime?.toFixed(4)}s`, "text-red-300"],
                      ["Peak Memory", `${result.peak_memory_mb?.toFixed(2)} MB`, "text-blue-300"],
                      ["CPU Time", `${result.cpu_time?.toFixed(4)}s`, "text-yellow-300"],
                    ].map(([k, v, c]) => (
                      <div key={k as string} className="p-2 bg-gray-800 rounded">
                        <div className="text-xs text-gray-500">{k}</div>
                        <div className={`font-semibold text-sm ${c}`}>{v}</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-red-400 text-sm">{result.error_message}</p>
                )}
              </div>

              {result.sustainability && (
                <div className="card border-green-900/40">
                  <div className="text-xs font-medium text-gray-300 mb-2">Sustainability Estimate</div>
                  <div className="text-xs text-yellow-400 mb-2">⚠ Modeled estimate — based on configured hardware assumptions</div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="p-2 bg-gray-800 rounded">
                      <div className="text-gray-500">Est. Energy</div>
                      <div className="text-white">{result.sustainability.estimated_energy_wh?.toFixed(8)} Wh</div>
                    </div>
                    <div className="p-2 bg-gray-800 rounded">
                      <div className="text-gray-500">Est. Carbon</div>
                      <div className="text-white">{result.sustainability.estimated_carbon_gco2e?.toFixed(8)} gCO2e</div>
                    </div>
                  </div>
                  <p className="text-xs text-gray-600 mt-2 leading-5">{result.sustainability.methodology_note?.slice(0,200)}…</p>
                </div>
              )}

              {result.output_sample && (
                <div className="card">
                  <div className="text-xs text-gray-400 mb-1">Output</div>
                  <pre className="text-xs text-gray-300 bg-gray-950 p-2 rounded overflow-x-auto">{result.output_sample}</pre>
                </div>
              )}
            </>
          ) : (
            !loading && <div className="card text-center py-10">
              <p className="text-gray-500">Run a benchmark to see results here.</p>
            </div>
          )}

          {history.length > 1 && (
            <div className="card">
              <div className="text-sm font-medium text-gray-200 mb-3">History ({history.length} runs)</div>
              <BenchmarkBar before={history[1]?.mean_runtime || 0} after={history[0]?.mean_runtime || 0} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
