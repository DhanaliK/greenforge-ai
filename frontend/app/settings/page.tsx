"use client";
import { useState, useEffect } from "react";
import { apiClient } from "@/lib/api";

export default function SettingsPage() {
  const [settings, setSettings] = useState<any>(null);
  const [edits, setEdits] = useState<any>({});
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => { apiClient.getSettings().then(s => { setSettings(s); setEdits(s); }).catch(() => {}); }, []);

  const save = async () => {
    setSaving(true); setSaved(false);
    try {
      await apiClient.updateSettings(edits);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch {} finally { setSaving(false); }
  };

  const field = (key: string, label: string, unit: string, help: string) => (
    <div className="p-4 bg-gray-800 rounded-lg">
      <label className="text-sm text-gray-300 font-medium">{label}</label>
      <div className="flex items-center gap-2 mt-1">
        <input type="number" step="any" value={edits[key] ?? ""}
          onChange={e => setEdits((p: any) => ({ ...p, [key]: parseFloat(e.target.value) }))}
          className="w-32 bg-gray-900 border border-gray-700 text-gray-200 text-sm rounded px-2 py-1 focus:outline-none" />
        <span className="text-xs text-gray-500">{unit}</span>
      </div>
      <p className="text-xs text-gray-600 mt-1">{help}</p>
    </div>
  );

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-white">Settings</h1>
        <p className="text-gray-400 text-sm mt-1">Configure hardware assumptions for sustainability estimation and benchmark behavior.</p>
        <div className="mt-2 p-3 bg-blue-900/20 border border-blue-800 rounded-lg text-xs text-blue-300">
          ℹ These are prototype assumptions used for modeled sustainability estimates. They do not represent universal facts.
          Adjust them to match your hardware environment for more relevant estimates.
        </div>
      </div>

      {settings ? (
        <>
          <div className="card mb-6">
            <div className="text-sm font-medium text-gray-200 mb-1">AI Provider</div>
            <div className="text-sm text-green-400">{settings.ai_provider_status}</div>
            <p className="text-xs text-gray-500 mt-1">Configure IBM Granite via environment variables (see .env.example).</p>
          </div>

          <div className="card mb-6">
            <div className="text-sm font-medium text-gray-200 mb-4">Sustainability Assumptions</div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {field("cpu_tdp_watts", "CPU TDP", "Watts", "Estimated CPU Thermal Design Power. Default: 95W.")}
              {field("gpu_tdp_watts", "GPU TDP", "Watts", "Estimated GPU TDP (used only if GPU workloads are detected). Default: 250W.")}
              {field("grid_carbon_intensity", "Grid Carbon Intensity", "gCO2e/kWh", "Average grid carbon intensity. World avg ~475. EU ~250. Nordics ~50.")}
              {field("pue", "PUE", "multiplier", "Power Usage Effectiveness. 1.0 = ideal. Typical data center: 1.5. Cloud: 1.1–1.2.")}
              {field("cpu_utilization", "CPU Utilization Fraction", "0–1", "Fraction of CPU TDP attributed to this workload. Default: 0.5.")}
            </div>
          </div>

          <div className="card mb-6">
            <div className="text-sm font-medium text-gray-200 mb-4">Benchmark Settings</div>
            <div className="grid grid-cols-2 gap-3">
              {field("benchmark_timeout", "Timeout", "seconds", "Max seconds per benchmark run.")}
              {field("benchmark_runs", "Runs", "count", "Number of runs to average.")}
            </div>
          </div>

          <button onClick={save} disabled={saving} className="btn-primary">
            {saving ? "Saving…" : saved ? "✓ Saved" : "Save Settings"}
          </button>
        </>
      ) : <p className="text-gray-500">Loading settings…</p>}
    </div>
  );
}
