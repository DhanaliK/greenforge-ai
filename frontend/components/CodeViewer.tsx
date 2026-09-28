"use client";
import { useEffect, useRef } from "react";

interface Props {
  code: string;
  language?: string;
  height?: number;
}

/* Lightweight syntax-highlighted code viewer (no Monaco needed) */
export default function CodeViewer({ code, language = "python", height = 300 }: Props) {
  return (
    <div
      className="bg-gray-950 border border-gray-800 rounded-lg overflow-auto font-mono text-xs leading-5"
      style={{ maxHeight: height, minHeight: 80 }}
    >
      <pre className="p-4 whitespace-pre-wrap break-all">
        {highlightPython(code, language)}
      </pre>
    </div>
  );
}

function highlightPython(code: string, lang: string): React.ReactNode {
  // Simple keyword highlighting without external deps
  const lines = code.split("\n");
  return lines.map((line, i) => (
    <div key={i} className="flex">
      <span className="select-none text-gray-600 mr-4 w-8 text-right shrink-0">{i + 1}</span>
      <span dangerouslySetInnerHTML={{ __html: colorize(line, lang) }} />
    </div>
  ));
}

function colorize(line: string, lang: string): string {
  if (lang !== "python") return escHtml(line);
  return escHtml(line)
    .replace(/(#.*)$/, '<span class="text-gray-500">$1</span>')
    .replace(
      /\b(def|class|import|from|return|if|else|elif|for|while|in|not|and|or|True|False|None|with|as|try|except|raise|lambda|yield|pass|break|continue|async|await)\b/g,
      '<span class="text-purple-400">$1</span>'
    )
    .replace(/\b(\d+\.?\d*)\b/g, '<span class="text-yellow-300">$1</span>')
    .replace(/(&quot;[^&]*&quot;|&#39;[^&]*&#39;)/g, '<span class="text-green-300">$1</span>');
}

function escHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}
