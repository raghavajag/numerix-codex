import { AlertCircle, Bot, User } from "lucide-react";

import { cn } from "@/lib/utils";
import { Message } from "@/types/chat";
import { VideoPlayer } from "./VideoPlayer";

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "rounded-[1.8rem] border p-5 shadow-sm transition-colors",
        isUser
          ? "border-primary/25 bg-primary/8"
          : "border-border/70 bg-card/80",
      )}
    >
      <div className="flex items-start gap-4">
        <div
          className={cn(
            "flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl",
            isUser ? "bg-primary text-primary-foreground" : "bg-secondary text-secondary-foreground",
          )}
        >
          {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
        </div>

        <div className="min-w-0 flex-1 space-y-3">
          <div className="flex items-center justify-between gap-3">
            <p className="font-medium text-foreground">{isUser ? "You" : "Numerix"}</p>
            <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">
              {message.timestamp.toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </p>
          </div>

          {message.isError ? (
            <div className="flex items-start gap-3 rounded-2xl border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
              <span className="leading-6">{message.content}</span>
            </div>
          ) : message.videoUrl ? (
            <div className="space-y-3">
              <VideoPlayer url={message.videoUrl} />
              <p className="text-sm leading-7 text-muted-foreground">{message.content}</p>
            </div>
          ) : (
            <p className="whitespace-pre-wrap text-sm leading-7 text-foreground/90">
              {message.content}
              {message.isStreaming && (
                <span className="ml-1 inline-block h-4 w-2 animate-pulse rounded-sm bg-primary align-middle" />
              )}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
