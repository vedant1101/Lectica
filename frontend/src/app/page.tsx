import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen bg-[#0a0a0a] flex flex-col">

      {/* Nav */}
      <nav className="flex items-center justify-between px-8 py-6 max-w-5xl mx-auto w-full">
        <span className="text-white font-semibold text-lg tracking-tight">Lectica</span>
        <Link
          href="/upload"
          className="text-sm text-gray-500 hover:text-white transition-colors"
        >
          Get started →
        </Link>
      </nav>

      {/* Hero */}
      <section className="flex-1 flex flex-col items-center justify-center px-8 text-center max-w-3xl mx-auto w-full py-24">
        <div className="inline-flex items-center gap-2 bg-white/5 border border-white/10 rounded-full px-4 py-1.5 mb-10">
          <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse"></span>
          <span className="text-xs text-gray-400 font-medium">AI-powered multimodal learning</span>
        </div>

        <h1 className="text-6xl md:text-7xl font-bold text-white mb-6 leading-tight tracking-tight">
          Turn any lecture into
          <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-purple-300">
            a study companion
          </span>
        </h1>

        <p className="text-base text-gray-500 mb-12 max-w-lg leading-relaxed">
          Upload videos, audio, images, or text. Lectica extracts key concepts and generates flashcards, quizzes, summaries, and answers your questions — instantly.
        </p>

        <Link
          href="/upload"
          className="bg-violet-600 hover:bg-violet-500 text-white font-medium px-8 py-3 rounded-xl transition-colors text-sm"
        >
          Start studying →
        </Link>
      </section>

      {/* Bottom section */}
      <section className="max-w-5xl mx-auto w-full px-8 pb-24 grid grid-cols-1 md:grid-cols-2 gap-16">

        {/* Supported formats */}
        <div>
          <p className="text-xs text-gray-600 uppercase tracking-widest font-medium mb-6">
            Supported formats
          </p>
          <div className="space-y-5">
            {[
              { icon: "🎬", label: "Video lectures",   desc: "Transcript + keyframes extracted automatically" },
              { icon: "🎙", label: "Audio & podcasts", desc: "Transcribed and chunked with Whisper" },
              { icon: "🖼", label: "Slides & images",  desc: "Vision AI reads every diagram and text" },
              { icon: "📄", label: "PDFs & notes",     desc: "Semantic chunking for deep understanding" },
            ].map((item) => (
              <div key={item.label} className="flex items-start gap-4">
                <span className="text-lg mt-0.5">{item.icon}</span>
                <div>
                  <p className="text-white text-sm font-medium">{item.label}</p>
                  <p className="text-gray-600 text-xs mt-0.5">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Features */}
        <div>
          <p className="text-xs text-gray-600 uppercase tracking-widest font-medium mb-6">
            What you get
          </p>
          <div className="space-y-5">
            {[
              { icon: "📇", label: "Flashcards", desc: "Auto-generated with spaced repetition (SM-2)" },
              { icon: "📝", label: "Quiz",        desc: "Multiple choice questions from your material" },
              { icon: "📋", label: "Summary",     desc: "Key concepts extracted and organised" },
              { icon: "💬", label: "AI Chat",     desc: "RAG-powered answers grounded in your content" },
            ].map((item) => (
              <div key={item.label} className="flex items-start gap-4">
                <span className="text-lg mt-0.5">{item.icon}</span>
                <div>
                  <p className="text-white text-sm font-medium">{item.label}</p>
                  <p className="text-gray-600 text-xs mt-0.5">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

      </section>

    </main>
  );
}