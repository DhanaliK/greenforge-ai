"use client";

interface DiffViewerProps {
  before: string;
  after: string;
}

export default function DiffViewer({ before, after }: DiffViewerProps) {
  const beforeLines = before.split("\n");
  const afterLines  = after.split("\n");
  const maxLen = Math.max(beforeLines.length, afterLines.length);

  return (
    <div className="grid grid-cols-2 gap-2">
      {/* Before */}
      <div>
        <div className="text-xs text-red-400 font-semibold mb-1 px-1">◀ Original</div>
        <div className="bg-gray-950 border border-gray-800 rounded-lg overflow-auto max-h-96 font-mono text-xs leading-5">
          <pre className="p-3">
            {beforeLines.map((line, i) => {
              const isRemoved = afterLines[i] !== line;
              return (
                <div key={i} className={isRemoved ? "bg-red-900/30 border-l-2 border-red-600 pl-1" : ""}>
                  <span className="text-gray-600 mr-3 select-none">{i + 1}</span>
                  {line || " "}
                </div>
              );
            })}
          </pre>
        </div>
      </div>
      {/* After */}
      <div>
        <div className="text-xs text-green-400 font-semibold mb-1 px-1">▶ Optimized</div>
        <div className="bg-gray-950 border border-gray-800 rounded-lg overflow-auto max-h-96 font-mono text-xs leading-5">
          <pre className="p-3">
            {afterLines.map((line, i) => {
              const isAdded = beforeLines[i] !== line;
              return (
                <div key={i} className={isAdded ? "bg-green-900/30 border-l-2 border-green-600 pl-1" : ""}>
                  <span className="text-gray-600 mr-3 select-none">{i + 1}</span>
                  {line || " "}
                </div>
              );
            })}
          </pre>
        </div>
      </div>
    </div>
  );
}
