import { useAuth } from "@/_core/hooks/useAuth";
import RepoAuthPage from "@/components/RepoAuthPage";
import RepoShell from "@/components/RepoShell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ArrowRight, Building2, Sparkles, Target } from "lucide-react";
import { useMemo, useState } from "react";
import { Link, useLocation } from "wouter";
import { useFastApiQuery } from "@/hooks/useFastApi";

type Recommendation = {
  key: string;
  title: string;
  description: string;
  estimatedReductionKg: number;
  provenance: string;
  trigger: string;
  impactBasis?: string | null;
  impactRank?: number;
  impactShareOfBaselinePct?: number | null;
  source?: string;
  shapContributionKg?: number;
};
type ResultLed = {
  available: boolean;
  reason: string | null;
  predictionKg: number | null;
  baselineKg: number | null;
  recommendations: Recommendation[];
  organizationRecommendations?: Recommendation[];
  basedOn?: { runId: string; runCreatedAt: string; rankingBasis: string };
};

function RecCard({ item, accent, planBadge }: { item: Recommendation; accent: string; planBadge?: string }) {
  const isTopRank = item.impactRank === 1;
  return (
    <div className={`rounded-2xl p-5 ${isTopRank ? "bg-emerald-50 ring-1 ring-emerald-200 dark:bg-emerald-950/40 dark:ring-emerald-800" : "bg-[#f6f8f7] dark:bg-emerald-950/30"}`}>
      <div className="flex items-start justify-between gap-3">
        <h2 className="font-semibold">
          {planBadge && (
            <span className="mr-2 inline-flex items-center rounded-full bg-[#3b5bdb] px-2 py-0.5 text-xs font-bold text-white">
              {planBadge}
            </span>
          )}
          {isTopRank && (
            <span className="mr-2 inline-flex items-center rounded-full bg-[#157f54] px-2 py-0.5 text-xs font-bold text-white">
              Highest impact
            </span>
          )}
          {item.title}
        </h2>
        <span className="shrink-0 text-sm font-semibold" style={{ color: accent }}>
          {item.estimatedReductionKg > 0 ? `−${item.estimatedReductionKg} kg` : "—"}
        </span>
      </div>
      <p className="mt-2 text-base leading-relaxed text-slate-500">{item.description}</p>
      <p className="mt-3 text-xs font-medium text-[#157f54]">{item.provenance}</p>
      <p className="mt-1 text-xs leading-5 text-slate-500">Why shown: {item.trigger}</p>
      {item.impactBasis && (
        <p className="mt-2 rounded-lg bg-white/70 px-3 py-2 font-mono text-[11px] leading-4 text-slate-500 dark:bg-black/20">
          Estimate basis: {item.impactBasis}
        </p>
      )}
      {typeof item.impactShareOfBaselinePct === "number" && item.impactShareOfBaselinePct > 0 && (
        <div className="mt-3">
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
            <div
              className="h-full rounded-full"
              style={{
                width: `${Math.min(100, Math.max(3, item.impactShareOfBaselinePct * 2))}%`,
                backgroundColor: accent,
              }}
            />
          </div>
          <p className="mt-1 text-[11px] text-slate-500">
            ≈{item.impactShareOfBaselinePct}% of your baseline result
          </p>
        </div>
      )}
      {item.source === "organization" ? (
        <p className="mt-2 inline-flex items-center gap-1 rounded-full bg-[#eef2fb] px-2.5 py-1 text-xs font-semibold text-[#3b5bdb] dark:bg-[#3b5bdb]/20 dark:text-[#a5b8f5]">
          <Building2 size={12} /> Organization recommendation
        </p>
      ) : (
        typeof item.shapContributionKg === "number" && (
          <p className="mt-2 inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300">
            <Sparkles size={12} /> Your model contribution: {item.shapContributionKg > 0 ? "+" : ""}
            {item.shapContributionKg} kg
          </p>
        )
      )}
    </div>
  );
}

