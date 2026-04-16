"use client";

import { useEffect, useState } from "react";

import { ChatInterface } from "@/components/ChatInterface";
import type { ChatMessage } from "@/components/MessageItem";
import { TopBar } from "@/components/TopBar";

const STORAGE_KEY = "numerix_chat_history";
const LEGACY_STORAGE_KEY = "animai_chat_history";

function createMessage(partial: Partial<ChatMessage> & Pick<ChatMessage, "text">): ChatMessage {
  return {
    id: crypto.randomUUID(),
    timestamp: new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    }),
    ...partial,
  };
}

export default function Page() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY) ?? localStorage.getItem(LEGACY_STORAGE_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored) as ChatMessage[];
        setMessages(parsed);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(parsed));
        localStorage.removeItem(LEGACY_STORAGE_KEY);
      } catch {
        localStorage.removeItem(STORAGE_KEY);
        localStorage.removeItem(LEGACY_STORAGE_KEY);
      }
    }
  }, []);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
  }, [messages]);

  async function handleSubmitPrompt(prompt: string) {
    const userMessage = createMessage({ text: prompt, isResponse: false });
    const loadingMessage = createMessage({
      text: "Generating your animation...",
      isResponse: true,
      isLoading: true,
    });

    setIsSubmitting(true);
    setMessages((current) => [...current, userMessage, loadingMessage]);

    try {
      const response = await fetch("/api/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt, language: "en" }),
      });

      const data = await response.json();
      setMessages((current) =>
        current.map((message) =>
          message.id === loadingMessage.id
            ? {
                ...message,
                isLoading: false,
                isError: !response.ok || data.status === "error",
                text:
                  response.ok && data.status === "success"
                    ? "Your animation is ready."
                    : data.result || "Something went wrong.",
                videoUrl:
                  response.ok && data.status === "success" ? data.result : undefined,
              }
            : message
        )
      );
    } catch {
      setMessages((current) =>
        current.map((message) =>
          message.id === loadingMessage.id
            ? {
                ...message,
                isLoading: false,
                isError: true,
                text: "Unable to reach the Numerix service right now.",
              }
            : message
        )
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="flex min-h-screen flex-col bg-slate-950 text-slate-100">
      <TopBar />
      <ChatInterface
        disabled={isSubmitting}
        messages={messages}
        onSubmitPrompt={handleSubmitPrompt}
      />
    </main>
  );
}
