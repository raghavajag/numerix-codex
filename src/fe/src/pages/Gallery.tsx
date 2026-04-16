import { useState } from "react";
import { Maximize2, Pause, Play } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const GALLERY_ITEMS = [
  {
    title: "Draw the equation of SHM",
    videoUrl:
      "https://pub-b215a097b7b243dc86da838a88d50339.r2.dev/media/videos/SimpleHarmonicMotionGraph/480p15/SimpleHarmonicMotionGraph.mp4",
  },
  {
    title: "Plot a 3D Spiral Curve expanding along the Z-Axis",
    videoUrl:
      "https://pub-b215a097b7b243dc86da838a88d50339.r2.dev/media/videos/Spiral3DScene/480p15/Spiral3DScene.mp4",
  },
  {
    title: "Explain Binary Search in an Array",
    videoUrl:
      "https://pub-b215a097b7b243dc86da838a88d50339.r2.dev/media/videos/BinarySearchTutorial/480p15/BinarySearchTutorial.mp4",
  },
  {
    title: "Draw y = x^3 Plot",
    videoUrl:
      "https://pub-b215a097b7b243dc86da838a88d50339.r2.dev/media/videos/CubicFunctionPlot/480p15/CubicFunctionPlot.mp4",
  },
  {
    title: "Visualize Electron Orbits in a Hydrogen Atom",
    videoUrl:
      "https://pub-b215a097b7b243dc86da838a88d50339.r2.dev/media/videos/HydrogenAtomOrbits/480p15/HydrogenAtomOrbits.mp4",
  },
  {
    title: "Draw y = sin(x) from -π to π",
    videoUrl:
      "https://pub-b215a097b7b243dc86da838a88d50339.r2.dev/media/videos/SineCurveWithKeyPoints/480p15/SineCurveWithKeyPoints.mp4",
  },
];

function GalleryCard({ title, videoUrl }: { title: string; videoUrl: string }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  return (
    <Card
      className="group overflow-hidden border-border/70 bg-card/80 shadow-[0_24px_90px_-60px_hsl(var(--foreground)/0.45)] backdrop-blur transition-all duration-300 hover:-translate-y-1 hover:border-primary/40"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <CardContent className="p-0">
        <div className="video-container relative aspect-video overflow-hidden bg-secondary/10">
          <video
            src={videoUrl}
            className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-[1.03]"
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
            loop
            muted
            playsInline
          />

          <div
            className={`absolute inset-0 flex items-center justify-center bg-gradient-to-t from-secondary/80 via-secondary/20 to-transparent transition-opacity duration-300 ${
              isHovered || !isPlaying ? "opacity-100" : "opacity-0"
            }`}
          >
            <Button
              size="icon"
              variant="secondary"
              className="h-14 w-14 rounded-full shadow-lg"
              onClick={(event) => {
                const video = event.currentTarget
                  .closest(".video-container")
                  ?.querySelector("video");
                if (!video) return;
                if (video.paused) {
                  void video.play();
                } else {
                  video.pause();
                }
              }}
            >
              {isPlaying ? <Pause className="h-6 w-6" /> : <Play className="ml-1 h-6 w-6" />}
            </Button>
          </div>

          <Button
            size="icon"
            variant="ghost"
            className={`absolute bottom-3 right-3 h-9 w-9 rounded-full bg-background/70 backdrop-blur transition-opacity ${
              isHovered ? "opacity-100" : "opacity-0"
            }`}
            onClick={(event) => {
              const video = event.currentTarget.closest(".video-container")?.querySelector("video");
              if (video) {
                void video.requestFullscreen();
              }
            }}
          >
            <Maximize2 className="h-4 w-4" />
          </Button>
        </div>

        <div className="space-y-2 p-5">
          <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-primary/70">
            Demo clip
          </p>
          <p className="text-base font-semibold leading-6 text-foreground">{title}</p>
        </div>
      </CardContent>
    </Card>
  );
}

export default function Gallery() {
  return (
    <div className="container py-12">
      <div className="mb-12 max-w-3xl space-y-4">
        <p className="font-mono text-xs uppercase tracking-[0.24em] text-primary/80">
          Demo videos
        </p>
        <h1 className="font-serif text-4xl tracking-tight text-foreground sm:text-5xl">
          Existing Numerix examples
        </h1>
        <p className="text-lg leading-8 text-muted-foreground">
          These examples stay in the product. They set quality expectations and give people a fast way
          to inspect style, motion, and output shape before they run their own prompt.
        </p>
      </div>

      <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
        {GALLERY_ITEMS.map((item) => (
          <GalleryCard key={item.videoUrl} title={item.title} videoUrl={item.videoUrl} />
        ))}
      </div>
    </div>
  );
}
