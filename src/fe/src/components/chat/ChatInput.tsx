import { KeyboardEvent, useState } from "react";
import { ArrowUpRight } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { LanguageCode, LanguageSelector } from "./LanguageSelector";

interface ChatInputProps {
  onSend: (message: string, language: LanguageCode) => void;
  isLoading: boolean;
  language: LanguageCode;
  onLanguageChange: (language: LanguageCode) => void;
}

const quickPrompts = [
  "Explain binary search visually.",
  "Show SHM with both graph and motion.",
  "Visualize Artemis II trajectory.",
];

export function ChatInput({
  onSend,
  isLoading,
  language,
  onLanguageChange,
}: ChatInputProps) {
  const [input, setInput] = useState("");

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;
    onSend(trimmed, language);
    setInput("");
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-border/60 bg-background/90 px-4 py-4 backdrop-blur-xl sm:px-6">
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap gap-2">
            {quickPrompts.map((prompt) => (
              <button
                key={prompt}
                type="button"
                className="rounded-full border border-border/70 bg-card/80 px-3 py-1.5 text-xs font-medium text-muted-foreground transition hover:border-primary/40 hover:bg-primary/5 hover:text-foreground"
                onClick={() => setInput(prompt)}
              >
                {prompt}
              </button>
            ))}
          </div>
          <LanguageSelector value={language} onChange={onLanguageChange} />
        </div>

        <div className="rounded-[1.9rem] border border-border/80 bg-card/85 p-3 shadow-[0_24px_80px_-58px_hsl(var(--foreground)/0.5)]">
          <div className="flex gap-3">
            <Textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask Numerix to generate a science or math explainer video..."
              className="min-h-[132px] resize-none rounded-[1.3rem] border-0 bg-background/80 px-4 py-4 text-base leading-7 shadow-none focus-visible:ring-1"
              disabled={isLoading}
            />
            <Button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              size="icon"
              className="h-14 w-14 shrink-0 self-end rounded-2xl"
            >
              <ArrowUpRight className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
