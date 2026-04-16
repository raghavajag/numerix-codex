import { Outlet } from "react-router-dom";
import { Header } from "./Header";
import { Footer } from "./Footer";

export function Layout() {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <Header />
      <main className="relative flex-1 overflow-hidden">
        <div className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(circle_at_top,_hsl(var(--primary)/0.14),_transparent_32%),linear-gradient(180deg,_hsl(var(--background)),_hsl(var(--card)))]" />
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
