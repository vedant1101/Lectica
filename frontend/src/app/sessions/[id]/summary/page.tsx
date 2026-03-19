"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";

interface Summary {
  title: string;
  key_concepts: string[];
  summary: string;
}

export default function SummaryPage() {
  const { id } = useParams();
  const [summary, setSummary] = useState<Summary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/sessions/${id}/summary`)
      .then(r => r.json())
      .then(data => { setSummary(data); setLoading(false); });
  }, [id]);

  if (loading) return (
    <main className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
      <div className="flex items-center gap-3 text-gray-600 text-sm">
        <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse"></span>
        Generating summary…
      </div>
    </main>
  );

  if (!summary) return null;

  return (
    <main className="min-h-screen bg-[#0a0a0a] flex flex-col">
      <style>{`
        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(12px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        .f0 { animation: fadeUp 0.4s ease 0s both; }
        .f1 { animation: fadeUp 0.4s ease 0.1s both; }
        .f2 { animation: fadeUp 0.4s ease 0.2s both; }
      `}</style>

      {/* Nav */}
      <nav className="px-8 py-6 max-w-5xl mx-auto w-full flex items-center justify-between">
        <a href="/" className="text-white font-semibold text-lg tracking-tight">Lectica</a>
        <Link
          href={`/sessions/${id}`}
          className="text-gray-600 hover:text-gray-400 text-sm transition-colors"
        >
          ← Back
        </Link>
      </nav>

      <div className="flex-1 max-w-2xl mx-auto w-full px-8 pt-6 pb-24">

        {/* Title */}
        <div className="f0 mb-12">
          <p className="text-[10px] text-gray-700 uppercase tracking-widest mb-3">
            Summary
          </p>
          <h1 className="text-3xl font-semibold text-white tracking-tight leading-snug">
            {summary.title}
          </h1>
        </div>

        {/* Key concepts */}
        <div className="f1 mb-10">
          <p className="text-[10px] text-gray-700 uppercase tracking-widest mb-5">
            Key concepts
          </p>
          <div className="space-y-1">
            {summary.key_concepts.map((concept, i) => (
              <div
                key={i}
                className="flex items-center gap-3 py-2.5 border-b border-white/[0.05]"
              >
                <span className="text-violet-500/60 text-xs font-mono">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <span className="text-gray-300 text-sm">{concept}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Summary text */}
        <div className="f2">
          <p className="text-[10px] text-gray-700 uppercase tracking-widest mb-5">
            Overview
          </p>
          <div className="border-l border-violet-500/20 pl-5">
            <p className="text-gray-400 text-sm leading-[1.95] whitespace-pre-wrap">
              {summary.summary}
            </p>
          </div>
        </div>

      </div>
    </main>
  );
}