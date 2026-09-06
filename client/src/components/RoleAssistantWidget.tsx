import { AIChatBox, type Message } from "@/components/AIChatBox";
import { useFastApiMutation } from "@/hooks/useFastApi";
import { Bot, X } from "lucide-react";
import { useState } from "react";

const rolePresentation = {
  individual: { icon: "🌱", label: "Carbon Coach", prompt: "How can I reduce transport emissions this month?" },
  org_admin: { icon: "🎯", label: "Action Advisor", prompt: "How can we assign a practical recommendation?" },
  super_admin: { icon: "🛡️", label: "Platform Guardian", prompt: "What evidence should I review before resolving a report?" },
} as const;

export default function RoleAssistantWidget({ role }: { role: keyof typeof rolePresentation }) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const chat = useFastApiMutation<{ answer: string; engine: string; scope: string }, { message: string }>("/assistant/chat");
  const presentation = rolePresentation[role];
  function send(message: string) {
    const content = message.trim();
    if (!content || chat.isPending) return;
    setMessages((current) => [...current, { role: "user", content }]);
    chat.mutate({ message: content }, {
      onSuccess: (result) => setMessages((current) => [...current, { role: "assistant", content: `${result.answer}\n\n*Context used: ${result.scope}*` }]),
      onError: (error) => setMessages((current) => [...current, { role: "assistant", content: `I could not complete that request: ${error.message}` }]),
    });
  }
  return <><button type="button" onClick={() => setOpen((value) => !value)} aria-label={open ? "Close CarbonSense assistant" : `Open ${presentation.label}`} className="fixed bottom-6 right-6 z-50 grid h-14 w-14 place-items-center rounded-full bg-gradient-to-br from-emerald-500 to-emerald-800 text-xl text-white shadow-xl shadow-emerald-900/25 transition-transform hover:scale-105 active:scale-[.97]" title={presentation.label}>{open ? <X size={23} /> : presentation.icon}</button>{open && <section className="fixed bottom-24 right-4 z-50 w-[min(390px,calc(100vw-2rem))] overflow-hidden rounded-3xl border border-emerald-950/15 bg-white shadow-2xl dark:border-white/10 dark:bg-[#13261f]"><header className="flex items-center gap-3 bg-gradient-to-r from-emerald-700 to-emerald-800 px-5 py-4 text-white"><span className="grid h-9 w-9 place-items-center rounded-xl bg-white/15 text-lg">{presentation.icon}</span><span className="min-w-0 flex-1"><b className="block text-sm">{presentation.label}</b><small className="block text-[11px] text-emerald-100">Grounded CarbonSense guidance</small></span><Bot size={18} /></header><AIChatBox className="border-0 shadow-none" height="420px" messages={messages} onSendMessage={send} isLoading={chat.isPending} placeholder="Ask about your CarbonSense workspace…" emptyStateMessage="Ask a question about your CarbonSense records." suggestedPrompts={[presentation.prompt, "Explain the model and data boundary."]} /><p className="border-t border-emerald-950/10 px-4 py-2 text-[10px] leading-4 text-slate-500 dark:border-white/10 dark:text-slate-400">Powered by Google Gemini, grounded in your CarbonSense workspace context. Planning guidance only — not verified emissions reductions.</p></section>}</>;
}
