"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";

interface Session {
  id: string;
  status: string;
  title: string | null;
  created_at: string;
}

const MODES = [
  {
    href: "flashcards",
    icon: "📇",
    title: "Flashcards",
    desc: "Review with spaced repetition",
  },
  {
    href: "quiz",
    icon: "📝",
    title: "Quiz",
    desc: "Test your understanding",
  },
  {
    href: "summary",
    icon: "📋",
    title: "Summary",
    desc: "Key concepts at a glance",
  },
  {
    href: "chat",
    icon: "💬",
    title: "Ask anything",
    desc: "Chat with your material",
  },
];

export default function SessionPage() {
  const { id } = useParams();
  const [session, setSession] = useState<Session | null>(null);
  const [polling, setPolling] = useState(true);

  useEffect(() => {
    if (!polling) return;
    const interval = setInterval(async () => {
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/v1/sessions/${id}`
        );
        const data = await res.json();
        setSession(data);
        if (data.status === "done" || data.status === "failed") {
          setPolling(false);
        }
      } catch (err) {
        console.error(err);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [id, polling]);

  if (!session) return (
    <main className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
      <div className="flex items-center gap-3 text-gray-600 text-sm">
        <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse"></span>
        Loading…
      </div>
    </main>
  );

  return (
    <main className="min-h-screen bg-[#0a0a0a] flex flex-col">

      {/* Nav */}
      <nav className="px-8 py-6 max-w-5xl mx-auto w-full">
        <a href="/" className="text-white font-semibold text-lg tracking-tight">
          Lectica
        </a>
      </nav>

      <div className="flex-1 flex flex-col items-center justify-center px-8 pb-16">
        <div className="max-w-lg w-full">

          {session.status !== "done" && session.status !== "failed" && (
            <div className="text-center">
              <div className="w-10 h-10 rounded-full border border-violet-500/40 border-t-violet-400 animate-spin mx-auto mb-6"></div>
              <h1 className="text-xl font-semibold text-white mb-2 tracking-tight">
                Processing your material
              </h1>
              <p className="text-gray-600 text-sm">
                This usually takes 10–30 seconds…
              </p>
            </div>
          )}

          {session.status === "failed" && (
            <div className="text-center">
              <p className="text-white text-lg font-medium mb-4">Something went wrong</p>
              <Link href="/upload" className="text-violet-400 text-sm underline underline-offset-2">
                Try again
              </Link>
            </div>
          )}

          {session.status === "done" && (
            <div>
              <div className="mb-8">
                <div className="inline-flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 rounded-full px-3 py-1 mb-4">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                  <span className="text-xs text-emerald-400 font-medium">Ready to study</span>
                </div>
                <h1 className="text-2xl font-semibold text-white tracking-tight">
                  What would you like to do?
                </h1>
              </div>

              <div className="space-y-2">
                {MODES.map((mode) => (
                  <Link
                    key={mode.href}
                    href={`/sessions/${id}/${mode.href}`}
                    className="flex items-center justify-between px-5 py-4 bg-white/[0.03] border border-white/[0.08] rounded-2xl hover:bg-white/[0.06] hover:border-white/[0.14] transition-all duration-200 group"
                  >
                    <div className="flex items-center gap-4">
                      <span className="text-xl">{mode.icon}</span>
                      <div>
                        <p className="text-white text-sm font-medium">{mode.title}</p>
                        <p className="text-gray-600 text-xs mt-0.5">{mode.desc}</p>
                      </div>
                    </div>
                    <span className="text-gray-700 group-hover:text-gray-400 transition-colors text-sm">
                      →
                    </span>
                  </Link>
                ))}
              </div>
            </div>
          )}

        </div>
      </div>
    </main>
  );
}