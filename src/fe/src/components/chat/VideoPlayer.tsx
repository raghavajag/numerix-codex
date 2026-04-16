import { useState } from "react";
import { Maximize, Pause, Play, Volume2, VolumeX } from "lucide-react";

import { Button } from "@/components/ui/button";

interface VideoPlayerProps {
  url: string;
}

export function VideoPlayer({ url }: VideoPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);

  return (
    <div className="group relative overflow-hidden rounded-[1.6rem] border border-border/70 bg-secondary/10">
      <video
        src={url}
        className="max-h-[28rem] w-full cursor-pointer bg-black/70 object-contain"
        onClick={(event) => {
          const video = event.currentTarget;
          if (video.paused) {
            void video.play();
            setIsPlaying(true);
          } else {
            video.pause();
            setIsPlaying(false);
          }
        }}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onEnded={() => setIsPlaying(false)}
        playsInline
      />

      <div className="absolute inset-x-0 bottom-0 flex items-center gap-2 bg-gradient-to-t from-secondary via-secondary/65 to-transparent p-3 opacity-0 transition-opacity duration-300 group-hover:opacity-100">
        <Button
          variant="ghost"
          size="icon"
          className="h-9 w-9 rounded-full text-secondary-foreground hover:bg-secondary-foreground/10"
          onClick={(event) => {
            const video = event.currentTarget.closest(".group")?.querySelector("video");
            if (!video) return;
            if (video.paused) {
              void video.play();
            } else {
              video.pause();
            }
          }}
        >
          {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="ml-0.5 h-4 w-4" />}
        </Button>

        <Button
          variant="ghost"
          size="icon"
          className="h-9 w-9 rounded-full text-secondary-foreground hover:bg-secondary-foreground/10"
          onClick={(event) => {
            const video = event.currentTarget.closest(".group")?.querySelector("video");
            if (!video) return;
            video.muted = !video.muted;
            setIsMuted(video.muted);
          }}
        >
          {isMuted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
        </Button>

        <div className="flex-1" />

        <Button
          variant="ghost"
          size="icon"
          className="h-9 w-9 rounded-full text-secondary-foreground hover:bg-secondary-foreground/10"
          onClick={(event) => {
            const video = event.currentTarget.closest(".group")?.querySelector("video");
            if (video) {
              void video.requestFullscreen();
            }
          }}
        >
          <Maximize className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
