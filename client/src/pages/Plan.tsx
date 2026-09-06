import { useAuth } from "@/_core/hooks/useAuth";
import RepoAuthPage from "@/components/RepoAuthPage";
import RepoShell from "@/components/RepoShell";
import { useFastApiMutation, useFastApiQuery } from "@/hooks/useFastApi";
import { ArrowRight, Route } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "wouter";

type StartingPoint = "ai_estimate" | "transparent_baseline";

function NumberControl({ label, value, onChange, min, max, suffix = "" }: { label: string; value: number; onChange: (value: number) => void; min: number; max: number; suffix?: string }) {
  return <label className="block rounded-2xl border border-emerald-950/10 bg-white/80 p-5 shadow-sm dark:border-white/10 dark:bg-white/5"><span className="flex justify-between gap-4"><span className="cs-range-label text-slate-600 dark:text-slate-300">{label}</span><span className="font-mono text-sm font-medium text-emerald-700 dark:text-emerald-400">{value}{suffix}</span></span><input className="cs-range mt-5 w-full" type="range" value={value} min={min} max={max} onChange={event => onChange(Number(event.target.value))} /></label>;
}

function StartingPointControl({ value, onChange, predictionKg, baselineKg }: { value: StartingPoint; onChange: (value: StartingPoint) => void; predictionKg: number; baselineKg: number }) {
  return <label className="block rounded-2xl border border-emerald-950/10 bg-white/80 p-5 shadow-sm dark:border-white/10 dark:bg-white/5"><span className="cs-range-label text-slate-600 dark:text-slate-300">Compare against</span><select aria-label="Compare against" value={value} onChange={event => onChange(event.target.value as StartingPoint)} className="mt-3 w-full rounded-xl border border-emerald-950/15 bg-white px-3 py-2.5 text-sm font-semibold text-slate-900 outline-none focus:ring-2 focus:ring-emerald-600 dark:border-white/15 dark:bg-slate-900 dark:text-white"><option value="ai_estimate">AI estimate · {predictionKg} kg</option><option value="transparent_baseline">Transparent baseline · {baselineKg} kg</option></select><p className="mt-3 text-xs leading-5 text-slate-500 dark:text-slate-400">The scenario uses the selected method only. CarbonSense does not average the two estimates.</p></label>;
}

function Metric({ label, value, emphasis = false }: { label: string; value: string; emphasis?: boolean }) { return <div className={`rounded-2xl p-5 ${emphasis ? "cs-result-card" : "cs-chart-frame"}`}><p className="cs-data-label text-slate-500">{label}</p><p className="mt-3 font-mono text-2xl font-medium">{value}</p></div>; }