export default function ResultRecommendations() {
  const auth = useAuth();
  const [location] = useLocation();
  const [goalPercent, setGoalPercent] = useState(0);
  const data = useFastApiQuery<ResultLed>(["fastapi", "recommendations", "result-led"], "/recommendations/result-led", auth.isAuthenticated);
  if (!auth.loading && !auth.isAuthenticated) return <RepoAuthPage mode="login" />;
  const d = data.data;
  const modelRecs = d?.recommendations ?? [];
  const orgRecs = d?.organizationRecommendations ?? [];

  // Goal plan: greedily take impact-ranked actions top-down until the target
  // is met. The per-action numbers are transparent band-delta planning
  // estimates — they guide sequencing, they do not literally add up in the
  // real world, and nothing here is a verified reduction.
  const baselineKg = d?.baselineKg ?? 0;
  const goalTargetKg = goalPercent > 0 && baselineKg > 0 ? Math.round(baselineKg * goalPercent / 100) : 0;
  const plan = useMemo(() => {
    if (goalTargetKg <= 0) return { inPlanKeys: new Set<string>(), plannedTotal: 0, met: false };
    let running = 0;
    const inPlanKeys = new Set<string>();
    for (const rec of modelRecs) {
      if (running >= goalTargetKg) break;
      inPlanKeys.add(rec.key);
      running += rec.estimatedReductionKg ?? 0;
    }
    return { inPlanKeys, plannedTotal: Math.round(running * 10) / 10, met: running >= goalTargetKg };
  }, [goalTargetKg, JSON.stringify(modelRecs.map(r => [r.key, r.estimatedReductionKg]))]);
  return (
    <RepoShell title="Your recommendations">
      <main className="cs-page mx-auto max-w-4xl">
        <Card className="cs-card border-0 p-7 sm:p-9">
          <p className="cs-kicker text-emerald-700">After your prediction</p>
          <h1 className="mt-3 text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl dark:text-white">
            Your personalized recommendations.
          </h1>
          <p className="mt-3 text-base leading-relaxed text-slate-500">
            Recalculated from your latest submitted result: every approved action is
            re-scored against the answers you just gave, and the highest-impact levers
            come first. Organization assignments appear separately below. These are
            planning guidance, not verified emissions reductions.
          </p>
          {d?.available && (
            <div className="mt-5 grid gap-3 sm:grid-cols-2">
              <div className="rounded-xl bg-[#f6f8f7] p-4 dark:bg-emerald-950/30">
                <p className="text-xs font-semibold uppercase tracking-[.12em] text-slate-500">Your AI result</p>
                <p className="mt-2 font-mono text-2xl">{d.predictionKg} kg</p>
              </div>
              <div className="rounded-xl bg-emerald-50 p-4 dark:bg-emerald-950/40">
                <p className="text-xs font-semibold uppercase tracking-[.12em] text-emerald-700">Transparent baseline</p>
                <p className="mt-2 font-mono text-2xl text-emerald-800">{d.baselineKg} kg</p>
              </div>
            </div>
          )}
          {!d?.available ? (
            <div className="mt-6 rounded-2xl bg-amber-50 p-5 text-sm text-amber-900 dark:bg-amber-950/40 dark:text-amber-200">
              <p className="font-semibold">Complete a prediction first</p>
              <p className="mt-2">{d?.reason || "Loading your completed result…"}</p>
              <Link href="/predict">
                <Button size="sm" className="mt-4 bg-[#157f54] hover:bg-[#106b47]">
                  Go to prediction <ArrowRight size={14} className="ml-1" />
                </Button>
              </Link>
            </div>
          ) : (
            <>
              <h2 className="mt-8 text-xl font-semibold">Plan to my goal</h2>
              <p className="mt-1 text-sm text-slate-500">
                Pick a reduction goal and the highest-impact actions are selected for you,
                top-down from the ranked list, until the goal is met.
              </p>
              <div className="mt-4 rounded-2xl bg-[#f6f8f7] p-5 dark:bg-emerald-950/30">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <label htmlFor="goal-slider" className="text-sm font-semibold text-slate-700 dark:text-slate-200">
                    {goalPercent === 0 ? "Set a reduction goal (of your baseline)" : `Goal: reduce ${goalPercent}% of your baseline`}
                  </label>
                  <span className="rounded-full bg-emerald-100 px-3 py-1 font-mono text-xs font-bold text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
                    {goalPercent === 0 ? "No goal set" : `${goalTargetKg} kg target`}
                  </span>
                </div>
                <input
                  id="goal-slider"
                  aria-label={`Reduction goal, ${goalPercent} percent of baseline`}
                  className="cs-range mt-4 w-full"
                  type="range"
                  min={0}
                  max={50}
                  step={5}
                  value={goalPercent}
                  onChange={event => setGoalPercent(Number(event.target.value))}
                />
                <div className="mt-2 flex justify-between text-xs text-slate-400">
                  <span>None</span><span>50%</span>
                </div>
                {goalPercent > 0 && (
                  plan.met ? (
                    <p className="mt-4 rounded-xl bg-emerald-50 p-4 text-sm leading-6 text-emerald-900 dark:bg-emerald-950 dark:text-emerald-100">
                      <Target size={15} className="mr-1 inline" />
                      Accepting the <strong>{plan.inPlanKeys.size} highlighted action{plan.inPlanKeys.size === 1 ? "" : "s"}</strong> targets
                      about <strong>−{plan.plannedTotal} kg</strong> against your {goalTargetKg} kg goal
                      ({goalPercent}% of your {baselineKg} kg baseline). Band-delta estimates guide sequencing —
                      they are planning guidance, not a guaranteed or verified reduction.
                    </p>
                  ) : (
                    <p className="mt-4 rounded-xl bg-amber-50 p-4 text-sm leading-6 text-amber-900 dark:bg-amber-950 dark:text-amber-200">
                      Every available action combined targets about −{plan.plannedTotal} kg — short of your
                      {` ${goalTargetKg} kg`} goal. Set a lower goal, or use the What-if simulator to explore larger
                      lifestyle changes.
                    </p>
                  )
                )}
              </div>

              <h2 className="mt-8 text-xl font-semibold">Model-ranked actions</h2>
              {d.basedOn?.rankingBasis && (
                <p className="mt-1 text-sm text-slate-500">{d.basedOn.rankingBasis}.</p>
              )}
              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                {modelRecs.map(item => (
                  <RecCard
                    key={item.key}
                    item={item}
                    accent="#157f54"
                    planBadge={plan.inPlanKeys.has(item.key) ? `In goal plan · #${modelRecs.indexOf(item) + 1}` : undefined}
                  />
                ))}
              </div>
              {orgRecs.length > 0 && (
                <>
                  <h2 className="mt-8 text-xl font-semibold">From your organization</h2>
                  <div className="mt-4 grid gap-4 sm:grid-cols-2">
                    {orgRecs.map((item, idx) => <RecCard key={`org-${idx}`} item={item} accent="#3b5bdb" />)}
                  </div>
                </>
              )}
              <div className="mt-8 flex flex-wrap gap-3">
                <Link href="/recommendations">
                  <Button variant="outline" className="border-emerald-700 text-emerald-800 hover:bg-emerald-50">
                    Accept & track in My Recommendations
                  </Button>
                </Link>
                <Link href="/whatif">
                  <Button variant="outline" className="border-emerald-700 text-emerald-800 hover:bg-emerald-50">
                    Test a What-if scenario <ArrowRight size={14} className="ml-1" />
                  </Button>
                </Link>
              </div>
            </>
          )}
          {data.error && <p role="alert" className="mt-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-base text-red-700">{data.error?.message}</p>}
        </Card>
      </main>
    </RepoShell>
  );
}
