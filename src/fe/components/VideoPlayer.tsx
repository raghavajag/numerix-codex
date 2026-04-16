"use client";

import ReactPlayer from "react-player";

export function VideoPlayer({ url }: { url: string }) {
  return (
    <div className="overflow-hidden rounded-2xl border border-white/10 bg-slate-900">
      <ReactPlayer
        controls
        height="100%"
        url={url}
        width="100%"
      />
    </div>
  );
}
