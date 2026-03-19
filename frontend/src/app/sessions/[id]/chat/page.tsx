"use client";

import { useState, useRef, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const SUGGESTIONS = [
  "Give me an overview",
  "What are the key concepts?",
  "Summarize the main points",
  "What should I focus on?",
];

const cleanContent = (text: string) =>
  text.replace(/\[source_ref:[^\]]*\]/g, "").replace(/\s+/g, " ").trim();

export default function ChatPage() {
  const { id } = useParams();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (text?: string) => {
    const question = text || input;
    if (!question.trim() || loading) return;

    const userMsg: Message = { role: "user", content: question };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    const assistantMsg: Message = { role: "assistant", content: "" };
    setMessages(prev => [...prev, assistantMsg]);

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/sessions/${id}/chat`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: question, history: messages }),
        }
      );

      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let full = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const text = decoder.decode(value);
        for (const line of text.split("\n")) {
          if (line.startsWith("data: ")) {
            const chunk = line.slice(6);
            if (chunk === "[DONE]") break;
            if (!chunk.startsWith("__sources__")) {
              full += chunk;
              setMessages(prev => [
                ...prev.slice(0, -1),
                { role: "assistant", content: full },
              ]);
            }
          }
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  return (
    <main className="h-screen bg-[#0a0a0a] flex flex-col overflow-hidden">
      <style>{`
        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(8px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        .msg { animation: fadeUp 0.25s ease forwards; }
        @keyframes blink {
          0%, 100% { opacity: 1; }
          50%       { opacity: 0; }
        }
        .cursor { display: inline-block; width: 1.5px; height: 13px; background: currentColor; margin-left: 1px; vertical-align: middle; animation: blink 1s step-end infinite; }
      `}</style>

      {/* Nav */}
      <nav className="px-8 py-6 max-w-5xl mx-auto w-full flex items-center justify-between flex-shrink-0">
        <a href="/" className="text-white font-semibold text-lg tracking-tight">Lectica</a>
        <Link
          href={`/sessions/${id}`}
          className="text-gray-600 hover:text-gray-400 text-sm transition-colors"
        >
          ← Back
        </Link>
      </nav>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-8 pb-6">
        <div className="max-w-2xl mx-auto">

          {messages.length === 0 && (
            <div className="pt-16 pb-10 text-center">
              <p className="text-3xl mb-6">✦</p>
              <p className="text-white text-lg font-medium mb-1 tracking-tight">
                Ask anything
              </p>
              <p className="text-gray-600 text-sm mb-10">
                Chat with your study material
              </p>
              <div className="grid grid-cols-2 gap-2">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    onClick={() => send(s)}
                    className="text-left px-4 py-3 bg-white/[0.03] border border-white/[0.07] rounded-xl text-gray-500 text-xs hover:bg-white/[0.06] hover:text-gray-300 hover:border-white/[0.12] transition-all duration-150"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="space-y-6 pt-4">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`msg flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {msg.role === "assistant" && (
                  <div className="w-5 h-5 rounded-full bg-violet-500/20 border border-violet-500/30 flex-shrink-0 mt-1 mr-3 flex items-center justify-center">
                    <span className="text-[8px] text-violet-400">✦</span>
                  </div>
                )}
                <div
                  className={`max-w-sm text-sm leading-relaxed
                    ${msg.role === "user"
                      ? "bg-white/[0.06] border border-white/[0.09] text-gray-200 px-4 py-3 rounded-2xl rounded-tr-sm"
                      : "text-gray-400"
                    }`}
                >
                  {msg.content
                    ? cleanContent(msg.content)
                    : loading && i === messages.length - 1
                    ? <span className="text-gray-600">Thinking<span className="cursor" /></span>
                    : null
                  }
                </div>
              </div>
            ))}
          </div>

          <div ref={bottomRef} className="h-4" />
        </div>
      </div>

      {/* Input */}
      <div className="flex-shrink-0 px-8 pb-8 pt-4 border-t border-white/[0.05]">
        <div className="max-w-2xl mx-auto flex gap-2">
          <input
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && send()}
            placeholder="Ask a question…"
            className="flex-1 bg-white/[0.03] border border-white/[0.08] rounded-xl px-4 py-3 text-sm text-white placeholder-gray-700 focus:outline-none focus:border-white/[0.16] transition-colors"
          />
          <button
            onClick={() => send()}
            disabled={!input.trim() || loading}
            className="px-5 py-3 rounded-xl text-sm font-medium transition-all duration-150
              bg-violet-600 hover:bg-violet-500 text-white
              disabled:bg-white/[0.03] disabled:text-gray-700 disabled:border disabled:border-white/[0.07]"
          >
            Send
          </button>
        </div>
      </div>

    </main>
  );
}