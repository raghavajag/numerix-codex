import { useCallback, useEffect, useMemo, useState } from "react";

import { runNumerixPrompt } from "@/lib/api";
import { Chat, Message } from "@/types/chat";

const STORAGE_KEY = "numerix-chat-history-v1";

type StoredState = {
  chats: Array<{
    id: string;
    title: string;
    createdAt: string;
    messages: Array<{
      id: string;
      role: "user" | "assistant";
      content: string;
      videoUrl?: string;
      isError?: boolean;
      isStreaming?: boolean;
      timestamp: string;
    }>;
  }>;
  currentChatId: string | null;
};

function makeChat(title = "Untitled request"): Chat {
  return {
    id: crypto.randomUUID(),
    title,
    messages: [],
    createdAt: new Date(),
  };
}

function serializeState(chats: Chat[], currentChatId: string | null): StoredState {
  return {
    chats: chats.map((chat) => ({
      ...chat,
      createdAt: chat.createdAt.toISOString(),
      messages: chat.messages.map((message) => ({
        ...message,
        timestamp: message.timestamp.toISOString(),
      })),
    })),
    currentChatId,
  };
}

function parseState(): StoredState | null {
  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) return null;

  try {
    return JSON.parse(raw) as StoredState;
  } catch {
    return null;
  }
}

function hydrateChats(stored: StoredState | null) {
  if (!stored) {
    return { chats: [], currentChatId: null as string | null };
  }

  return {
    chats: stored.chats.map((chat) => ({
      ...chat,
      createdAt: new Date(chat.createdAt),
      messages: chat.messages.map((message) => ({
        ...message,
        timestamp: new Date(message.timestamp),
      })),
    })),
    currentChatId: stored.currentChatId,
  };
}

function buildTitle(content: string) {
  return content.length > 52 ? `${content.slice(0, 52)}…` : content;
}

export function useChat() {
  const initialState = useMemo(() => {
    if (typeof window === "undefined") {
      return { chats: [], currentChatId: null as string | null };
    }
    return hydrateChats(parseState());
  }, []);

  const [chats, setChats] = useState<Chat[]>(initialState.chats);
  const [currentChatId, setCurrentChatId] = useState<string | null>(initialState.currentChatId);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingChats] = useState(false);

  const currentChat = chats.find((chat) => chat.id === currentChatId) ?? null;

  useEffect(() => {
    if (typeof window === "undefined") return;
    window.localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify(serializeState(chats, currentChatId)),
    );
  }, [chats, currentChatId]);

  const createNewChat = useCallback(() => {
    const newChat = makeChat();
    setChats((prev) => [newChat, ...prev]);
    setCurrentChatId(newChat.id);
    return newChat.id;
  }, []);

  const deleteChat = useCallback(
    (chatId: string) => {
      const nextChats = chats.filter((chat) => chat.id !== chatId);
      setChats(nextChats);
      if (currentChatId === chatId) {
        setCurrentChatId(nextChats[0]?.id ?? null);
      }
    },
    [chats, currentChatId],
  );

  const selectChat = useCallback((chatId: string) => {
    setCurrentChatId(chatId);
  }, []);

  const sendMessage = useCallback(
    async (content: string, language: string = "en") => {
      const chatId = currentChatId || createNewChat();
      const userMessage: Message = {
        id: crypto.randomUUID(),
        role: "user",
        content,
        timestamp: new Date(),
      };

      setChats((prev) =>
        prev.map((chat) =>
          chat.id === chatId
            ? {
                ...chat,
                title: chat.messages.length === 0 ? buildTitle(content) : chat.title,
                messages: [...chat.messages, userMessage],
              }
            : chat,
        ),
      );
      setCurrentChatId(chatId);
      setIsLoading(true);

      try {
        const data = await runNumerixPrompt(content, language);

        const assistantMessage: Message = {
          id: crypto.randomUUID(),
          role: "assistant",
          content:
            data.status === "success"
              ? "Render complete. Your generated Numerix video is ready."
              : data.result,
          videoUrl: data.status === "success" ? data.result : undefined,
          isError: data.status === "error",
          timestamp: new Date(),
        };

        setChats((prev) =>
          prev.map((chat) =>
            chat.id === chatId
              ? {
                  ...chat,
                  messages: [...chat.messages, assistantMessage],
                }
              : chat,
          ),
        );
      } catch (error) {
        const assistantMessage: Message = {
          id: crypto.randomUUID(),
          role: "assistant",
          content:
            error instanceof Error
              ? error.message
              : "The request failed before Numerix could finish the render.",
          isError: true,
          timestamp: new Date(),
        };

        setChats((prev) =>
          prev.map((chat) =>
            chat.id === chatId
              ? {
                  ...chat,
                  messages: [...chat.messages, assistantMessage],
                }
              : chat,
          ),
        );
      } finally {
        setIsLoading(false);
      }
    },
    [createNewChat, currentChatId],
  );

  return {
    chats,
    currentChat,
    currentChatId,
    isLoading,
    isLoadingChats,
    createNewChat,
    deleteChat,
    selectChat,
    sendMessage,
  };
}
