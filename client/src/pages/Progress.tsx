import { useAuth } from "@/_core/hooks/useAuth";
import { useFastApiQuery } from "@/hooks/useFastApi";
import { Award, Flame, Globe2, ShieldCheck, Sparkles, Trophy, UsersRound } from "lucide-react";
import { useState } from "react";
import { Link } from "wouter";
import RepoAuthPage from "@/components/RepoAuthPage";
import ContributorAggregateMap from "@/components/ContributorAggregateMap";
import RepoShell from "@/components/RepoShell";
import { BackToTop } from "@/components/BackToTop";
import { BadgeCard } from "@/components/BadgeCard";
import { ScoreGauge } from "@/components/ScoreGauge";
import { StreakCalendar } from "@/components/StreakCalendar";

type ProgressMode = "quests" | "contributors";
type ContributorRow = { country: string; value: number };

export default function RepoProgress() {
  const { user, isAuthenticated } = useAuth();
  // Contributor analytics are an organization-only surface: individual
  // accounts never see the section or the toggle.
  const canViewContributors = ["org_admin", "super_admin"].includes(user?.role || "");
  const [mode, setMode] = useState<ProgressMode>(() => canViewContributors ? "contributors" : "quests");
  const [country, setCountry] = useState("");
  const [region, setRegion] = useState<"mixed" | "renewable_heavy" | undefined>(undefined);
  const query = new URLSearchParams();
  if (country) query.set("country", country);
  if (region) query.set("region", region);
  const contributorPath = `/organization/contributors${query.size ? `?${query.toString()}` : ""}`;
  const questSummary = useFastApiQuery<any>(["activity", "quest-summary"], "/activity/quest-summary", isAuthenticated);
  const contributors = useFastApiQuery<any>(["organization", "contributors", country, region], contributorPath, isAuthenticated && canViewContributors && mode === "contributors");

  if (!isAuthenticated) return <RepoAuthPage mode="login" />;

  const summary = questSummary.data;
  const countryRows = contributors.data?.countryCounts || [];
  const consentedParticipantCount = countryRows.reduce((sum: number, row: ContributorRow) => sum + row.value, 0);
  const countryCount = countryRows.length;
  const hasActiveFilter = Boolean(country || region);
  const resetFilters = () => {
    setCountry("");
    setRegion(undefined);
  };
  const showContributors = canViewContributors && mode === "contributors";
  const showQuests = !showContributors;

  return (
    <RepoShell>
      <main className="cs-page cs-progress-page">
        <Link href="/" className="inline-flex items-center text-sm font-semibold text-emerald-700 hover:underline dark:text-emerald-300">← Dashboard</Link>

        <section className="cs-progress-heading mt-5">
          <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl dark:text-white">Your Progress</h1>
          <p className="mt-3 max-w-2xl text-base leading-7 text-slate-600 dark:text-slate-300">
            {canViewContributors
              ? "Track recorded participation, build meaningful habits, and explore contributor patterns only where aggregate sharing is enabled."
              : "Track recorded participation, build meaningful habits, and watch your recognition grow from real records."}
          </p>
        </section>

        <section className="cs-progress-overview cs-card mt-8" aria-labelledby="progress-overview-title">
          <span className="cs-progress-overview-icon"><Trophy size={24} /></span>
          <div><h2 id="progress-overview-title" className="text-xl font-bold tracking-[-0.04em] text-slate-900 dark:text-white">Level up your sustainability</h2><p className="mt-1 text-base leading-relaxed text-slate-500 dark:text-slate-400">{canViewContributors ? "Earn recognition from recorded participation, maintain your engagement streak, and explore consent-filtered aggregate patterns." : "Earn recognition from recorded participation and maintain your engagement streak."}</p></div>
        </section>

        {canViewContributors && (
          <div className="cs-progress-switcher mt-7" role="tablist" aria-label="Progress views">
            <button type="button" role="tab" aria-selected={mode === "quests"} aria-controls="progress-quests-panel" onClick={() => setMode("quests")} className={`cs-progress-tab ${showQuests ? "is-active" : ""}`}><Award size={16} aria-hidden="true" /> Quests &amp; badges</button>
            <button type="button" role="tab" aria-selected={mode === "contributors"} aria-controls="progress-contributors-panel" onClick={() => setMode("contributors")} className={`cs-progress-tab ${showContributors ? "is-active" : ""}`}><Globe2 size={16} aria-hidden="true" /> Contributors</button>
          </div>
        )}

        {showQuests ? (
          <section id="progress-quests-panel" role="tabpanel" className="mt-8">
            <section className="cs-progress-celebrate cs-card" aria-labelledby="progress-intro-title">
              <div className="cs-progress-celebrate-icon"><Trophy size={25} /></div>
              <div><p className="cs-data-label">CarbonQuest</p><h2 id="progress-intro-title" className="mt-1 text-xl font-bold tracking-[-0.04em] text-slate-900 dark:text-white">Make consistent climate participation visible.</h2><p className="mt-2 text-base leading-relaxed text-slate-600 dark:text-slate-300">Recognition reflects recorded participation and administrator-verified action completion. It does not prove real-world emissions reductions.</p></div>
            </section>
            <div className="mt-5 grid gap-5 md:grid-cols-3">
              <article className="cs-progress-stat cs-card"><ScoreGauge score={summary?.score ?? 0} maximum={1000} label="recorded points" /><p className="cs-data-label mt-5">CarbonQuest score</p><p className="mt-2 text-5xl font-bold tracking-[-0.07em] text-slate-900 dark:text-white">{summary?.score ?? 0}</p><p className="mt-2 text-base leading-relaxed text-slate-500 dark:text-slate-400">Recorded participation points</p></article>
              <article className="cs-progress-stat cs-card"><span className="cs-progress-stat-icon cs-progress-stat-icon--amber"><Flame size={24} /></span><p className="cs-data-label mt-5">Day streak</p><p className="mt-2 text-5xl font-bold tracking-[-0.07em] text-slate-900 dark:text-white">{summary?.streak ?? 0}</p><div className="mt-4"><StreakCalendar activeDays={Array.from({ length: Math.min(28, summary?.streak ?? 0) }, (_, index) => index + 1)} /></div><p className="mt-3 text-base leading-relaxed text-slate-500 dark:text-slate-400">Recorded engagement points in sequence</p></article>
              <article className="cs-progress-stat cs-card"><p className="cs-data-label">Score basis</p><div className="mt-5 space-y-4"><div className="cs-progress-score-row"><span>Recorded estimates</span><b>{summary?.score ?? 0} points</b><i /></div><div className="cs-progress-score-row"><span>Verified actions</span><b>Included when verified</b><i /></div><div className="cs-progress-score-row"><span>Recognition</span><b>{summary?.badges?.length ?? 0} badge{summary?.badges?.length === 1 ? "" : "s"}</b><i /></div></div></article>
            </div>
              <article className="cs-card mt-5 p-6 sm:p-7"><div className="flex flex-wrap items-start justify-between gap-4"><div><p className="cs-data-label">Badges</p><h2 className="mt-2 text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Recognition from real records.</h2></div><Sparkles className="text-emerald-600 dark:text-emerald-300" size={23} aria-hidden="true" /></div>{summary?.badges?.length ? <div className="mt-6 grid gap-3 sm:grid-cols-2">{summary.badges.map((badge: string) => <BadgeCard key={badge} label={badge} detail="Recognition is based on recorded participation or administrator-verified action completion." />)}</div> : <div className="cs-progress-empty mt-6"><Award size={21} aria-hidden="true" /><div><p className="font-bold text-slate-900 dark:text-white">Your first recognition is waiting.</p><p className="mt-1 text-base leading-relaxed text-slate-500 dark:text-slate-400">Complete an estimate or receive a verified action completion to unlock a badge.</p></div></div>}<p className="mt-6 text-xs leading-5 text-slate-500 dark:text-slate-400">{summary?.disclaimer || "Points are available only when secure activity storage is available."}</p></article>
          </section>
        ) : (
          <section id="progress-contributors-panel" role="tabpanel" className="mt-12">
            <div className="cs-reference-contributors-heading"><span className="cs-progress-contributors-icon"><Globe2 size={28} /></span><div><h2 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Contributors Around the World</h2><p className="mt-3 text-base leading-7 text-slate-600 dark:text-slate-300">View consented aggregate participation across {countryCount} countr{countryCount === 1 ? "y" : "ies"}. Individual histories and member names are never shown.</p></div></div>
            <div className="cs-contributor-filter-row mt-7"><button type="button" onClick={resetFilters} className={`cs-contributor-filter-all ${!hasActiveFilter ? "is-active" : ""}`}><Globe2 size={15} /> All <span>{consentedParticipantCount}</span></button><label>Country<select value={country} onChange={(event) => setCountry(event.target.value)} className="cs-select"><option value="">All countries</option>{contributors.data?.countries.map((item: string) => <option key={item} value={item}>{item}</option>)}</select></label><label>Grid cohort<select value={region || ""} onChange={(event) => setRegion(event.target.value ? event.target.value as "mixed" | "renewable_heavy" : undefined)} className="cs-select"><option value="">All cohorts</option><option value="mixed">Mixed grid</option><option value="renewable_heavy">Renewable-heavy grid</option></select></label></div>
            <div className="mt-6 grid gap-5 lg:grid-cols-[1.25fr_.75fr]">
              <article className="cs-contributor-map-card cs-card p-6 sm:p-7"><div className="flex items-start justify-between gap-4"><div><p className="cs-data-label">Aggregate contributor map</p><h3 className="mt-2 text-xl font-bold tracking-[-0.04em] text-slate-900 dark:text-white">Country coverage</h3></div><ShieldCheck className="text-emerald-700 dark:text-emerald-300" size={21} aria-hidden="true" /></div><ContributorAggregateMap countryRows={countryRows} onSelectCountry={setCountry} /><div className="cs-map-legend mt-5"><span>Fewer</span><i /><i /><i /><i /><i /><span>More</span></div><p className="mt-5 text-xs leading-5 text-slate-500 dark:text-slate-400">Zoom and pan to examine country-level aggregate coverage. The consent-filtered view refreshes while open, so new country coverage can appear without revealing an individual location or private activity history.</p></article>
              <aside className="cs-card p-6 sm:p-7"><div className="flex items-center justify-between gap-3"><div><p className="cs-data-label">Contributors</p><h3 className="mt-2 text-xl font-bold tracking-[-0.04em] text-slate-900 dark:text-white">Aggregate cohort</h3></div><span className="text-sm text-slate-500 dark:text-slate-400">{consentedParticipantCount} shown</span></div>{countryRows.length ? <div className="mt-6 space-y-3">{countryRows.map((row: ContributorRow) => <button type="button" key={row.country} onClick={() => setCountry(row.country)} className="cs-contributor-row"><UsersRound size={17} /><span>{row.country}</span><b>{row.value}</b></button>)}</div> : <div className="cs-contributors-empty"><Globe2 size={35} /><p className="mt-4 font-bold text-slate-900 dark:text-white">No contributors found for this selection.</p><p className="mt-2 text-base leading-relaxed text-slate-500 dark:text-slate-400">Coverage appears only when members consent to aggregate sharing.</p></div>}<div className="mt-7 border-t border-emerald-950/10 pt-5 dark:border-white/10"><Link href="/quests" className="cs-action inline-flex items-center text-sm font-bold text-emerald-700 hover:underline dark:text-emerald-300">View privacy-aware leaderboard →</Link></div></aside>
            </div>
            <p className="mt-6 text-xs leading-5 text-slate-500 dark:text-slate-400">{contributors.data?.disclaimer || "Aggregate records are loading."}</p>
          </section>
        )}
      </main>
      <BackToTop />
    </RepoShell>
  );
}
