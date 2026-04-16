"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { ChatMessage, MessageItem } from "@/components/MessageItem";

const formSchema = z.object({
  prompt: z.string().min(1, "Please enter a prompt."),
});

type FormValues = z.infer<typeof formSchema>;

type ChatInterfaceProps = {
  messages: ChatMessage[];
  onSubmitPrompt: (prompt: string) => Promise<void>;
  disabled?: boolean;
};

export function ChatInterface({
  messages,
  onSubmitPrompt,
  disabled = false,
}: ChatInterfaceProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { prompt: "" },
  });

  const onSubmit = handleSubmit(async (values) => {
    await onSubmitPrompt(values.prompt);
    reset();
  });

  return (
    <section className="mx-auto flex max-w-5xl flex-1 flex-col px-6 py-6">
      <div className="mb-6 flex-1 space-y-4 overflow-y-auto rounded-3xl border border-white/10 bg-slate-950/70 p-5 shadow-2xl shadow-cyan-950/20">
        {messages.length === 0 ? (
          <div className="rounded-3xl border border-dashed border-white/10 bg-white/5 p-6 text-sm text-slate-300">
            Ask for an animation like “explain projectile motion” or “show derivative of x squared”.
          </div>
        ) : (
          messages.map((message) => <MessageItem key={message.id} message={message} />)
        )}
      </div>

      <form
        className="rounded-3xl border border-white/10 bg-slate-950/80 p-4 shadow-xl"
        onSubmit={onSubmit}
      >
        <label className="mb-2 block text-sm font-medium text-slate-200" htmlFor="prompt">
          Describe the animation you want
        </label>
        <div className="flex flex-col gap-3 md:flex-row">
          <textarea
            id="prompt"
            rows={3}
            className="min-h-28 flex-1 rounded-2xl border border-white/10 bg-slate-900 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-cyan-400/50"
            placeholder="Explain the area of a circle with a visual proof..."
            {...register("prompt")}
          />
          <button
            className="rounded-2xl bg-cyan-400 px-6 py-3 font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-300"
            disabled={disabled}
            type="submit"
          >
            {disabled ? "Working..." : "Generate"}
          </button>
        </div>
        {errors.prompt ? (
          <p className="mt-2 text-sm text-rose-300">{errors.prompt.message}</p>
        ) : null}
      </form>
    </section>
  );
}
