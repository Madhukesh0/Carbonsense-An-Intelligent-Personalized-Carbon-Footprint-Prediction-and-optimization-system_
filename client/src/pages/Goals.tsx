import { useState } from "react";
import { useAuth } from "@/_core/hooks/useAuth";
import RepoAuthPage from "@/components/RepoAuthPage";
import RepoShell from "@/components/RepoShell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useFastApiMutation, useFastApiQuery } from "@/hooks/useFastApi";

type Goal = { _id?: string; id?: string; baseline_kg: number; target_kg: number; deadline: string; status: string };
type GoalInput = { baseline_kg: number; target_kg: number; deadline: string };

export default function Goals() {
  const auth = useAuth();
  const [baselineKg, setBaselineKg] = useState(684);
  const [targetKg, setTargetKg] = useState(547);
  const goals = useFastApiQuery<Goal[]>(["fastapi", "goals"], "/goals", auth.isAuthenticated);
  const createGoal = useFastApiMutation<{ success: boolean }, GoalInput>("/goals", "POST", [["fastapi", "goals"]]);

  if (!auth.loading && !auth.isAuthenticated) return <RepoAuthPage mode="login" />;
  const saveGoal = () => createGoal.mutate({ baseline_kg: baselineKg, target_kg: targetKg, deadline: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString() });

  return <RepoShell title="Goals"><main className="cs-page"><Card className="cs-card mx-auto max-w-3xl p-6 sm:p-8"><p className="cs-kicker text-emerald-700">Planning target</p><h1 className="mt-3 text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl dark:text-white">Reduction goals</h1><p className="mt-3 text-base leading-relaxed text-slate-500">Set a target below your recorded starting value and review it alongside your history. Saving a new goal supersedes an active one.</p><div className="mt-6 grid gap-3 sm:grid-cols-3"><input aria-label="Goal baseline kilograms" type="number" min="1" value={baselineKg} onChange={event => setBaselineKg(Number(event.target.value))} className="rounded-xl border border-[#dce8e3] px-3 py-2 text-sm" /><input aria-label="Goal target kilograms" type="number" min="1" value={targetKg} onChange={event => setTargetKg(Number(event.target.value))} className="rounded-xl border border-[#dce8e3] px-3 py-2 text-sm" /><Button className="bg-[#157f54] hover:bg-[#106b47]" onClick={saveGoal} disabled={createGoal.isPending}>Save 90-day goal</Button></div>{createGoal.error && <p role="alert" className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-base text-red-700">{createGoal.error.message}</p>}<div className="mt-7 space-y-3">{goals.data?.length ? goals.data.map(goal => <div key={goal._id || goal.id} className="rounded-xl bg-[#e5f7ec] p-4"><div className="flex justify-between gap-4"><span className="font-semibold">{goal.target_kg} kg target</span><span className="text-sm text-slate-500">by {new Date(goal.deadline).toLocaleDateString()}</span></div><p className="mt-2 text-sm text-slate-600">Baseline {goal.baseline_kg} kg · {goal.status}</p></div>) : <p className="rounded-xl bg-[#f6f8f7] p-4 text-sm text-slate-500">No active goal yet.</p>}</div></Card></main></RepoShell>;
}
