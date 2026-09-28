// Centralised API client for GreenForge AI frontend
const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `API error ${res.status}`);
  }
  return res.json();
}

export const apiClient = {
  health: () => api<any>("/health"),

  analyzeCode: (code: string, language = "python") =>
    api<any>("/analyze/code", {
      method: "POST",
      body: JSON.stringify({ code, language }),
    }),

  benchmark: (code: string, label = "original", runs = 5, analysis_id?: number) =>
    api<any>("/benchmark", {
      method: "POST",
      body: JSON.stringify({ code, label, runs, analysis_id }),
    }),

  optimize: (code: string, language = "python", findings?: any[], analysis_id?: number, run_benchmark = true) =>
    api<any>("/optimize", {
      method: "POST",
      body: JSON.stringify({ code, language, findings, analysis_id, run_benchmark }),
    }),

  ragQuery: (query: string, top_k = 5, context?: any) =>
    api<any>("/rag/query", {
      method: "POST",
      body: JSON.stringify({ query, top_k, context }),
    }),

  ragDocuments: () => api<any>("/rag/documents"),

  copilotChat: (message: string, history: any[] = [], analysis_context?: any) =>
    api<any>("/copilot/chat", {
      method: "POST",
      body: JSON.stringify({ message, history, analysis_context }),
    }),

  mlWorkloads: () => api<any>("/ml/workloads"),
  analyzeML: (workload_id: string) =>
    api<any>(`/ml/analyze/${workload_id}`, { method: "POST" }),

  generateReport: (analysis_id?: number, title?: string) =>
    api<any>("/reports/generate", {
      method: "POST",
      body: JSON.stringify({ analysis_id, title: title || "GreenForge AI Report", include_benchmarks: true, include_ml: true }),
    }),

  getSettings: () => api<any>("/settings"),
  updateSettings: (data: any) =>
    api<any>("/settings", { method: "POST", body: JSON.stringify(data) }),

  demoProjects: () => api<any>("/demo/projects"),
  demoProject: (id: string) => api<any>(`/demo/projects/${id}`),
  runDemo: (id: string) => api<any>(`/demo/run/${id}`, { method: "POST" }),
};
