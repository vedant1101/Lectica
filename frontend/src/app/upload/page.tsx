"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";

const ACCEPTED = [
  "video/mp4", "video/quicktime", "video/webm",
  "audio/mpeg", "audio/wav", "audio/mp4",
  "image/jpeg", "image/png", "image/webp",
  "text/plain", "text/markdown", "application/pdf",
  ".txt", ".md", ".pdf", ".mp4", ".mp3", ".wav", ".jpg", ".png"
];

const FORMAT_HINTS = [
  { icon: "🎬", label: "Video" },
  { icon: "🎙", label: "Audio" },
  { icon: "🖼", label: "Images" },
  { icon: "📄", label: "PDF & Text" },
];

export default function UploadPage() {
  const router = useRouter();
  const [files, setFiles] = useState<File[]>([]);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    setFiles(prev => [...prev, ...Array.from(e.dataTransfer.files)]);
  }, []);

  const onFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files)
      setFiles(prev => [...prev, ...Array.from(e.target.files!)]);
  };

  const removeFile = (i: number) =>
    setFiles(prev => prev.filter((_, idx) => idx !== i));

  const getIcon = (file: File) => {
    if (file.type.startsWith("video")) return "🎬";
    if (file.type.startsWith("audio")) return "🎙";
    if (file.type.startsWith("image")) return "🖼";
    return "📄";
  };

  const handleSubmit = async () => {
    if (!files.length) return;
    setLoading(true);
    setError("");
    const form = new FormData();
    files.forEach(f => form.append("files", f));
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/sessions`,
        { method: "POST", body: form }
      );
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      router.push(`/sessions/${data.session_id}`);
    } catch (err: any) {
      setError(err.message || "Upload failed");
      setLoading(false);
    }
  };

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

          {/* Header */}
          <div className="mb-8">
            <h1 className="text-2xl font-semibold text-white tracking-tight mb-1">
              Upload your material
            </h1>
            <p className="text-gray-600 text-sm">
              Drop any lecture, podcast, slide, or note below
            </p>
          </div>

          {/* Drop zone */}
          <div
            onDrop={onDrop}
            onDragOver={e => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onClick={() => document.getElementById("file-input")?.click()}
            className={`relative rounded-2xl cursor-pointer transition-all duration-200 overflow-hidden
              ${dragging
                ? "border border-violet-500/50 bg-violet-500/5"
                : "border border-white/[0.08] bg-white/[0.02] hover:bg-white/[0.04] hover:border-white/[0.14]"
              }`}
          >
            <div className="px-8 py-14 text-center">
              <div className="flex justify-center gap-3 mb-6">
                {FORMAT_HINTS.map(f => (
                  <div
                    key={f.label}
                    className="flex flex-col items-center gap-1.5"
                  >
                    <span className="text-xl">{f.icon}</span>
                    <span className="text-[10px] text-gray-600">{f.label}</span>
                  </div>
                ))}
              </div>
              <p className="text-white text-sm font-medium mb-1">
                {dragging ? "Release to upload" : "Drop files here"}
              </p>
              <p className="text-gray-600 text-xs">
                or{" "}
                <span className="text-violet-400 underline underline-offset-2">
                  browse from your computer
                </span>
              </p>
            </div>
            <input
              id="file-input"
              type="file"
              multiple
              accept={ACCEPTED.join(",")}
              className="hidden"
              onChange={onFileInput}
            />
          </div>

          {/* File list */}
          {files.length > 0 && (
            <div className="mt-3 space-y-1.5">
              {files.map((f, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between px-4 py-3 bg-white/[0.03] border border-white/[0.07] rounded-xl group"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="text-base flex-shrink-0">{getIcon(f)}</span>
                    <div className="min-w-0">
                      <p className="text-white text-xs font-medium truncate">{f.name}</p>
                      <p className="text-gray-600 text-[10px] mt-0.5">
                        {(f.size / 1024 / 1024).toFixed(1)} MB
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => removeFile(i)}
                    className="text-gray-700 hover:text-red-400 transition-colors ml-4 flex-shrink-0 text-base leading-none"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Error */}
          {error && (
            <p className="mt-3 text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3">
              {error}
            </p>
          )}

          {/* Submit */}
          <button
            onClick={handleSubmit}
            disabled={loading || !files.length}
            className="mt-4 w-full py-3 rounded-xl text-sm font-medium transition-all duration-200
              bg-violet-600 hover:bg-violet-500 text-white
              disabled:bg-white/[0.04] disabled:text-gray-600 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="w-3.5 h-3.5 border border-white/30 border-t-white rounded-full animate-spin"></span>
                Uploading…
              </span>
            ) : (
              "Start studying →"
            )}
          </button>

          {files.length === 0 && (
            <p className="text-center text-gray-700 text-xs mt-4">
              Supports MP4, MP3, JPG, PNG, PDF, TXT and more
            </p>
          )}

        </div>
      </div>
    </main>
  );
}