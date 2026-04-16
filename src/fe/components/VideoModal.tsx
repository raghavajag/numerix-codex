"use client";

import * as Dialog from "@radix-ui/react-dialog";
import { ReactNode } from "react";

import { VideoPlayer } from "@/components/VideoPlayer";

type VideoModalProps = {
  trigger: ReactNode;
  url: string;
};

export function VideoModal({ trigger, url }: VideoModalProps) {
  return (
    <Dialog.Root>
      <Dialog.Trigger asChild>{trigger}</Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm" />
        <Dialog.Content className="fixed left-1/2 top-1/2 w-[min(92vw,960px)] -translate-x-1/2 -translate-y-1/2 rounded-3xl border border-white/10 bg-slate-950 p-4 shadow-2xl">
          <div className="mb-3 flex items-center justify-between">
            <Dialog.Title className="text-lg font-semibold text-white">
              Animation Preview
            </Dialog.Title>
            <Dialog.Close className="rounded-full border border-white/10 px-3 py-1 text-sm text-slate-300 transition hover:border-cyan-400/40 hover:text-white">
              Close
            </Dialog.Close>
          </div>
          <VideoPlayer url={url} />
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
