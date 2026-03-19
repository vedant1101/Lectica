"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";

interface Flashcard {
  id: string;
  question: string;
  answer: string;
  source_ref: string;
  ease_factor: number;
  interval: number;
}

export default function FlashcardsPage() {
  const { id } = useParams();
  const [cards, setCards] = useState<Flashcard[]>([]);
  const [index, setIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [loading, setLoading] = useState(true);
  const [done, setDone] = useState(false);
  const [animating, setAnimating] = useState(false);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/sessions/${id}/flashcards`)
      .then(r => r.json())
      .then(data => { setCards(data); setLoading(false); });
  }, [id]);

  const review = async (quality: number) => {
    await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/v1/sessions/${id}/flashcards/${cards[index].id}/review`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ quality }),
      }
    );
    setAnimating(true);
    setTimeout(() => {
      if (index + 1 >= cards.length) {
        setDone(true);
      } else {
        setIndex(i => i + 1);
        setFlipped(false);
        setAnimating(false);
      }
    }, 300);
  };

  const handleFlip = () => {
    if (animating) return;
    setFlipped(f => !f);
  };

  if (loading) return (
    <main className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
      <div className="flex items-center gap-3 text-gray-600 text-sm">
        <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse"></span>
        Loading flashcards…
      </div>
    </main>
  );

  if (done) return (
    <main className="min-h-screen bg-[#0a0a0a] flex flex-col items-center justify-center p-8">
      <div className="text-center" style={{ animation: "fadeUp 0.4s ease forwards" }}>
        <p className="text-5xl mb-8">✦</p>
        <h1 className="text-2xl font-semibold text-white mb-2 tracking-tight">
          Session complete
        </h1>
        <p className="text-gray-600 text-sm mb-10">
          You reviewed all {cards.length} cards.
        </p>
        <Link
          href={`/sessions/${id}`}
          className="text-sm text-violet-400 hover:text-violet-300 transition-colors underline underline-offset-4"
        >
          Back to session
        </Link>
      </div>
      <style>{`
        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(12px); }
          to   { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </main>
  );

  const card = cards[index];

  if (!card) return (
    <main className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
      <p className="text-gray-600 text-sm">No flashcards found.</p>
    </main>
  );

  const progress = ((index + 1) / cards.length) * 100;

  return (
    <main className="min-h-screen bg-[#0a0a0a] flex flex-col">
      <style>{`
        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(10px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes fadeOut {
          from { opacity: 1; transform: translateY(0); }
          to   { opacity: 0; transform: translateY(-10px); }
        }
        .card-enter { animation: fadeUp 0.3s ease forwards; }
        .card-exit  { animation: fadeOut 0.3s ease forwards; }
        .flip-enter { animation: fadeUp 0.2s ease forwards; }
      `}</style>

      {/* Nav */}
      <nav className="px-8 py-6 max-w-5xl mx-auto w-full flex items-center justify-between">
        <a href="/" className="text-white font-semibold text-lg tracking-tight">
          Lectica
        </a>
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
              Flashcards
            </p>
            <p className="text-[10px] text-gray-700">
              {index + 1} / {cards.length}
            </p>
          </div>

          {/* Progress bar */}
          <div className="w-full h-px bg-white/[0.05] mb-10 rounded-full overflow-hidden">
            <div
              className="h-full bg-violet-500/60 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>

          {/* Card */}
          <div
            onClick={handleFlip}
            className={`rounded-2xl border cursor-pointer min-h-60 flex flex-col items-center justify-center px-10 py-14 text-center mb-5 transition-colors duration-200
              ${animating ? "card-exit" : "card-enter"}
              ${flipped
                ? "bg-white/[0.04] border-white/[0.10]"
                : "bg-white/[0.02] border-white/[0.06] hover:border-white/[0.11] hover:bg-white/[0.035]"
              }`}
          >
            <p className="text-[9px] text-gray-700 uppercase tracking-[0.2em] mb-6">
              {flipped ? "Answer" : "Question"}
            </p>

            <p
              key={`${index}-${flipped}`}
              className="text-white text-lg font-medium leading-relaxed flip-enter"
            >
              {flipped ? card.answer : card.question}
            </p>

            {!flipped && (
              <p className="text-gray-700 text-[10px] mt-8 tracking-wide">
                click to reveal
              </p>
            )}
          </div>

          {/* Source */}
          {card.source_ref && (
            <p className="text-[10px] text-gray-700 text-center mb-5 truncate">
              {card.source_ref}
            </p>
          )}

          {/* Rating */}
          {flipped && (
            <div
              className="grid grid-cols-3 gap-2"
              style={{ animation: "fadeUp 0.25s ease forwards" }}
            >
              {[
                { label: "Hard", quality: 1, color: "hover:text-red-400 hover:border-red-500/20 hover:bg-red-500/5" },
                { label: "Good", quality: 3, color: "hover:text-amber-400 hover:border-amber-500/20 hover:bg-amber-500/5" },
                { label: "Easy", quality: 5, color: "hover:text-emerald-400 hover:border-emerald-500/20 hover:bg-emerald-500/5" },
              ].map((btn) => (
                <button
                  key={btn.label}
                  onClick={() => review(btn.quality)}
                  className={`py-3 rounded-xl text-[11px] font-medium transition-all duration-150
                    bg-white/[0.02] border border-white/[0.07] text-gray-500
                    ${btn.color}`}
                >
                  {btn.label}
                </button>
              ))}
            </div>
          )}

        </div>
      </div>
    </main>
  );
}