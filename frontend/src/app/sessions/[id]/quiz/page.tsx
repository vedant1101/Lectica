"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";

interface Question {
  question: string;
  options: string[];
  correct_index: number;
  explanation: string;
}

export default function QuizPage() {
  const { id } = useParams();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [index, setIndex] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [score, setScore] = useState(0);
  const [done, setDone] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/sessions/${id}/quiz?n=5`)
      .then(r => r.json())
      .then(data => { setQuestions(data.questions); setLoading(false); });
  }, [id]);

  const handleSelect = (i: number) => {
    if (selected !== null) return;
    setSelected(i);
    if (i === questions[index].correct_index) setScore(s => s + 1);
  };

  const next = () => {
    if (index + 1 >= questions.length) {
      setDone(true);
    } else {
      setIndex(i => i + 1);
      setSelected(null);
    }
  };

  if (loading) return (
    <main className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
      <div className="flex items-center gap-3 text-gray-600 text-sm">
        <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse"></span>
        Generating quiz…
      </div>
    </main>
  );

  if (done) return (
    <main className="min-h-screen bg-[#0a0a0a] flex flex-col items-center justify-center p-8">
      <style>{`
        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(12px); }
          to   { opacity: 1; transform: translateY(0); }
        }
      `}</style>
      <div className="text-center" style={{ animation: "fadeUp 0.4s ease forwards" }}>
        <p className="text-5xl mb-8">✦</p>
        <h1 className="text-2xl font-semibold text-white mb-2 tracking-tight">
          Quiz complete
        </h1>
        <p className="text-violet-400 text-4xl font-bold mt-6 mb-2">
          {score}<span className="text-gray-700 text-2xl"> / {questions.length}</span>
        </p>
        <p className="text-gray-600 text-sm mt-3 mb-10">
          {score === questions.length
            ? "Perfect — you nailed it."
            : score >= questions.length / 2
            ? "Good effort — keep reviewing."
            : "Keep studying, you'll get there."}
        </p>
        <Link
          href={`/sessions/${id}`}
          className="text-sm text-violet-400 hover:text-violet-300 transition-colors underline underline-offset-4"
        >
          Back to session
        </Link>
      </div>
    </main>
  );

  const q = questions[index];
  const progress = ((index + 1) / questions.length) * 100;

  return (
    <main className="min-h-screen bg-[#0a0a0a] flex flex-col">
      <style>{`
        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(10px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        .fade-up { animation: fadeUp 0.3s ease forwards; }
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

      <div className="flex-1 flex flex-col items-center justify-center px-8 pb-16">
        <div className="max-w-lg w-full">

          {/* Header */}
          <div className="flex items-center justify-between mb-5">
            <p className="text-[10px] text-gray-700 uppercase tracking-widest font-medium">
              Quiz
            </p>
            <p className="text-[10px] text-gray-700">
              {index + 1} / {questions.length}
            </p>
          </div>

          {/* Progress bar */}
          <div className="w-full h-px bg-white/[0.05] mb-10 rounded-full overflow-hidden">
            <div
              className="h-full bg-violet-500/60 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>

          {/* Question */}
          <p
            key={index}
            className="text-white text-lg font-medium leading-relaxed mb-8 fade-up"
          >
            {q.question}
          </p>

          {/* Options */}
          <div className="space-y-2 mb-6">
            {q.options.map((opt, i) => {
              let style = "bg-white/[0.02] border-white/[0.07] text-gray-400 hover:bg-white/[0.04] hover:border-white/[0.12] hover:text-white cursor-pointer";
              if (selected !== null) {
                if (i === q.correct_index)
                  style = "bg-emerald-500/10 border-emerald-500/30 text-emerald-400 cursor-default";
                else if (i === selected)
                  style = "bg-red-500/10 border-red-500/30 text-red-400 cursor-default";
                else
                  style = "bg-white/[0.01] border-white/[0.04] text-gray-700 cursor-default";
              }

              return (
                <button
                  key={i}
                  onClick={() => handleSelect(i)}
                  className={`w-full text-left px-5 py-3.5 rounded-xl border text-sm transition-all duration-150 ${style}`}
                >
                  <span className="text-[10px] text-gray-700 mr-3 font-mono">
                    {String.fromCharCode(65 + i)}
                  </span>
                  {opt}
                </button>
              );
            })}
          </div>

          {/* Explanation */}
          {selected !== null && (
            <div
              className="bg-white/[0.02] border border-white/[0.07] rounded-xl px-5 py-4 mb-5 fade-up"
            >
              <p className="text-[10px] text-gray-700 uppercase tracking-widest mb-2">
                Explanation
              </p>
              <p className="text-gray-400 text-sm leading-relaxed">
                {q.explanation}
              </p>
            </div>
          )}

          {/* Next */}
          {selected !== null && (
            <button
              onClick={next}
              className="w-full py-3 rounded-xl text-sm font-medium transition-all duration-150
                bg-violet-600 hover:bg-violet-500 text-white fade-up"
            >
              {index + 1 >= questions.length ? "See results" : "Next →"}
            </button>
          )}

        </div>
      </div>
    </main>
  );
}