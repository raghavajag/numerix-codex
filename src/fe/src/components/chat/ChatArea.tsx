import { useEffect, useRef } from "react";
import { Loader2, Sparkles } from "lucide-react";

import { ScrollArea } from "@/components/ui/scroll-area";
import { LanguageCode } from "@/lib/languages";
import { Message } from "@/types/chat";
import { ChatInput } from "./ChatInput";
import { ChatMessage } from "./ChatMessage";

interface ChatAreaProps {
  messages: Message[];
  onSendMessage: (content: string, language: LanguageCode) => void;
  isLoading: boolean;
  language: LanguageCode;
  onLanguageChange: (language: LanguageCode) => void;
}

export function ChatArea({
  messages,
  onSendMessage,
  isLoading,
  language,
  onLanguageChange,
}: ChatAreaProps) {
  const scrollAreaRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const viewport = scrollAreaRef.current?.querySelector<HTMLDivElement>(
      "[data-radix-scroll-area-viewport]",
    );
    if (viewport) {
      viewport.scrollTop = viewport.scrollHeight;
    }
  }, [messages, isLoading]);

  return (
    <div className="flex h-full flex-1 flex-col">
      {messages.length === 0 ? (
        <div className="flex flex-1 items-center justify-center px-6 py-12">
          <div className="max-w-2xl space-y-6 text-center">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-[1.75rem] bg-primary/12 text-primary">
              <Sparkles className="h-8 w-8" />
            </div>
            <div className="space-y-3">
              <h2 className="font-serif text-4xl tracking-tight text-foreground">
                Describe the science video you want.
              </h2>
              <p className="text-base leading-8 text-muted-foreground sm:text-lg">
                Use one clear prompt. Numerix sends it to the backend, waits for the response,
                and drops the finished video or reply directly into this thread.
              </p>
            </div>
          </div>
        </div>
      ) : (
        <ScrollArea className="flex-1" ref={scrollAreaRef}>
          <div className="mx-auto flex w-full max-w-5xl flex-col gap-4 px-4 py-6 sm:px-6">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isLoading && (
              <div className="rounded-[1.75rem] border border-border/70 bg-card/80 p-5 shadow-sm">
                <div className="flex items-start gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-2xl bg-primary/12 text-primary">
                    <Loader2 className="h-4 w-4 animate-spin" />
                  </div>
                  <div className="space-y-1">
                    <p className="font-medium text-foreground">Numerix</p>
                    <p className="text-sm leading-6 text-muted-foreground">
                      Sending the prompt through the generation pipeline and waiting for the render result.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
      )}

      <ChatInput
        onSend={onSendMessage}
        isLoading={isLoading}
        language={language}
        onLanguageChange={onLanguageChange}
      />
    </div>
  );
}
