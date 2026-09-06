import { useAuth } from "@/_core/hooks/useAuth";
import RepoAuthPage from "@/components/RepoAuthPage";
import RepoShell from "@/components/RepoShell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useFastApiMutation, useFastApiQuery } from "@/hooks/useFastApi";

type Recommendation = { key: string; title: string; description: string; estimatedReductionKg: number; provenance: string; trigger: string };
type ResultLed = { available: boolean; reason: string | null; predictionKg: number | null; baselineKg: number | null; recommendations: Recommendation[] };

export default function Recommendations() {
  const auth = useAuth();
  const resultLed = useFastApiQuery<ResultLed>(["fastapi", "recommendations", "result-led"], "/recommendations/result-led", auth.isAuthenticated);
  const accept = useFastApiMutation<{ success: boolean }, { recommendation_key: string }>("/recommendations/accept", "POST", [["fastapi", "recommendations", "result-led"], ["fastapi", "recommendations", "mine"]]);
  if (!auth.loading && !auth.isAuthenticated) return <RepoAuthPage mode="login" />;
  const data = resultLed.data;
  return <RepoShell title="Recommendations"><main className="cs-page"><Card className="cs-card mx-auto max-w-4xl p-6 sm:p-8"><p className="cs-kicker text-emerald-700">Completed-result actions</p><h1 className="mt-3 text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl dark:text-white">Recommendations</h1><p className="mt-3 text-base leading-relaxed text-slate-500">Profile-matched actions are selected from your completed AI prediction and transparent baseline. They are planning guidance, not verified emissions reductions.</p>{!data?.available ? <div className="mt-6 rounded-2xl bg-amber-50 p-5 text-sm text-amber-900"><p className="font-semibold">Complete your result first</p><p className="mt-2">{data?.reason || "Loading your completed result…"}</p></div> : <><div className="mt-6 grid gap-3 sm:grid-cols-2"><div className="rounded-xl bg-[#f6f8f7] p-4"><p className="text-xs font-semibold uppercase tracking-[.12em] text-slate-500">Starting AI result</p><p className="mt-2 font-mono text-2xl">{data.predictionKg} kg</p></div><div className="rounded-xl bg-emerald-50 p-4"><p className="text-xs font-semibold uppercase tracking-[.12em] text-emerald-700">Starting baseline</p><p className="mt-2 font-mono text-2xl text-emerald-800">{data.baselineKg} kg</p></div></div><div className="mt-6 grid gap-4 sm:grid-cols-2">{data.recommendations.map(item => <div key={item.key} className="rounded-2xl bg-[#f6f8f7] p-5"><div className="flex justify-between gap-3"><h2 className="font-semibold">{item.title}</h2><span className="text-sm font-semibold text-[#157f54]">−{item.estimatedReductionKg} kg</span></div><p className="mt-2 text-base leading-relaxed text-slate-500">{item.description}</p><p className="mt-3 text-xs font-medium text-[#157f54]">{item.provenance}</p><p className="mt-1 text-xs leading-5 text-slate-500">Why shown: {item.trigger}</p><Button size="sm" className="mt-4 bg-[#157f54] hover:bg-[#106b47]" onClick={() => accept.mutate({ recommendation_key: item.key })} disabled={accept.isPending}>Accept recommendation</Button></div>)}</div></>}{(resultLed.error || accept.error) && <p role="alert" className="mt-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-base text-red-700">{(resultLed.error || accept.error)?.message}</p>}</Card></main></RepoShell>;
}