export function PlanningWorkspace() {
  const { isAuthenticated } = useAuth();
  const whatIf = useFastApiMutation<any, { input: Record<string, unknown>; changes: Record<string, number>; starting_point: StartingPoint }>("/planning/what-if");
  const completedResult = useFastApiQuery<any>(["planning", "latest-completed"], "/planning/latest-completed", isAuthenticated);
  const [startingPoint, setStartingPoint] = useState<StartingPoint>("ai_estimate");
  const [distance, setDistance] = useState(300);
  const [clothes, setClothes] = useState(2);
  const profile = completedResult.data?.available ? completedResult.data.profile : null;
  const predictionKg = completedResult.data?.predictionKg ?? 0;
  const baselineKg = completedResult.data?.baselineKg ?? 0;
  useEffect(() => { if (profile) { setDistance(profile.vehicle_monthly_distance_km); setClothes(profile.how_many_new_clothes_monthly); } }, [profile]);
  if (!isAuthenticated) return <RepoAuthPage mode="login" />;
  const gate = () => completedResult.isLoading ? <p className="mt-7 rounded-2xl bg-emerald-50 p-5 text-sm text-emerald-800 dark:bg-emerald-950 dark:text-emerald-100">Loading your completed AI prediction and transparent baseline…</p> : !profile ? <div className="mt-7 rounded-2xl border border-amber-200 bg-amber-50 p-6 text-base leading-relaxed text-amber-900"><p className="font-bold">Complete your result first</p><p className="mt-2">{completedResult.data?.reason || "Complete an AI prediction and transparent baseline before opening this planning tool."}</p><Link href="/predict" className="cs-action mt-5 inline-flex items-center rounded-xl bg-emerald-700 px-4 py-2.5 font-bold text-white">Calculate AI prediction + baseline <ArrowRight size={16} className="ml-2" /></Link></div> : null;
  return (
    <RepoShell>
      <main className="cs-page cs-plan-page">
        <Link href="/" className="inline-flex items-center text-sm font-semibold text-emerald-700 hover:underline dark:text-emerald-400">← Dashboard</Link>
        <section className="mt-4 max-w-3xl">
          <p className="cs-data-label">Planning workspace</p>
          <h1 className="mt-2 text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl dark:text-white">What-if Simulator</h1>
          <p className="mt-3 text-base leading-7 text-slate-600 dark:text-slate-300">
            Use your completed result as the read-only starting point, change one habit at a time,
            and see how the selected estimate responds. For your highest-impact actions, see{" "}
            <Link href="/result-recommendations" className="font-semibold text-emerald-700 hover:underline dark:text-emerald-400">your recommendations</Link>.
          </p>
        </section>
        <section className="cs-form-surface cs-card cs-plan-tool-shell mt-8 p-6 sm:p-8">
          <div className="flex flex-wrap items-start justify-between gap-4 border-b border-emerald-950/10 pb-5 dark:border-white/10">
            <div>
              <p className="cs-data-label">What-if Simulator</p>
              <h2 className="mt-2 text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Compare a selected lifestyle scenario.</h2>
              <p className="mt-2 max-w-2xl text-base leading-relaxed text-slate-600 dark:text-slate-300">Use a completed result as your read-only starting point and compare the changes you select.</p>
            </div>
            <span className="rounded-full bg-emerald-100 px-3 py-1.5 font-mono text-xs font-bold text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">WHAT-IF</span>
          </div>
          {gate() ?? (
            <>
              <div className="cs-whatif-lifestyle-grid cs-whatif-lifestyle-grid--single mt-5">
                <article className="cs-card cs-whatif-lifestyle-card cs-whatif-lifestyle-modified">
                  <p className="cs-data-label">Modified Lifestyle</p>
                  <h3 className="mt-2 text-lg font-bold text-slate-900 dark:text-white">Set the scenario changes</h3>
                  <div className="mt-5 grid gap-4">
                    <StartingPointControl value={startingPoint} onChange={setStartingPoint} predictionKg={predictionKg} baselineKg={baselineKg} />
                    <NumberControl label="Monthly vehicle distance" value={distance} onChange={setDistance} min={0} max={1200} suffix=" km" />
                    <NumberControl label="New clothing items" value={clothes} onChange={setClothes} min={0} max={20} suffix=" / month" />
                  </div>
                </article>
              </div>
              <button
                disabled={whatIf.isPending}
                onClick={() => whatIf.mutate({ input: profile!, changes: { vehicle_monthly_distance_km: distance, how_many_new_clothes_monthly: clothes }, starting_point: startingPoint })}
                className="cs-plan-primary-action cs-action mt-8 inline-flex items-center justify-center rounded-xl bg-emerald-700 px-5 py-3 text-sm font-bold text-white shadow-md shadow-emerald-800/20 disabled:opacity-60"
              >
                Compare with selected result <ArrowRight size={16} className="ml-2" />
              </button>
              {whatIf.data && (
                <div className="mt-8 grid grid-cols-2 gap-4">
                  <Metric label={whatIf.data.startingPointLabel} value={`${whatIf.data.before} kg`} />
                  <Metric label={`Scenario ${whatIf.data.startingPointLabel.toLowerCase()}`} value={`${whatIf.data.after} kg`} emphasis />
                </div>
              )}
              {whatIf.data && (
                <p className="mt-4 rounded-xl bg-emerald-50 p-4 text-sm text-emerald-900 dark:bg-emerald-950 dark:text-emerald-100">{whatIf.data.interpretation}</p>
              )}
            </>
          )}
          {whatIf.error && <p className="mt-5 rounded-xl bg-red-50 p-3 text-sm text-red-700 dark:bg-red-950 dark:text-red-200">{whatIf.error.message}</p>}
          {completedResult.error && <p className="mt-5 rounded-xl bg-red-50 p-3 text-sm text-red-700 dark:bg-red-950 dark:text-red-200">{completedResult.error.message}</p>}
        </section>
      </main>
    </RepoShell>
  );
}

export default function Plan() { return <PlanningWorkspace />; }
