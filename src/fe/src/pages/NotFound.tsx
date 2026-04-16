import { useEffect } from "react";
import { useLocation } from "react-router-dom";

import { Button } from "@/components/ui/button";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error("404 Error: User attempted to access non-existent route:", location.pathname);
  }, [location.pathname]);

  return (
    <div className="flex min-h-screen items-center justify-center px-6">
      <div className="max-w-md space-y-6 text-center">
        <p className="font-mono text-xs uppercase tracking-[0.24em] text-primary/80">404</p>
        <h1 className="font-serif text-5xl tracking-tight text-foreground">Route not found</h1>
        <p className="text-lg leading-8 text-muted-foreground">
          This Numerix page does not exist. Go back to the home page or reopen the studio.
        </p>
        <div className="flex items-center justify-center gap-3">
          <Button asChild className="rounded-full px-6">
            <a href="/">Back home</a>
          </Button>
          <Button asChild variant="outline" className="rounded-full px-6">
            <a href="/chat">Open studio</a>
          </Button>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
