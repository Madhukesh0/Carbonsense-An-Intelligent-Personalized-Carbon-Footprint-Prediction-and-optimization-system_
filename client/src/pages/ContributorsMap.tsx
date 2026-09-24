import { useAuth } from "@/_core/hooks/useAuth";
import { useFastApiQuery } from "@/hooks/useFastApi";
import { MapPinned, Users } from "lucide-react";
import { useState } from "react";
import RepoAuthPage from "@/components/RepoAuthPage";
import RepoShell from "@/components/RepoShell";

export default function RepoContributors() {
  const { user, isAuthenticated } = useAuth();
  const hasAggregateRole = ["org_admin", "super_admin"].includes(user?.role || "");
  const [country, setCountry] = useState("");
  const [region, setRegion] = useState<"mixed" | "renewable_heavy" | "">("");
  const query = new URLSearchParams();
  if (country) query.set("country", country);
  if (region) query.set("region", region);
  const contributors = useFastApiQuery<any>(["organization", "contributors", country, region], `/organization/contributors${query.size ? `?${query}` : ""}`, isAuthenticated && hasAggregateRole);
  if (!isAuthenticated) return <RepoAuthPage mode="login" />;
  if (!hasAggregateRole) return <RepoShell><main className="cs-page"><p className="cs-card p-6 text-base leading-relaxed text-muted-foreground">Contributor analytics are available only to authorized organization roles and contain consented aggregate data, never individual histories.</p></main></RepoShell>;
  const countryRows = contributors.data?.countryCounts || [];
  const maxCountry = Math.max(1, ...countryRows.map((row: { value: number }) => row.value));
  return <RepoShell><main className="cs-page"><div className="max-w-3xl"><span className="grid h-12 w-12 place-items-center rounded-2xl bg-primary/10 text-primary dark:bg-primary/20"><MapPinned size={24} /></span><p className="cs-kicker mt-5 text-primary">Contributors map</p><h1 className="mt-2 text-4xl font-extrabold tracking-tight sm:text-5xl text-foreground">Explore consented aggregate coverage.</h1><p className="mt-4 text-base leading-7 text-muted-foreground">This repository-style geographic view uses a privacy-preserving map-equivalent display: regions and countries are aggregated, and it never identifies a person or exposes their individual history.</p></div>
    <section className="cs-card mt-9 grid gap-3 p-5 sm:grid-cols-2"><label className="text-sm font-bold text-secondary-foreground">Country<select value={country} onChange={(event) => setCountry(event.target.value)} className="mt-2 w-full rounded-xl border border-border bg-white px-3 py-2 dark:border-white/15 dark:bg-white/10"><option value="">All consented countries</option>{contributors.data?.countries.map((item: string) => <option key={item} value={item}>{item}</option>)}</select></label><label className="text-sm font-bold text-secondary-foreground">Grid cohort<select value={region} onChange={(event) => setRegion(event.target.value as typeof region)} className="mt-2 w-full rounded-xl border border-border bg-white px-3 py-2 dark:border-white/15 dark:bg-white/10"><option value="">All cohorts</option><option value="mixed">Mixed</option><option value="renewable_heavy">Renewable heavy</option></select></label></section><section className="mt-5 grid gap-5 lg:grid-cols-2"><article className="cs-card p-7"><div className="flex items-center gap-3"><Users className="text-primary" size={22} /><h2 className="font-bold text-foreground">Regional grid cohorts</h2></div><div className="mt-6 space-y-5">{contributors.data?.regions.map((region: any) => <div key={region.region}><div className="flex justify-between text-sm"><span className="capitalize">{region.region.replace("_", " ")}</span><b>{region.value} recorded run{region.value === 1 ? "" : "s"}</b></div><div className="mt-2 h-3 overflow-hidden rounded-full bg-muted dark:bg-white/10"><div className="h-full rounded-full bg-primary/90" style={{ width: `${Math.min(100, region.value ? region.value * 20 : 0)}%` }} /></div></div>)}</div></article><article className="cs-card p-7"><h2 className="font-bold text-foreground">Country coverage</h2><div className="mt-6 space-y-4">{countryRows.length ? countryRows.map((row: any) => <div key={row.country}><div className="flex justify-between text-sm"><span className="capitalize">{row.country}</span><b>{row.value} consenting member{row.value === 1 ? "" : "s"}</b></div><div className="mt-2 h-3 overflow-hidden rounded-full bg-muted dark:bg-white/10"><div className="h-full rounded-full bg-teal-500" style={{ width: `${Math.round(row.value / maxCountry * 100)}%` }} /></div></div>) : <p className="rounded-2xl bg-muted p-4 text-sm text-muted-foreground dark:bg-white/10">No consented country aggregate is available yet.</p>}</div></article></section><p className="mt-6 max-w-3xl text-xs leading-5 text-muted-foreground">{contributors.data?.disclaimer}</p>
  </main></RepoShell>;
}
