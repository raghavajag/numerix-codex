import { useEffect, useRef, useState } from "react";
import { ArrowLeft, Menu, Plus, X } from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";

import { ChatArea } from "@/components/chat/ChatArea";
import { ChatSidebar } from "@/components/chat/ChatSidebar";
import { Button } from "@/components/ui/button";
import { useChat } from "@/hooks/useChat";
import { LanguageCode } from "@/lib/languages";
import { cn } from "@/lib/utils";

type StudioLocationState = {
  initialPrompt?: string;
  initialLanguage?: LanguageCode;
};

export default function Chat() {
  const navigate = useNavigate();
  const location = useLocation();
  const locationState = location.state as StudioLocationState | null;
  const initialPrompt = locationState?.initialPrompt?.trim() || "";
  const initialLanguage: LanguageCode = locationState?.initialLanguage ?? "en";
  const seededPromptRef = useRef<string | null>(initialPrompt || null);
  const [selectedLanguage, setSelectedLanguage] = useState<LanguageCode>(initialLanguage);

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const {
    chats,
    currentChat,
    currentChatId,
    isLoading,
    createNewChat,
    deleteChat,
    selectChat,
    sendMessage,
  } = useChat();

  useEffect(() => {
    if (!seededPromptRef.current) return;
    if (isLoading) return;

    const prompt = seededPromptRef.current;
    seededPromptRef.current = null;
    void sendMessage(prompt, selectedLanguage);
    navigate(location.pathname, { replace: true, state: null });
  }, [isLoading, location.pathname, navigate, selectedLanguage, sendMessage]);

  return (
    <div className="flex min-h-[calc(100vh-8rem)]">
      <div className="fixed left-4 top-20 z-40 flex items-center gap-2 md:hidden">
        <Button variant="ghost" size="icon" onClick={() => navigate("/")}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <Button variant="ghost" size="icon" onClick={() => setSidebarOpen((value) => !value)}>
          {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </Button>
      </div>

      <div
        className={cn(
          "fixed inset-y-0 left-0 top-16 z-40 w-72 transition-transform duration-300 md:sticky md:top-16 md:h-[calc(100vh-4rem)] md:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <ChatSidebar
          chats={chats}
          currentChatId={currentChatId}
          onSelectChat={(chatId) => {
            selectChat(chatId);
            setSidebarOpen(false);
          }}
          onNewChat={() => {
            createNewChat();
            setSidebarOpen(false);
          }}
          onDeleteChat={deleteChat}
        />
      </div>

      {sidebarOpen && (
        <button
          type="button"
          className="fixed inset-0 top-16 z-30 bg-background/65 backdrop-blur-sm md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <section className="flex min-h-[calc(100vh-8rem)] flex-1 flex-col">
        <div className="border-b border-border/60 bg-card/50 px-4 py-4 backdrop-blur-sm sm:px-6">
          <div className="mx-auto flex w-full max-w-5xl items-center justify-between gap-4">
            <div>
              <p className="font-mono text-xs uppercase tracking-[0.22em] text-primary/80">
                Numerix Studio
              </p>
              <h1 className="text-xl font-semibold text-foreground">Single-prompt render workflow</h1>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" className="hidden rounded-full sm:flex" onClick={() => navigate("/")}>
                Back home
              </Button>
              <Button className="rounded-full" onClick={() => createNewChat()}>
                <Plus className="mr-2 h-4 w-4" />
                New thread
              </Button>
            </div>
          </div>
        </div>

        <div className="flex-1">
          <ChatArea
            messages={currentChat?.messages ?? []}
            onSendMessage={sendMessage}
            isLoading={isLoading}
            language={selectedLanguage}
            onLanguageChange={setSelectedLanguage}
          />
        </div>
      </section>
    </div>
  );
}
