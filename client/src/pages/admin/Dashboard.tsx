import { useAuth } from "@/_core/hooks/useAuth";
import RepoOrganizationRecommendations from "@/components/RepoOrganizationRecommendations";
import RepoShell from "@/components/RepoShell";
import { useFastApiQuery } from "@/hooks/useFastApi";
import { BarChart3, Building2, MapPinned, Users } from "lucide-react";
import { useState } from "react";

type AdminDashboardData = {
  members: number;
  runs: number;
  averageKg: number;
  regions: Array<{ region: string; count: number; averageKg: number }>;
  timeline: Array<{ week: string; runs: number; averageKg: number }>;
  disclaimer: string;
};

type ContributorAggregate = {
  countries: string[];
  countryCounts: Array<{ country: string; value: number }>;
  disclaimer: string;
};

type OrganizationSummary = { organizationId: string; members: number; consentingMembers: number };

export default function AdminDashboard() {
  const { user } = useAuth();
  const eligible = ["org_admin", "super_admin"].includes(user?.role || "");
  const [country, setCountry] = useState("");
  const [region, setRegion] = useState<"mixed" | "renewable_heavy" | "">("");
  const filters = new URLSearchParams();
  if (country) filters.set("country", country);
  if (region) filters.set("region", region);
  const contributorsPath = `/organization/contributors${filters.size ? `?${filters.toString()}` : ""}`;
  const dashboard = useFastApiQuery<AdminDashboardData>(["admin", "dashboard"], "/admin/dashboard", eligible);
  const filtered = useFastApiQuery<ContributorAggregate>(["organization", "contributors", country, region], contributorsPath, eligible);
  const organizations = useFastApiQuery<OrganizationSummary[]>(["organization", "summaries"], "/organization/summaries", eligible);

  if (!eligible) {
    return <RepoShell><main className="cs-page"><p className="cs-card p-6 text-base leading-relaxed text-slate-600 dark:text-slate-300">Organization or super-admin access is required for aggregate administration.</p></main></RepoShell>;
  }

  const data = dashboard.data;
  const maxTimeline = Math.max(1, ...(data?.timeline.map((point) => point.runs) || [1]));
  const metrics = [
    { label: "Consenting members", value: data?.members || 0, icon: Users },
    { label: "Saved runs", value: data?.runs || 0, icon: BarChart3 },
    { label: "Average monthly kg", value: data?.averageKg || 0, icon: MapPinned },
  ];

  return <RepoShell><main className="cs-page">
    <section className="cs-hub-head"><div className="max-w-3xl"><span className="grid h-12 w-12 place-items-center rounded-2xl bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300"><Building2 size={24} /></span><p className="cs-data-label mt-5 text-amber-700 dark:text-amber-300">Administrator dashboard</p><h1 className="mt-2 text-4xl font-extrabold tracking-tight sm:text-5xl text-slate-900 dark:text-white">Aggregated platform insights.</h1><p className="mt-4 text-base leading-7 text-slate-600 dark:text-slate-300">Organization metrics with the CarbonSense privacy boundary preserved: every figure uses opt-in aggregate records only.</p></div><aside className="cs-hub-signal"><p className="cs-data-label text-amber-700 dark:text-amber-300">Data boundary</p><p className="mt-3 text-sm font-bold text-slate-900 dark:text-white">Consent before comparison.</p><p className="mt-2 text-xs leading-5 text-slate-500 dark:text-slate-400">No private histories or individual identities are shown in this workspace.</p></aside></section>
    <section className="mt-9 grid gap-4 sm:grid-cols-3">{metrics.map((metric, index) => { const Icon = metric.icon; return <article key={metric.label} className="cs-metric-card cs-card p-6"><div className="flex items-center justify-between"><Icon size={20} className="text-amber-700 dark:text-amber-300" /><span className="font-mono text-[0.62rem] tracking-[0.12em] text-slate-400">0{index + 1}</span></div><p className="mt-5 font-mono text-4xl font-medium tracking-[-.07em] tabular-nums">{metric.value}</p><p className="mt-1 text-sm text-slate-500">{metric.label}</p></article>; })}</section>
    <section className="mt-5 grid gap-5 lg:grid-cols-[1.2fr_.8fr]"><article className="cs-card p-7"><div className="flex items-center justify-between"><h2 className="font-bold text-slate-900 dark:text-white">Weekly aggregate activity</h2><span className="cs-data-label">6-week view</span></div>{data?.runs ? <div className="cs-chart-frame mt-7 flex h-52 items-end gap-3 rounded-2xl p-5">{data.timeline.map((point) => <div key={point.week} className="flex flex-1 flex-col items-center gap-2"><div className="flex h-36 w-full items-end"><div className="cs-chart-bar w-full rounded-t-xl" style={{ height: `${Math.max(6, point.runs / maxTimeline * 100)}%` }} /></div><span className="text-xs font-bold text-slate-500">{point.week}</span><span className="font-mono text-[10px] text-slate-400">{point.runs} run{point.runs === 1 ? "" : "s"}</span></div>)}</div> : <p className="cs-empty-state mt-6 rounded-2xl p-5 text-base leading-relaxed text-slate-500 dark:text-slate-300">No consented aggregate records are available yet. Ask members to opt into aggregate sharing before trends are displayed.</p>}</article><article className="cs-card p-7"><div className="flex items-center justify-between"><h2 className="font-bold text-slate-900 dark:text-white">Regional grid cohorts</h2><span className="cs-data-label">Energy lens</span></div><div className="mt-6 space-y-3">{data?.regions.map((item) => <div key={item.region} className="cs-cohort-card rounded-2xl p-4"><p className="capitalize text-sm font-bold">{item.region.replace("_", " ")}</p><p className="mt-2 font-mono text-2xl font-medium tracking-[-.06em]">{item.averageKg} kg</p><p className="text-xs text-slate-500">{item.count} aggregate record{item.count === 1 ? "" : "s"}</p></div>)}</div></article></section>
    <section className="cs-filter-panel cs-card mt-5 grid gap-4 p-5 sm:grid-cols-2"><label className="cs-filter-label text-slate-700 dark:text-slate-200">Filter country<select value={country} onChange={(event) => setCountry(event.target.value)} className="cs-select mt-2 w-full rounded-xl border px-3 py-2.5 font-sans text-sm font-semibold text-slate-700 outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 dark:text-slate-200"><option value="">All consented countries</option>{filtered.data?.countries.map((item) => <option key={item} value={item}>{item}</option>)}</select></label><label className="cs-filter-label text-slate-700 dark:text-slate-200">Filter grid cohort<select value={region} onChange={(event) => setRegion(event.target.value as typeof region)} className="cs-select mt-2 w-full rounded-xl border px-3 py-2.5 font-sans text-sm font-semibold text-slate-700 outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 dark:text-slate-200"><option value="">All cohorts</option><option value="mixed">Mixed</option><option value="renewable_heavy">Renewable heavy</option></select></label></section>
    <section className="cs-card mt-5 p-7"><div className="flex items-center justify-between"><h2 className="font-bold text-slate-900 dark:text-white">Country coverage</h2><span className="cs-data-label">Aggregate only</span></div><div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{filtered.data?.countryCounts.length ? filtered.data.countryCounts.map((item) => <div key={item.country} className="cs-chart-frame rounded-2xl p-4"><p className="font-bold">{item.country}</p><p className="mt-3 font-mono text-2xl font-medium tracking-[-.06em]">{item.value}</p><p className="mt-1 text-sm text-slate-500">consenting member{item.value === 1 ? "" : "s"}</p></div>) : <p className="cs-empty-state rounded-2xl p-4 text-sm text-slate-500 dark:text-slate-300">No consented country aggregate is available for this filter.</p>}</div><p className="mt-6 text-xs leading-5 text-slate-500">{filtered.data?.disclaimer || data?.disclaimer}</p></section>
    <section className="cs-card mt-5 p-7"><div className="flex items-center justify-between"><h2 className="font-bold text-slate-900 dark:text-white">Organization summaries</h2><span className="cs-data-label">Member scope</span></div><div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{organizations.data?.length ? organizations.data.map((organization) => <div key={organization.organizationId} className="cs-cohort-card rounded-2xl p-5"><p className="font-bold">{organization.organizationId}</p><p className="mt-3 text-sm text-slate-600 dark:text-slate-300">{organization.members} member{organization.members === 1 ? "" : "s"} · {organization.consentingMembers} opted into aggregates</p></div>) : <p className="cs-empty-state rounded-2xl p-4 text-sm text-slate-500 dark:text-slate-300">No organization summary is available yet.</p>}</div></section>
    <RepoOrganizationRecommendations />
  </main></RepoShell>;
}
