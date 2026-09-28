"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const nav = [
  { href: "/",           label: "Dashboard",        icon: "⬡" },
  { href: "/green-code", label: "Green Code",        icon: "⟨⟩" },
  { href: "/green-ai",   label: "Green AI Lab",      icon: "🧠" },
  { href: "/benchmarks", label: "Benchmarks",        icon: "⏱" },
  { href: "/rag",        label: "RAG Knowledge",     icon: "📚" },
  { href: "/copilot",    label: "GF Copilot",        icon: "💬" },
  { href: "/reports",    label: "Reports",           icon: "📄" },
  { href: "/settings",   label: "Settings",          icon: "⚙" },
  { href: "/about",      label: "About",             icon: "ℹ" },
];

export default function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-gray-900 border-r border-gray-800 flex flex-col z-40">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-green-500 to-emerald-700 flex items-center justify-center text-white font-bold text-sm">GF</div>
          <div>
            <div className="font-bold text-green-400 text-sm leading-tight">GreenForge AI</div>
            <div className="text-gray-500 text-xs leading-tight">Sustainable Dev Tools</div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {nav.map((item) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                active
                  ? "bg-green-900/50 text-green-300 border border-green-800/60"
                  : "text-gray-400 hover:text-gray-200 hover:bg-gray-800"
              }`}
            >
              <span className="text-base w-5 text-center">{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-gray-800">
        <p className="text-xs text-gray-600 leading-tight">Forge more efficient code.</p>
        <p className="text-xs text-gray-600">Build greener AI.</p>
      </div>
    </aside>
  );
}
