export function Footer() {
  return (
    <footer className="border-t border-border/60 bg-card/40">
      <div className="container flex flex-col gap-2 py-8 text-sm text-muted-foreground md:flex-row md:items-center md:justify-between">
        <div>
          <span className="font-medium text-foreground">Numerix</span> turns scientific and
          mathematical ideas into rendered visual explanations.
        </div>
        <div className="font-mono text-xs uppercase tracking-[0.24em] text-primary/80">
          Prompt · Render · Review
        </div>
      </div>
    </footer>
  );
}
