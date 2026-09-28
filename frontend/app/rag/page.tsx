"use client";
import { useState, useEffect } from "react";
import { apiClient } from "@/lib/api";

export default function RAGPage() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<any>(null);
  const [docs, setDocs] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => { apiClient.ragDocuments().then(setDocs).catch(() => {}); }, []);

  const search = async () => {
    if (!query.trim()) return;
    setLoading(true); setError(""); setResult(null);
    try {
      const res = await apiClient.ragQuery(query);
      setResult(res);
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  };

  const examples = [
    "What is Software Carbon Intensity (SCI)?",
    "How does batching improve ML inference efficiency?",
    "What is PUE and why does it matter?",
    "How do nested loops affect energy consumption?",
    "What are the three pillars of green software?",
    "How does carbon-aware computing work?",
  ];

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-white">RAG Knowledge Base</h1>
        <p className="text-gray-400 text-sm mt-1">
          Query the GreenForge AI knowledge base covering green software engineering, sustainable AI, SDGs, and optimization practices.
          Answers are grounded in retrieved documents.
        </p>
      </div>

      {/* Search */}
      <div className="card mb-6">
        <div className="flex gap-2">
          <input
            value={query} onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === "Enter" && search()}
            placeholder="Ask about green software, sustainable AI, efficiency…"
            className="flex-1 bg-gray-800 border border-gray-700 text-gray-200 text-sm rounded-lg px-4 py-2.5 focus:outline-none focus:border-green-600"
          />
          <button onClick={search} disabled={loading || !query.trim()} className="btn-primary">
            {loading ? "…" : "Search"}
          </button>
        </div>
        <div className="flex flex-wrap gap-2 mt-3">
          {examples.map(ex => (
            <button key={ex} onClick={() => { setQuery(ex); }}
              className="text-xs bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-gray-200 px-2 py-1 rounded border border-gray-700 transition-colors">
              {ex}
            </button>
          ))}
        </div>
      </div>

      {error && <div className="mb-4 p-3 bg-red-900/30 border border-red-700 rounded-lg text-red-300 text-sm">{error}</div>}

      {/* Result */}
      {result && (
        <div className="space-y-4 mb-6">
          <div className="card border-green-900/40">
            <div className="flex items-center gap-2 mb-3">
              <span className={`text-xs px-2 py-1 rounded-full ${result.is_grounded ? "bg-green-900/50 text-green-300" : "bg-yellow-900/50 text-yellow-300"}`}>
                {result.is_grounded ? "✓ Evidence-grounded" : "⚠ General reasoning"}
              </span>
              <span className="text-xs text-gray-500">{result.ai_provider?.includes("Local") ? "Local AI mode" : "IBM Granite"}</span>
            </div>
            <div className="text-sm text-gray-200 leading-6 whitespace-pre-wrap">{result.answer}</div>
          </div>

          {result.source_chunks?.length > 0 && (
            <div className="card">
              <div className="text-sm font-medium text-gray-200 mb-3">Source Documents ({result.source_chunks.length})</div>
              <div className="space-y-3">
                {result.source_chunks.map((c: any, i: number) => (
                  <div key={i} className="p-3 bg-gray-800 rounded-lg">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-medium text-blue-300">{c.document_title}</span>
                      <span className="text-xs text-gray-500 ml-auto">score: {c.score?.toFixed(3)}</span>
                    </div>
                    <p className="text-xs text-gray-400 leading-5">{c.chunk_text}</p>
                    {c.document_source && (
                      <a href={c.document_source} target="_blank" rel="noopener noreferrer"
                        className="text-xs text-green-500 hover:underline mt-1 inline-block">{c.document_source}</a>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Document list */}
      <div className="card">
        <div className="text-sm font-medium text-gray-200 mb-3">Knowledge Base ({docs.length} documents)</div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {docs.map((d, i) => (
            <div key={i} className="p-2 bg-gray-800 rounded text-xs">
              <div className="text-gray-200 font-medium">{d.title}</div>
              <div className="text-gray-500 mt-0.5">{d.category} · <a href={d.source} target="_blank" rel="noopener noreferrer" className="text-green-500 hover:underline">{d.source?.slice(0, 40)}</a></div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
