"use client";
import { useState } from "react";
import { apiClient } from "@/lib/api";

export default function ReportsPage() {
  const [analysisId, setAnalysisId] = useState("");
  const [title, setTitle] = useState("GreenForge AI Sustainability Report");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const generate = async () => {
    setLoading(true); setError(""); setResult(null);
    try {
      const id = analysisId ? parseInt(analysisId) : undefined;
      const res = await apiClient.generateReport(id, title);
      setResult(res);
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  const downloadPDF = () => {
    if (result?.report_id) {
      window.open(`http://localhost:8000/api/reports/${result.report_id}/pdf`, "_blank");
    }
  };

  const downloadJSON = () => {
    if (!result?.content) return;
    const blob = new Blob([JSON.stringify(result.content, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a"); a.href = url; a.download = "greenforge_report.json"; a.click();
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-white">Reports</h1>
        <p className="text-gray-400 text-sm mt-1">Generate comprehensive sustainability analysis reports with PDF and JSON export.</p>
      </div>

      <div className="card mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-3">
          <div className="md:col-span-2">
            <label className="text-xs text-gray-400 mb-1 block">Report Title</label>
            <input value={title} onChange={e => setTitle(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 text-gray-200 text-sm rounded-lg px-3 py-2 focus:outline-none" />
          </div>
          <div>
            <label className="text-xs text-gray-400 mb-1 block">Analysis ID (optional)</label>
            <input value={analysisId} onChange={e => setAnalysisId(e.target.value)} type="number" placeholder="Leave blank for latest"
              className="w-full bg-gray-800 border border-gray-700 text-gray-200 text-sm rounded-lg px-3 py-2 focus:outline-none" />
          </div>
        </div>
        <button onClick={generate} disabled={loading} className="btn-primary">
          {loading ? "Generating…" : "Generate Report"}
        </button>
      </div>

      {error && <div className="mb-4 p-3 bg-red-900/30 border border-red-700 rounded-lg text-red-300 text-sm">{error}</div>}

      {result && (
        <div className="space-y-4">
          {/* Header */}
          <div className="card border-green-900/40">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h2 className="font-bold text-white">{result.title}</h2>
                <p className="text-xs text-gray-500 mt-0.5">Report ID: {result.report_id} · {result.created_at?.slice(0,19)}</p>
              </div>
              <div className="flex gap-2">
                {result.pdf_available && (
                  <button onClick={downloadPDF} className="btn-primary btn-sm">📄 Download PDF</button>
                )}
                <button onClick={downloadJSON} className="btn-secondary btn-sm">{ } Download JSON</button>
              </div>
            </div>

            {/* Executive Summary */}
            <div className="p-3 bg-gray-800 rounded-lg">
              <div className="text-xs text-gray-400 mb-1 font-medium">Executive Summary</div>
              <p className="text-sm text-gray-300 leading-6">{result.content?.executive_summary}</p>
            </div>
          </div>

          {/* Score */}
          {result.content?.greenforge_score?.total && (
            <div className="card">
              <div className="text-sm font-medium text-gray-200 mb-3">GreenForge Score</div>
              <div className="grid grid-cols-4 gap-2 text-xs">
                {Object.entries(result.content.greenforge_score)
                  .filter(([k]) => !["methodology_note", "total"].includes(k))
                  .map(([k, v]: any) => (
                  <div key={k} className="p-2 bg-gray-800 rounded text-center">
                    <div className={`text-lg font-bold ${v >= 80 ? "text-green-400" : v >= 60 ? "text-yellow-400" : "text-red-400"}`}>{Math.round(v)}</div>
                    <div className="text-gray-500 leading-4">{k.replace(/_/g," ")}</div>
                  </div>
                ))}
                <div className="p-2 bg-green-900/30 border border-green-800 rounded text-center">
                  <div className="text-2xl font-bold text-green-400">{Math.round(result.content.greenforge_score.total)}</div>
                  <div className="text-gray-400">Total</div>
                </div>
              </div>
            </div>
          )}

          {/* Findings */}
          {result.content?.code_findings?.findings?.length > 0 && (
            <div className="card">
              <div className="text-sm font-medium text-gray-200 mb-3">
                Code Findings ({result.content.code_findings.total})
              </div>
              <div className="flex gap-2 mb-3">
                {Object.entries(result.content.code_findings.by_severity || {}).map(([s, n]: any) => n > 0 && (
                  <span key={s} className={`badge-${s.toLowerCase() === "critical" ? "critical" : s.toLowerCase() === "high" ? "high" : s.toLowerCase() === "medium" ? "medium" : "low"}`}>
                    {s}: {n}
                  </span>
                ))}
              </div>
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {result.content.code_findings.findings.slice(0, 8).map((f: any, i: number) => (
                  <div key={i} className="p-2 bg-gray-800 rounded text-xs">
                    <span className={`badge-${f.severity?.toLowerCase() === "critical" ? "critical" : f.severity?.toLowerCase() === "high" ? "high" : "medium"} mr-2`}>{f.severity}</span>
                    <span className="text-gray-200">{f.title}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Responsible AI */}
          <div className="card border-blue-900/40">
            <div className="text-sm font-medium text-gray-200 mb-2">Responsible AI Statement</div>
            <p className="text-xs text-gray-500 leading-5">{result.content?.responsible_ai_note}</p>
          </div>

          {/* SDG */}
          <div className="card border-green-900/40 bg-green-950/10">
            <div className="text-xs font-medium text-green-400 mb-2">SDG Alignment</div>
            <div className="text-xs text-gray-300">{result.content?.sdg_alignment?.primary}</div>
            {result.content?.sdg_alignment?.secondary?.map((s: string) => (
              <div key={s} className="text-xs text-gray-500">↳ {s}</div>
            ))}
          </div>
        </div>
      )}

      {!result && !loading && (
        <div className="card text-center py-12">
          <div className="text-4xl mb-3">📄</div>
          <p className="text-gray-400">Click <strong className="text-green-400">Generate Report</strong> to create a full sustainability analysis report.</p>
          <p className="text-xs text-gray-600 mt-2">Run an analysis first for richer report content.</p>
        </div>
      )}
    </div>
  );
}
