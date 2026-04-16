export function TopBar() {
  return (
    <header className="border-b border-white/10 bg-slate-950/80 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-cyan-300">
            AnimAI
          </p>
          <h1 className="mt-1 text-2xl font-semibold text-white">
            Turn prompts into narrated Manim animations
          </h1>
        </div>
        <div className="rounded-full border border-emerald-400/30 bg-emerald-400/10 px-3 py-1 text-sm text-emerald-200">
          Beta
        </div>
      </div>
    </header>
  );
}
