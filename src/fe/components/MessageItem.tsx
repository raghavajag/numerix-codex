"use client";

import { VideoModal } from "@/components/VideoModal";

export type ChatMessage = {
  id: string;
  text: string;
  timestamp: string;
  videoUrl?: string;
  isResponse?: boolean;
  isLoading?: boolean;
  isError?: boolean;
};

export function MessageItem({ message }: { message: ChatMessage }) {
  const bubbleStyle = message.isResponse
    ? "bg-slate-900/90 border-white/10"
    : "bg-cyan-500/15 border-cyan-400/30";

  return (
    <div className={`flex ${message.isResponse ? "justify-start" : "justify-end"}`}>
      <div className={`max-w-3xl rounded-3xl border px-4 py-3 shadow-lg ${bubbleStyle}`}>
        <p className="mb-2 text-sm leading-6 text-slate-100">
          {message.isLoading ? "Generating your animation..." : message.text}
        </p>
        <div className="flex items-center justify-between gap-3">
          <span className="text-xs text-slate-400">{message.timestamp}</span>
          {message.videoUrl ? (
            <VideoModal
              url={message.videoUrl}
              trigger={
                <button className="rounded-full bg-emerald-400 px-3 py-1 text-xs font-semibold text-slate-950 transition hover:bg-emerald-300">
                  Play video
                </button>
              }
            />
          ) : null}
          {message.isError ? (
            <span className="text-xs font-medium text-rose-300">Error</span>
          ) : null}
        </div>
      </div>
    </div>
  );
}
