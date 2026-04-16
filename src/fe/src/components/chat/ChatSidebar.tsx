import { MessageSquare, Plus, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { Chat } from "@/types/chat";

interface ChatSidebarProps {
  chats: Chat[];
  currentChatId: string | null;
  onSelectChat: (chatId: string) => void;
  onNewChat: () => void;
  onDeleteChat: (chatId: string) => void;
}

export function ChatSidebar({
  chats,
  currentChatId,
  onSelectChat,
  onNewChat,
  onDeleteChat,
}: ChatSidebarProps) {
  return (
    <aside className="flex h-full w-72 flex-col border-r border-border/60 bg-card/90 backdrop-blur-xl">
      <div className="space-y-4 border-b border-border/60 p-5">
        <div>
          <p className="font-mono text-xs uppercase tracking-[0.22em] text-primary/80">
            Session history
          </p>
          <h2 className="mt-2 text-xl font-semibold text-foreground">Numerix threads</h2>
          <p className="mt-1 text-sm leading-6 text-muted-foreground">
            Stored locally for quick demo loops.
          </p>
        </div>

        <Button onClick={onNewChat} className="w-full rounded-full">
          <Plus className="mr-2 h-4 w-4" />
          New thread
        </Button>
      </div>

      <ScrollArea className="flex-1 px-3 py-3">
        <div className="space-y-2">
          {chats.length === 0 ? (
            <div className="rounded-3xl border border-dashed border-border/70 px-4 py-8 text-center text-sm leading-6 text-muted-foreground">
              No renders yet. Start by describing a science video in the studio.
            </div>
          ) : (
            chats.map((chat) => (
              <div
                key={chat.id}
                onClick={() => onSelectChat(chat.id)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    onSelectChat(chat.id);
                  }
                }}
                role="button"
                tabIndex={0}
                className={cn(
                  "group flex w-full items-start gap-3 rounded-3xl border px-4 py-3 text-left transition",
                  currentChatId === chat.id
                    ? "border-primary/35 bg-primary/10"
                    : "border-border/70 bg-background/75 hover:border-primary/25 hover:bg-primary/5",
                )}
              >
                <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl bg-secondary/70 text-secondary-foreground">
                  <MessageSquare className="h-4 w-4" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-foreground">{chat.title}</p>
                  <p className="mt-1 text-xs uppercase tracking-[0.18em] text-muted-foreground">
                    {chat.createdAt.toLocaleDateString()}
                  </p>
                </div>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 shrink-0 rounded-full opacity-0 transition-opacity group-hover:opacity-100"
                  onClick={(event) => {
                    event.stopPropagation();
                    onDeleteChat(chat.id);
                  }}
                >
                  <Trash2 className="h-4 w-4 text-muted-foreground" />
                </Button>
              </div>
            ))
          )}
        </div>
      </ScrollArea>
    </aside>
  );
}
