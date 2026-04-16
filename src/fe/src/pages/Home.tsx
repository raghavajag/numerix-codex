import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowRight, Atom, GalleryHorizontal, Orbit, Sparkles, Waves } from "lucide-react";

import { LanguageCode, LanguageSelector } from "@/components/chat/LanguageSelector";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";

const examplePrompts = [
  "Explain binary search in an array with a clean step-by-step animation.",
  "Visualize simple harmonic motion with the graph and the moving mass together.",
  "Show how the recent Artemis II moon voyage works from Earth orbit to lunar flyby and back.",
];

const capabilities = [
  {
    icon: Orbit,
    title: "Prompt to render",
    body: "Describe the concept once. Numerix sends the prompt straight into the video-generation pipeline.",
  },
  {
    icon: Waves,
    title: "Science-first output",
    body: "The backend plans the explanation, retrieves the right Manim context, and returns a playable result.",
  },
  {
    icon: GalleryHorizontal,
    title: "Examples preserved",
    body: "Demo videos stay available so users can see what the system can already produce before trying it.",
  },
];

export default function Home() {
  const navigate = useNavigate();
  const [prompt, setPrompt] = useState(examplePrompts[2]);
  const [language, setLanguage] = useState<LanguageCode>("en");

  const openStudio = (value: string) => {
    const trimmed = value.trim();
    navigate("/chat", {
      state: trimmed ? { initialPrompt: trimmed, initialLanguage: language } : undefined,
    });
  };

  return (
    <div className="container py-10 sm:py-14">
      <section className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
        <div className="space-y-8">
          <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-1.5 text-xs font-medium uppercase tracking-[0.22em] text-primary">
            <Sparkles className="h-3.5 w-3.5" />
            Numerix Studio
          </div>

          <div className="space-y-4">
            <h1 className="max-w-4xl font-serif text-5xl leading-[0.95] tracking-tight text-foreground sm:text-6xl lg:text-7xl">
              Prompt in.
              <br />
              Science video out.
            </h1>
            <p className="max-w-2xl text-lg leading-8 text-muted-foreground sm:text-xl">
              Numerix turns technical ideas into cinematic visual explanations.
              Start with a prompt, move into the studio, and review the rendered result in one
              focused workflow.
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            {capabilities.map((item) => (
              <Card
                key={item.title}
                className="border-border/70 bg-card/80 shadow-[0_24px_80px_-56px_hsl(var(--foreground)/0.45)] backdrop-blur"
              >
                <CardContent className="space-y-3 p-5">
                  <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-primary/12 text-primary">
                    <item.icon className="h-5 w-5" />
                  </div>
                  <div className="space-y-1">
                    <h2 className="font-semibold text-foreground">{item.title}</h2>
                    <p className="text-sm leading-6 text-muted-foreground">{item.body}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        <Card className="border-border/70 bg-card/85 shadow-[0_30px_90px_-54px_hsl(var(--foreground)/0.45)] backdrop-blur">
          <CardContent className="space-y-5 p-6 sm:p-7">
            <div className="space-y-2">
              <p className="font-mono text-xs uppercase tracking-[0.22em] text-primary/80">
                Launch Prompt
              </p>
              <h2 className="text-2xl font-semibold text-foreground">Open the studio with a real prompt</h2>
              <p className="text-sm leading-6 text-muted-foreground">
                Start with a concept worth exploring. Numerix handles ambitious topics across
                mathematics, physics, engineering, and scientific storytelling.
              </p>
            </div>

            <Textarea
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              className="min-h-[200px] resize-none rounded-3xl border-border/80 bg-background/70 p-5 text-base leading-7"
              placeholder="Describe the science video you want Numerix to generate..."
            />

            <div className="flex flex-wrap gap-3">
              <Button size="lg" className="rounded-full px-6" onClick={() => openStudio(prompt)}>
                Open Studio
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
              <Button variant="outline" size="lg" className="rounded-full px-6" onClick={() => navigate("/gallery")}>
                View Demo Videos
              </Button>
            </div>

            <div className="flex items-center justify-between gap-3 rounded-3xl border border-border/70 bg-background/60 px-4 py-3">
              <div className="space-y-1">
                <p className="font-mono text-xs uppercase tracking-[0.22em] text-primary/80">
                  Output Language
                </p>
                <p className="text-sm text-muted-foreground">
                  Choose the narration and explanation language for this render.
                </p>
              </div>
              <LanguageSelector value={language} onChange={setLanguage} />
            </div>

            <div className="grid gap-3">
              {examplePrompts.map((item) => (
                <button
                  key={item}
                  type="button"
                  className="rounded-2xl border border-border/70 bg-background/60 px-4 py-3 text-left text-sm leading-6 text-muted-foreground transition hover:border-primary/40 hover:bg-primary/5 hover:text-foreground"
                  onClick={() => setPrompt(item)}
                >
                  {item}
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      </section>

      <section className="mt-16 grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
        <Card className="border-border/70 bg-secondary/95 text-secondary-foreground shadow-[0_24px_80px_-54px_hsl(var(--foreground)/0.55)]">
          <CardContent className="space-y-5 p-7">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-primary/20 text-primary">
                <Atom className="h-5 w-5" />
              </div>
              <div>
                <p className="font-mono text-xs uppercase tracking-[0.22em] text-primary/70">
                  Workflow
                </p>
                <h3 className="text-xl font-semibold">From prompt to visual explanation</h3>
              </div>
            </div>
            <div className="space-y-3 text-sm leading-7 text-secondary-foreground/80">
              <p>1. Describe the concept, mechanism, or story you want to see.</p>
              <p>2. Numerix plans the explanation and builds the animation.</p>
              <p>3. Review the generated video directly inside the studio.</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-border/70 bg-card/85 backdrop-blur">
          <CardContent className="grid gap-6 p-7 sm:grid-cols-2">
            <div>
              <p className="font-mono text-xs uppercase tracking-[0.22em] text-primary/80">
                Experience
              </p>
              <h3 className="mt-2 text-xl font-semibold text-foreground">Built for clarity and momentum</h3>
            </div>
            <div className="space-y-3 text-sm leading-7 text-muted-foreground">
              <p>A single studio keeps the interaction focused from prompt to playback.</p>
              <p>Thread history stays available so ideas can be iterated without losing context.</p>
              <p>The gallery remains visible for quickly inspecting sample results and visual range.</p>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
