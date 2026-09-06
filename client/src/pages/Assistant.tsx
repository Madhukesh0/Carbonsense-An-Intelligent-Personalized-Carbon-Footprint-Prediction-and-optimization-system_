import { useState } from "react";
import { useAuth } from "@/_core/hooks/useAuth";
import RepoAuthPage from "@/components/RepoAuthPage";
import RepoShell from "@/components/RepoShell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useFastApiMutation } from "@/hooks/useFastApi";

type AssistantReply = { answer: string; scope: string; context?: { acceptedRecommendations?: number } };

export default function Assistant() {
  const auth = useAuth();
  const [message, setMessage] = useState("");
  const chat = useFastApiMutation<AssistantReply, { message: string }>("/assistant/chat");
  if (!auth.loading && !auth.isAuthenticated) return <RepoAuthPage mode="login" />;
  return <RepoShell title="Assistant"><main className="cs-page"><Card className="cs-card mx-auto max-w-3xl p-6 sm:p-8"><p className="cs-kicker text-emerald-700">Private guidance</p><h1 className="mt-3 text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl dark:text-white">CarbonSense climate assistant</h1><p className="mt-3 text-base leading-relaxed text-slate-500">Ask about transport, electricity, diet, fuel, goals, forecasts, or approved recommendations. Responses use only your authenticated workspace and do not claim a verified emissions reduction.</p><div className="mt-6 flex gap-3"><Input value={message} onChange={event => setMessage(event.target.value)} placeholder="How can I lower my transport emissions?" /><Button className="bg-[#157f54] hover:bg-[#106b47]" onClick={() => chat.mutate({ message })} disabled={chat.isPending || !message.trim()}>Ask</Button></div>{chat.data && <div className="mt-6 rounded-2xl bg-[#e5f7ec] p-5"><p className="font-semibold">Assistant response</p><p className="mt-2 text-base leading-relaxed text-slate-600">{chat.data.answer}</p><p className="mt-4 text-xs text-slate-500">Grounded in: {chat.data.scope}</p>{(chat.data.context?.acceptedRecommendations ?? 0) > 0 && <p className="mt-3 text-base text-slate-600">{chat.data.context?.acceptedRecommendations} accepted action(s) are ready to track before completion is reported.</p>}</div>}{chat.error && <p role="alert" className="mt-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-base text-red-700">{chat.error.message}</p>}</Card></main></RepoShell>;
}
