"use client";
import { useState } from "react";
import { apiClient } from "@/lib/api";

interface Msg { role: "user" | "assistant"; content: string; }

const SUGGESTIONS = [
  "Why was this function flagged as inefficient?",
  "What is the biggest optimization opportunity?",
  "Explain the sustainability estimate methodology.",
  "What trade-offs does the optimization introduce?",
  "How can I improve this ML model's inference efficiency?",
  "What assumptions were used for the energy estimate?",
];

export default function CopilotPage() {
  const [messages, setMessages] = useState<Msg[]>([
    { role: "assistant", content: "Hi! I'm GreenForge Copilot. Ask me anything about your code analysis, benchmark results, sustainability estimates, or green software practices." }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const send = async (msg?: string) => {
    const text = (msg || input).trim();
    if (!text) return;
    const newMsgs: Msg[] = [...messages, { role: "user", content: text }];
    setMessages(newMsgs);
    setInput("");
    setLoading(true);
    try {
      const history = newMsgs.slice(-8).map(m => ({ role: m.role, content: m.content }));
      const res = await apiClient.copilotChat(text, history.slice(0, -1));
      setMessages(m => [...m, { role: "assistant", content: res.reply }]);
    } catch (e: any) {
      setMessages(m => [...m, { role: "assistant", content: `Error: ${e.message}` }]);
    } finally { setLoading(false); }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto flex flex-col h-[calc(100vh-4rem)]">
      <div className="mb-4">
        <h1 className="text-xl font-bold text-white">GreenForge Copilot</h1>
        <p className="text-gray-400 text-sm">Contextual AI assistant for sustainability, code analysis and optimization guidance.</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-3 mb-4">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-6 ${
              m.role === "user"
                ? "bg-green-700/60 text-white"
                : "bg-gray-800 text-gray-200"
            }`}>
              {m.role === "assistant" && (
                <div className="text-xs text-green-400 font-medium mb-1">GreenForge Copilot</div>
              )}
              <div className="whitespace-pre-wrap">{m.content}</div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-800 rounded-2xl px-4 py-3 text-sm text-gray-400">
              <div className="text-xs text-green-400 mb-1">GreenForge Copilot</div>
              Thinking…
            </div>
          </div>
        )}
      </div>

      {/* Suggestions */}
      <div className="flex flex-wrap gap-2 mb-3">
        {SUGGESTIONS.map(s => (
          <button key={s} onClick={() => send(s)}
            className="text-xs bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-gray-200 px-2 py-1 rounded border border-gray-700">
            {s}
          </button>
        ))}
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <input
          value={input} onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && !e.shiftKey && send()}
          placeholder="Ask about your analysis, benchmarks, sustainability…"
          className="flex-1 bg-gray-800 border border-gray-700 text-gray-200 text-sm rounded-xl px-4 py-3 focus:outline-none focus:border-green-600"
        />
        <button onClick={() => send()} disabled={loading || !input.trim()} className="btn-primary px-6">
          Send
        </button>
      </div>
    </div>
  );
}
