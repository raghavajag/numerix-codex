import { useState } from "react";
import { Menu, Sparkles, X } from "lucide-react";

import { NavLink } from "@/components/NavLink";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const links = [
  { to: "/", label: "Home" },
  { to: "/chat", label: "Studio" },
  { to: "/gallery", label: "Examples" },
  { to: "/about", label: "About" },
];

export function Header() {
  const [open, setOpen] = useState(false);
  const linkClasses =
    "text-sm font-medium text-muted-foreground transition-colors hover:text-foreground";
  const activeLinkClasses = "text-foreground";

  return (
    <header className="sticky top-0 z-50 border-b border-border/60 bg-background/80 backdrop-blur-xl">
      <div className="container flex h-16 items-center justify-between">
        <NavLink to="/" className="flex items-center gap-3" onClick={() => setOpen(false)}>
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-[0_12px_30px_-14px_hsl(var(--primary)/0.8)]">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <div className="font-mono text-[11px] uppercase tracking-[0.3em] text-primary/80">
              Numerix
            </div>
            <div className="text-sm text-muted-foreground">Science video generation</div>
          </div>
        </NavLink>

        <nav className="hidden items-center gap-8 md:flex">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={linkClasses}
              activeClassName={activeLinkClasses}
              end={link.to === "/"}
            >
              {link.label}
            </NavLink>
          ))}
          <Button asChild size="sm" className="rounded-full px-5">
            <NavLink to="/chat">Open Studio</NavLink>
          </Button>
        </nav>

        <Button
          variant="ghost"
          size="icon"
          className="md:hidden"
          onClick={() => setOpen((value) => !value)}
          aria-label="Toggle navigation"
        >
          {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </Button>
      </div>

      <div
        className={cn(
          "border-t border-border/60 bg-background/95 transition-[max-height,opacity] duration-300 md:hidden",
          open ? "max-h-80 opacity-100" : "max-h-0 overflow-hidden opacity-0",
        )}
      >
        <div className="container flex flex-col gap-2 py-4">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className="rounded-2xl px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-card hover:text-foreground"
              activeClassName="bg-card text-foreground"
              end={link.to === "/"}
              onClick={() => setOpen(false)}
            >
              {link.label}
            </NavLink>
          ))}
          <Button asChild className="mt-2 rounded-full">
            <NavLink to="/chat" onClick={() => setOpen(false)}>
              Open Studio
            </NavLink>
          </Button>
        </div>
      </div>
    </header>
  );
}
