import { useState } from "react";
import { ArrowRight, CircleAlert, History, LineChart, RefreshCw, ShieldCheck } from "lucide-react";
import { Link } from "wouter";
import { Bar, BarChart, CartesianGrid, Cell, ErrorBar, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useAuth } from "@/_core/hooks/useAuth";
import { useFastApiQuery } from "@/hooks/useFastApi";
import RepoAuthPage from "@/components/RepoAuthPage";
import RepoShell from "@/components/RepoShell";

export type InsightMode = "forecast" | "history";

function StatusCard({ children }: { children: React.ReactNode }) {
  return <section className="cs-card mt-8 grid min-h-44 place-items-center px-6 py-10 text-center"><div className="max-w-xl">{children}</div></section>;
}

const HISTORY_BAR = "#157f54";
const FORECAST_BAR = "#3b82f6";
const FALLBACK_BAR = "#f59e0b";

const monthLabel = (value: string) => {
  const date = new Date(`${value.length === 7 ? `${value}-01` : value}T00:00:00Z`);
  return date.toLocaleDateString(undefined, { month: "short", year: "2-digit" });
};

export function InsightsWorkspace({ initialMode = "forecast" }: { initialMode?: InsightMode }) {
  const { isAuthenticated, loading } = useAuth();
  const [mode, setMode] = useState<InsightMode>(() => initialMode);
  const forecast = useFastApiQuery<any>(["insights", "forecast"], "/insights/forecast", isAuthenticated && mode === "forecast");
  const history = useFastApiQuery<any[]>(["insights", "history"], "/insights/history", isAuthenticated && mode === "history");

  if (!loading && !isAuthenticated) return <RepoAuthPage mode="login" />;

  const hasRecordedHistory = Boolean(history.data?.length);
  const hasForecastPoints = Boolean(forecast.data?.points?.length);

  // Bar-graph data: completed monthly history followed by the forecast months.
  const engine = forecast.data?.status as string | undefined;
  const barColor = engine === "prophet" ? FORECAST_BAR : engine === "ets" ? FORECAST_BAR : FALLBACK_BAR;
  const chartRows = [
    ...(forecast.data?.history ?? []).map((row: any) => ({
      label: monthLabel(row.ds),
      kg: row.y,
      kind: "history" as const,
      lowerKg: null as number | null,
      upperKg: null as number | null,
    })),
    ...(forecast.data?.points ?? []).map((point: any) => ({
      label: point.date ? monthLabel(point.date) : `+${point.month}m`,
      kg: point.kg,
      kind: "forecast" as const,
      lowerKg: point.lowerKg ?? null,
      upperKg: point.upperKg ?? null,
      errorBar: [Math.max(0, point.kg - (point.lowerKg ?? point.kg)), Math.max(0, (point.upperKg ?? point.kg) - point.kg)],
    })),
  ];

  return <RepoShell><main className="cs-page pb-20">
    <Link href="/" className="inline-flex items-center text-sm font-semibold text-emerald-700 hover:underline dark:text-emerald-400">← Dashboard</Link>
    <section className="mt-4 max-w-3xl">
      <p className="cs-data-label">Personal climate record</p>
      <h1 className="mt-2 text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl dark:text-white">Your Carbon Insights</h1>
      <p className="mt-3 max-w-2xl text-base leading-7 text-slate-600 dark:text-slate-300">Track your recorded history and review a forecast only when your own activity evidence supports one.</p>
    </section>

    <div role="tablist" aria-label="Carbon insights view" className="cs-explore-method-slider cs-workspace-mode-slider mt-9 grid grid-cols-2">
      <button role="tab" aria-selected={mode === "forecast"} onClick={() => setMode("forecast")} className={`cs-workspace-mode-tab ${mode === "forecast" ? "is-active" : ""}`}><LineChart className="mr-2 inline" size={17} />Forecast</button>
      <button role="tab" aria-selected={mode === "history"} onClick={() => setMode("history")} className={`cs-workspace-mode-tab ${mode === "history" ? "is-active" : ""}`}><History className="mr-2 inline" size={17} />History</button>
    </div>

    {mode === "forecast" && <section role="tabpanel" aria-label="Forecast">
      {forecast.isLoading ? <StatusCard><RefreshCw className="mx-auto animate-spin text-emerald-700" size={25} /><p className="mt-3 text-sm font-medium text-slate-600 dark:text-slate-300">Checking your recorded history…</p></StatusCard>
        : forecast.isError ? <StatusCard><CircleAlert className="mx-auto text-amber-600" size={26} /><p className="mt-3 font-semibold text-slate-800 dark:text-white">Forecast is temporarily unavailable.</p><p className="mt-2 text-sm text-slate-500">Your saved history has not been changed. Please try again shortly.</p></StatusCard>
        : !hasForecastPoints ? <StatusCard><p className="text-base font-medium text-slate-500 dark:text-slate-400">Not enough data for forecasting. Run a prediction or baseline first.</p></StatusCard>
        : <section className="cs-card mt-8 p-6 sm:p-8"><div className="flex flex-wrap items-start justify-between gap-4"><div><p className="cs-data-label">{forecast.data?.status === "prophet" ? "Model-based personal history" : "History-building mode"}</p><h2 className="mt-2 text-2xl font-bold tracking-tight text-slate-900 dark:text-white">{forecast.data?.method || "Forecast"}</h2><p className="mt-2 max-w-2xl text-base leading-relaxed text-slate-500 dark:text-slate-400">{forecast.data?.disclaimer}</p></div><span className={`rounded-full px-3 py-1.5 text-xs font-bold ${forecast.data?.status === "prophet" ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300" : "bg-amber-50 text-amber-800 dark:bg-amber-950/40 dark:text-amber-200"}`}>{forecast.data?.status === "prophet" ? "Prophet · 80% interval" : "Directional only"}</span></div><div className="mt-6 grid gap-3 sm:grid-cols-3"><div className="rounded-xl bg-slate-50 p-4 dark:bg-white/5"><p className="text-xs text-slate-500">Completed months</p><p className="mt-1 text-lg font-bold text-slate-900 dark:text-white">{forecast.data?.eligibility.completeMonths ?? 0}/{forecast.data?.eligibility.requiredCompleteMonths ?? 12}</p></div><div className="rounded-xl bg-slate-50 p-4 dark:bg-white/5"><p className="text-xs text-slate-500">Recorded days</p><p className="mt-1 text-lg font-bold text-slate-900 dark:text-white">{forecast.data?.eligibility.distinctActivityDays ?? 0}/{forecast.data?.eligibility.requiredDistinctActivityDays ?? 90}</p></div><div className="rounded-xl bg-slate-50 p-4 dark:bg-white/5"><p className="text-xs text-slate-500">Forecast source</p><p className="mt-1 text-sm font-bold text-slate-900 dark:text-white">{forecast.data?.source || "Personal records"}</p></div></div>
          <div className="mt-8">
            <div className="flex flex-wrap items-center gap-4 text-xs font-semibold text-slate-500">
              <span className="flex items-center gap-1.5"><span className="inline-block h-3 w-3 rounded-sm" style={{ backgroundColor: HISTORY_BAR }} /> Recorded history</span>
              <span className="flex items-center gap-1.5"><span className="inline-block h-3 w-3 rounded-sm" style={{ backgroundColor: barColor }} /> Forecast</span>
              {engine === "prophet" && <span>whiskers = 80% interval</span>}
            </div>
            <div className="mt-3 h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartRows} margin={{ top: 8, right: 8, bottom: 4, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8e5" />
                  <XAxis dataKey="label" tick={{ fontSize: 11 }} interval="preserveStartEnd" minTickGap={8} />
                  <YAxis tick={{ fontSize: 11 }} width={44} unit=" kg" />
                  <Tooltip
                    formatter={(value: number, _name, item: any) => {
                      const row = item?.payload;
                      return [`${value} kg${row?.kind === "forecast" && row?.lowerKg != null ? ` (${row.lowerKg}–${row.upperKg} kg)` : ""}`, row?.kind === "history" ? "Recorded" : "Forecast"];
                    }}
                    labelStyle={{ fontWeight: 700 }}
                  />
                  <Bar dataKey="kg" radius={[3, 3, 0, 0]} maxBarSize={38}>
                    {chartRows.map((row, index) => (
                      <Cell key={index} fill={row.kind === "history" ? HISTORY_BAR : barColor} fillOpacity={row.kind === "history" ? 1 : 0.85} />
                    ))}
                    {engine === "prophet" && <ErrorBar dataKey="errorBar" direction="y" width={4} strokeWidth={1.5} stroke="#334155" />}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3">{forecast.data?.points.map((point: any) => <article key={point.month} className="rounded-xl border border-slate-100 bg-white p-4 dark:border-white/10 dark:bg-white/5"><p className="text-xs text-slate-500">{point.date ? new Date(`${point.date}T00:00:00Z`).toLocaleDateString(undefined, { month: "short", year: "numeric" }) : `Month ${point.month}`}</p><p className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{point.kg} <span className="text-sm font-medium text-slate-400">kg</span></p><p className="mt-1 text-xs text-slate-500">{forecast.data?.status === "prophet" ? `${point.lowerKg}–${point.upperKg} kg interval` : `±${point.uncertainty} kg directional range`}</p></article>)}</div></section>}
    </section>}

    {mode === "history" && <section role="tabpanel" aria-label="History">
      {history.isLoading ? <StatusCard><RefreshCw className="mx-auto animate-spin text-emerald-700" size={25} /><p className="mt-3 text-sm font-medium text-slate-600 dark:text-slate-300">Loading your private history…</p></StatusCard>
        : history.isError ? <StatusCard><CircleAlert className="mx-auto text-amber-600" size={26} /><p className="mt-3 font-semibold text-slate-800 dark:text-white">History is temporarily unavailable.</p><p className="mt-2 text-sm text-slate-500">Your records remain scoped to your account.</p></StatusCard>
        : !hasRecordedHistory ? <StatusCard><History className="mx-auto text-emerald-700" size={28} /><p className="mt-3 text-base font-semibold text-slate-800 dark:text-white">No history entries yet.</p><p className="mt-2 text-sm text-slate-500">Run a prediction or transparent baseline first. New results will appear here only for your signed-in account.</p><Link href="/predict" className="cs-action mt-5 inline-flex items-center text-sm font-bold text-emerald-700 hover:underline dark:text-emerald-300">Start a prediction <ArrowRight className="ml-1" size={15} /></Link></StatusCard>
        : <section className="cs-card mt-8 overflow-hidden"><div className="flex items-start justify-between gap-4 border-b border-slate-100 px-6 py-5 dark:border-white/10"><div><p className="cs-data-label">Private history</p><h2 className="mt-2 text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Your saved results</h2></div><ShieldCheck className="text-emerald-700 dark:text-emerald-300" size={22} /></div><div className="divide-y divide-slate-100 dark:divide-white/10">{history.data?.map((run: any) => <article key={run.id} className="flex flex-wrap items-center justify-between gap-3 px-6 py-4"><div><p className="font-bold capitalize text-slate-900 dark:text-white">{run.runType.replace("_", " ")}</p><p className="mt-1 text-xs text-slate-500">Saved to your authenticated history</p></div><p className="text-lg font-bold text-slate-900 dark:text-white">{run.predictedKg} <span className="text-sm font-medium text-slate-400">kg</span></p></article>)}</div></section>}
    </section>}
  </main></RepoShell>;
}

export default function Insights() { return <InsightsWorkspace />; }
