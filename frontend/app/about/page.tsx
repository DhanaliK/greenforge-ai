export default function AboutPage() {
  const Section = ({ title, children }: { title: string; children: React.ReactNode }) => (
    <div className="card mb-4">
      <h2 className="text-sm font-bold text-green-400 uppercase tracking-wider mb-3">{title}</h2>
      {children}
    </div>
  );

  return (
    <div className="p-8 max-w-4xl mx-auto">
      {/* Hero */}
      <div className="flex items-center gap-4 mb-8">
        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-green-500 to-emerald-700 flex items-center justify-center text-white font-bold text-xl">GF</div>
        <div>
          <h1 className="text-2xl font-bold text-white">GreenForge AI</h1>
          <p className="text-green-400">Agentic AI for Sustainable Software &amp; Machine Learning</p>
          <p className="text-gray-500 text-sm italic mt-0.5">"Forge more efficient code. Build greener AI."</p>
        </div>
      </div>

      <Section title="Problem Statement">
        <p className="text-sm text-gray-300 leading-6">
          Software is typically optimized for correctness, speed, and cost — but rarely for sustainability.
          Inefficient algorithms, repeated computation, excessive memory use, redundant I/O, and non-batched ML inference
          can increase resource consumption, yet developers lack visibility into these inefficiencies during everyday coding.
        </p>
        <p className="text-sm text-gray-300 leading-6 mt-2">
          GreenForge AI bridges this gap by combining static code analysis, computational complexity analysis,
          runtime benchmarking, AI-assisted optimization, and transparent sustainability estimation — surfacing
          efficiency insights at development time.
        </p>
      </Section>

      <Section title="SDG Alignment">
        <div className="space-y-2">
          {[
            { sdg: "SDG 12 — Responsible Consumption and Production", role: "Primary", desc: "Reduce computational waste and promote efficient resource usage in software development." },
            { sdg: "SDG 13 — Climate Action", role: "Secondary", desc: "Contribute to lower ICT sector emissions through developer-facing sustainability tools." },
            { sdg: "SDG 9 — Industry, Innovation and Infrastructure", role: "Secondary", desc: "Foster sustainable innovation in software engineering tooling and AI systems." },
          ].map(({ sdg, role, desc }) => (
            <div key={sdg} className="p-3 bg-gray-800 rounded-lg">
              <div className="flex items-center gap-2">
                <span className="text-green-300 font-medium text-sm">{sdg}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full ${role === "Primary" ? "bg-green-900/50 text-green-400" : "bg-gray-700 text-gray-400"}`}>{role}</span>
              </div>
              <p className="text-xs text-gray-500 mt-1">{desc}</p>
            </div>
          ))}
        </div>
      </Section>

      <Section title="Core Engines">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {[
            { name: "Green Code Engine", desc: "Python/JS AST-based static analysis detecting 20+ inefficiency patterns (nested loops, repeated I/O, ML anti-patterns, string concatenation, etc.)." },
            { name: "Green AI Lab (EcoML)", desc: "ML workload benchmarking: model size, inference latency, memory, batching analysis, model comparison with accuracy/efficiency trade-off view." },
            { name: "Benchmark Engine", desc: "Safe subprocess isolation with timeout, CPU time, memory tracing. Generates before/after comparisons. Refuses to accept regressions." },
            { name: "Sustainability Engine", desc: "Translates benchmark measurements into modeled energy/carbon estimates using configurable CPU TDP, PUE, and grid carbon intensity." },
            { name: "GreenForge Score", desc: "Transparent 0–100 composite score across 7 dimensions with documented methodology. Not an industry certification." },
            { name: "RAG Knowledge System", desc: "TF-IDF retrieval over curated green software knowledge base. Grounded answers with source attribution." },
          ].map(({ name, desc }) => (
            <div key={name} className="p-3 bg-gray-800 rounded-lg">
              <div className="text-sm font-medium text-blue-300 mb-1">{name}</div>
              <p className="text-xs text-gray-400 leading-5">{desc}</p>
            </div>
          ))}
        </div>
      </Section>

      <Section title="AI Technology Stack">
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {[
            ["IBM Granite", "Primary generative AI provider via watsonx.ai"],
            ["Agentic AI", "8-agent orchestration pipeline"],
            ["RAG", "TF-IDF retrieval + knowledge base"],
            ["Static Analysis", "Python AST + complexity metrics"],
            ["Benchmarking", "Subprocess isolation + resource tracking"],
            ["Local Fallback", "Deterministic templates when offline"],
          ].map(([name, desc]) => (
            <div key={name as string} className="p-2 bg-gray-800 rounded text-xs">
              <div className="text-green-300 font-medium">{name}</div>
              <div className="text-gray-500 mt-0.5">{desc}</div>
            </div>
          ))}
        </div>
      </Section>

      <Section title="Development Technology">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {[
            ["IBM Bob", "AI-assisted development environment used to implement this project"],
            ["Next.js 15", "React framework for the frontend"],
            ["TypeScript", "Frontend language"],
            ["Tailwind CSS", "Utility-first styling"],
            ["Python 3.12", "Backend language"],
            ["FastAPI", "Backend API framework"],
            ["SQLite", "Local persistence"],
            ["Recharts", "Data visualization"],
          ].map(([name, desc]) => (
            <div key={name as string} className="p-2 bg-gray-800 rounded text-xs">
              <div className="text-purple-300 font-medium">{name}</div>
              <div className="text-gray-500 mt-0.5">{desc}</div>
            </div>
          ))}
        </div>
        <p className="text-xs text-gray-600 mt-3">
          <strong className="text-gray-400">Note:</strong> IBM Bob is the AI-assisted development environment used to implement GreenForge AI.
          IBM Granite is the generative AI component embedded inside the product for code optimization, RAG, and copilot features.
        </p>
      </Section>

      <Section title="Responsible AI">
        <div className="space-y-2 text-xs text-gray-400 leading-5">
          {[
            ["Transparency", "All findings show their source (static analysis vs AI-suggested), confidence level, and methodology."],
            ["Human Oversight", "All AI suggestions must be reviewed and benchmarked before adoption."],
            ["Accuracy", "Sustainability estimates are clearly labeled as modeled — not validated measurements."],
            ["Privacy", "Code is not sent to external AI unless IBM Granite is explicitly configured."],
            ["Fairness", "GreenForge scores code and workloads — never developers or individuals."],
            ["Limitations", "Source-level analysis cannot perfectly predict real-world environmental impact."],
          ].map(([k, v]) => (
            <div key={k as string} className="flex gap-2">
              <span className="text-green-400 font-medium min-w-[110px]">{k}:</span>
              <span>{v}</span>
            </div>
          ))}
        </div>
      </Section>

      <div className="card border-gray-800 text-center">
        <p className="text-xs text-gray-600">
          GreenForge AI is a student innovation prototype. It is not an industry-certified sustainability tool
          and does not provide validated carbon reduction claims. Built with IBM Bob · IBM Granite · FastAPI · Next.js
        </p>
      </div>
    </div>
  );
}
