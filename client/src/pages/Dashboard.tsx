import { useAuth } from "@/_core/hooks/useAuth";
import { useFastApiQuery } from "@/hooks/useFastApi";
import { fastApi } from "@/lib/fastapiClient";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowRight, Bell, Building2, CheckCircle2, Compass, Flame, Hourglass, LineChart, Sparkles, Target, Trophy, UserPlus, X, XCircle } from "lucide-react";
import { Link } from "wouter";
import RepoShell from "@/components/RepoShell";

type OrgData = { id: string; name: string; inviteCode: string | null; memberCount: number; yourRole: string };
type QuestData = { score: number; streak: number; badges: string[] };
type Reminder = { id: string; title: string; message: string; reminderType: string; status: string; senderName: string; createdAt: string };
type HistoryItem = { id: string; created_at: string };
type JoinRequestInfo = { id: string; organizationId: string; organizationName: string; status: "pending" | "approved" | "rejected"; source: string | null; createdAt: string; decidedAt: string | null };
type PendingJoinRequest = { id: string; userId: string; userName: string | null; userEmail: string | null; organizationId: string; status: string; source: string | null; createdAt: string };

function ReminderBanner() {
  const auth = useAuth();
  const reminders = useFastApiQuery<Reminder[]>(["fastapi", "organization", "reminders"], "/organization/reminders", auth.isAuthenticated);
  const queryClient = useQueryClient();
  const acknowledge = useMutation({ mutationFn: fastApi.organization.acknowledgeReminder, onSuccess: () => queryClient.invalidateQueries({ queryKey: ["fastapi", "organization", "reminders"] }) });
  const dismiss = useMutation({ mutationFn: fastApi.organization.dismissReminder, onSuccess: () => queryClient.invalidateQueries({ queryKey: ["fastapi", "organization", "reminders"] }) });

  const pending = (reminders.data || []).filter((r) => r.status === "pending");
  if (pending.length === 0) return null;

  return (
    <div className="space-y-3">
      {pending.map((r) => (
        <div key={r.id} className="flex flex-wrap items-start gap-4 rounded-2xl border border-amber-100 bg-amber-50/60 p-5 dark:border-amber-950 dark:bg-amber-950/20">
          <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300"><Bell size={18} /></div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-semibold uppercase tracking-wider text-amber-700 dark:text-amber-300">{r.reminderType} reminder from {r.senderName}</p>
            <h3 className="mt-1 font-bold text-slate-900 dark:text-white">{r.title}</h3>
            <p className="mt-1 text-sm leading-6 text-slate-600 dark:text-slate-300">{r.message}</p>
            <p className="mt-2 text-xs text-slate-400">{new Date(r.createdAt).toLocaleString()}</p>
          </div>
          <div className="flex gap-2 shrink-0">
            <button onClick={() => acknowledge.mutate(r.id)} disabled={acknowledge.isPending} className="flex items-center gap-1.5 rounded-xl bg-emerald-700 px-3 py-2 text-xs font-bold text-white hover:bg-emerald-600"><CheckCircle2 size={13} /> Acknowledge</button>
            <button onClick={() => dismiss.mutate(r.id)} disabled={dismiss.isPending} className="flex items-center gap-1.5 rounded-xl bg-slate-100 px-3 py-2 text-xs font-bold text-slate-600 hover:bg-slate-200 dark:bg-white/10 dark:text-slate-300"><X size={13} /> Dismiss</button>
          </div>
        </div>
      ))}
    </div>
  );
}

function StatCard({ label, value, sub, icon: Icon, color }: { label: string; value: string | number; sub?: string; icon: typeof Compass; color: string }) {
  return (
    <div className="cs-card p-5 sm:p-6">
      <div className="flex items-center justify-between">
        <dt className="cs-data-label">{label}</dt>
        <div className={`grid h-8 w-8 place-items-center rounded-lg ${color}`}><Icon size={16} /></div>
      </div>
      <dd className="mt-3 font-mono text-3xl font-medium tracking-[-0.04em] text-slate-900 dark:text-white">{value}</dd>
      {sub && <p className="mt-1 text-xs text-slate-500">{sub}</p>}
    </div>
  );
}

function QuickActions({ hasOrg, hasHistory }: { hasOrg: boolean; hasHistory: boolean }) {
  const actions = [
    { href: "/predict", label: "AI Prediction", desc: "15-question survey (country, household, travel, home, food, consumption) for your monthly footprint estimate", icon: Sparkles, color: "bg-violet-100 text-violet-700 dark:bg-violet-950 dark:text-violet-300" },
    { href: "/baseline", label: "Transparent Baseline", desc: "Auditable formula-based calculation with documented sources", icon: Compass, color: "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300" },
    ...(hasHistory ? [{ href: "/recommendations", label: "Recommendations", desc: "Profile-matched actions to reduce your footprint", icon: Target, color: "bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300" }] : []),
    { href: "/forecast", label: "Forecast", desc: "Predict your future emissions from activity history", icon: LineChart, color: "bg-sky-100 text-sky-700 dark:bg-sky-950 dark:text-sky-300" },
    { href: "/quests", label: "CarbonQuest", desc: "Track streaks, badges, and your climate engagement score", icon: Trophy, color: "bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300" },
    ...(hasOrg ? [{ href: "/my-recommendations", label: "My Actions", desc: "Track recommendations assigned by your organization", icon: CheckCircle2, color: "bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300" }] : []),
  ];
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {actions.map((a) => (
        <Link key={a.href} href={a.href} className="cs-card group flex flex-col p-5 sm:p-6">
          <div className={`grid h-10 w-10 place-items-center rounded-xl ${a.color}`}><a.icon size={18} /></div>
          <h3 className="mt-4 font-bold text-slate-900 group-hover:text-emerald-700 dark:text-white dark:group-hover:text-emerald-300">{a.label}</h3>
          <p className="mt-2 flex-1 text-sm leading-5 text-slate-500">{a.desc}</p>
          <span className="mt-4 inline-flex items-center text-sm font-bold text-emerald-700 dark:text-emerald-400">Open <ArrowRight size={14} className="ml-1 transition group-hover:translate-x-0.5" /></span>
        </Link>
      ))}
    </div>
  );
}

function OrgQuickLink({ org }: { org: OrgData }) {
  return (
        <Link href="/organization" className="cs-card group flex items-center gap-4 p-5 sm:p-6">
      <div className="grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-emerald-100 text-emerald-700 group-hover:scale-110 transition-transform dark:bg-emerald-950 dark:text-emerald-300"><Building2 size={22} /></div>
      <div className="flex-1 min-w-0">
        <p className="text-xs font-semibold uppercase tracking-wider text-emerald-700 dark:text-emerald-300">Your organization</p>
        <p className="mt-1 font-bold text-slate-900 dark:text-white">{org.name}</p>
        <p className="text-xs text-slate-500">{org.memberCount} member{org.memberCount !== 1 ? "s" : ""} · {org.yourRole === "org_admin" ? "Admin" : "Member"}</p>
      </div>
      <ArrowRight size={18} className="text-emerald-600 dark:text-emerald-400" />
    </Link>
  );
}

function JoinRequestBanner({ request }: { request: JoinRequestInfo }) {
  const refresh = useQueryClient();
  const states = {
    pending: { label: "Join request pending", body: `Your request to join ${request.organizationName} is waiting for the organization administrator's approval. You'll become a member once they accept.`, classes: "border-amber-100 bg-amber-50/60 text-amber-900 dark:border-amber-950 dark:bg-amber-950/20 dark:text-amber-100", icon: Hourglass },
    approved: { label: `You joined ${request.organizationName}`, body: "Your membership request was approved. Open your organization page to see the workspace.", classes: "border-emerald-100 bg-emerald-50/60 text-emerald-900 dark:border-emerald-950 dark:bg-emerald-950/20 dark:text-emerald-100", icon: CheckCircle2 },
    rejected: { label: "Join request declined", body: `Your request to join ${request.organizationName} was declined. You can request again from the organization page.`, classes: "border-red-100 bg-red-50/60 text-red-900 dark:border-red-950 dark:bg-red-950/20 dark:text-red-100", icon: XCircle },
  } as const;
  const state = states[request.status];
  const Icon = state.icon;
  return (
    <div className={`mt-6 flex flex-wrap items-center gap-4 rounded-2xl border p-5 ${state.classes}`}>
      <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-white/70 dark:bg-white/10"><Icon size={18} /></div>
      <div className="min-w-0 flex-1">
        <p className="font-bold">{state.label}</p>
        <p className="mt-0.5 text-sm opacity-85">{state.body}</p>
      </div>
      <Link href="/organization" className="flex items-center gap-1.5 rounded-xl bg-white/80 px-4 py-2.5 text-sm font-bold shadow-sm transition hover:bg-white dark:bg-white/10 dark:hover:bg-white/20">Open organization <ArrowRight size={14} /></Link>
      {request.status !== "pending" && (
        <button onClick={() => refresh.invalidateQueries({ queryKey: ["fastapi", "organization"] })} className="rounded-xl px-3 py-2.5 text-sm font-bold opacity-70 transition hover:opacity-100" aria-label="Dismiss join request status"><X size={14} /></button>
      )}
    </div>
  );
}

function AdminJoinRequestsBanner({ requests }: { requests: PendingJoinRequest[] }) {
  return (
    <div className="mt-6 flex flex-wrap items-center gap-4 rounded-2xl border border-sky-100 bg-sky-50/60 p-5 dark:border-sky-950 dark:bg-sky-950/20">
      <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-white/70 text-sky-700 dark:bg-white/10 dark:text-sky-300"><UserPlus size={18} /></div>
      <div className="min-w-0 flex-1">
        <p className="font-bold text-slate-900 dark:text-white">{requests.length} join request{requests.length !== 1 ? "s" : ""} waiting for approval</p>
        <p className="mt-0.5 text-sm text-slate-600 dark:text-slate-300">{requests.map((r) => r.userName || "Unknown user").join(", ")} asked to join your organization.</p>
      </div>
      <Link href="/organization" className="flex items-center gap-1.5 rounded-xl bg-sky-700 px-4 py-2.5 text-sm font-bold text-white shadow-lg shadow-sky-800/20 transition hover:bg-sky-600">Review requests <ArrowRight size={14} /></Link>
    </div>
  );
}

function LoggedInDashboard() {
  const auth = useAuth();
  const user = auth.user;
  const org = useFastApiQuery<OrgData | null>(["fastapi", "organization", "me"], "/organization/me", auth.isAuthenticated);
  const quests = useFastApiQuery<QuestData>(["activity", "quest-summary"], "/activity/quest-summary", auth.isAuthenticated);
  const history = useFastApiQuery<HistoryItem[]>(["insights", "history"], "/insights/history", auth.isAuthenticated);
  const myJoinRequest = useFastApiQuery<JoinRequestInfo | null>(["fastapi", "organization", "join-request", "mine"], "/organization/join-requests/mine", auth.isAuthenticated);
  const isAdmin = ["org_admin", "super_admin"].includes(user?.role || "");
  const pendingJoinRequests = useFastApiQuery<PendingJoinRequest[]>(["fastapi", "organization", "join-requests"], "/organization/join-requests", auth.isAuthenticated && isAdmin);

  const hasOrg = Boolean(org.data);
  const hasHistory = (history.data || []).length > 0;
  const streak = quests.data?.streak || 0;
  const score = quests.data?.score || 0;
  const bannerRequest = !hasOrg && myJoinRequest.data ? myJoinRequest.data : null;
  const adminRequests = isAdmin ? (pendingJoinRequests.data || []) : [];

  return (
    <RepoShell>
      <main id="main-content" className="cs-page">
        <section className="mb-8" aria-label="Personal summary">
          <p className="cs-data-label">Welcome back</p>
          <h1 className="cs-section-title mt-3 text-4xl sm:text-5xl">
            {user?.name ? `Hello, ${user.name.split(" ")[0]}.` : "Welcome back."}
          </h1>
          <p className="cs-section-lede mt-4 max-w-2xl">
            Track your carbon footprint, get personalized recommendations, and see the impact of your climate actions.
          </p>
        </section>

        <ReminderBanner />

        {bannerRequest && <JoinRequestBanner request={bannerRequest} />}
        {adminRequests.length > 0 && <AdminJoinRequestsBanner requests={adminRequests} />}

        {hasOrg && org.data && <div className="mt-6"><OrgQuickLink org={org.data} /></div>}

        {!hasOrg && (
          <div className="mt-8 rounded-2xl border border-dashed border-emerald-300 bg-emerald-50/30 p-5 sm:p-6 dark:border-emerald-950 dark:bg-emerald-950/10">
            <div className="flex flex-wrap items-center gap-4">
              <div className="grid h-10 w-10 place-items-center rounded-xl bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300"><Building2 size={18} /></div>
              <div className="flex-1">
                <p className="font-bold text-slate-900 dark:text-white">Join your organization</p>
                <p className="text-sm text-slate-500">Create or join an organization to receive team recommendations and track aggregate progress.</p>
              </div>
              <Link href="/organization" className="flex items-center gap-1.5 rounded-xl bg-emerald-700 px-4 py-2.5 text-sm font-bold text-white hover:bg-emerald-600">Get started <ArrowRight size={14} /></Link>
            </div>
          </div>
        )}

        <dl className="mt-8 grid gap-4 sm:grid-cols-3">
          <StatCard label="Engagement score" value={score} sub={streak + "-day streak"} icon={Flame} color="bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300" />
          <StatCard label="Estimates run" value={(history.data || []).length} sub="Private records" icon={LineChart} color="bg-sky-100 text-sky-700 dark:bg-sky-950 dark:text-sky-300" />
          <StatCard label="Badges earned" value={(quests.data?.badges || []).length} sub="From participation" icon={Trophy} color="bg-violet-100 text-violet-700 dark:bg-violet-950 dark:text-violet-300" />
        </dl>

        <section className="mt-12 sm:mt-14" aria-labelledby="quick-actions-title">
          <p className="cs-data-label">Quick actions</p>
          <h2 id="quick-actions-title" className="cs-section-title mt-3 text-2xl sm:text-3xl">What would you like to do?</h2>
          <div className="mt-6">
            <QuickActions hasOrg={hasOrg} hasHistory={hasHistory} />
          </div>
        </section>

        <section className="cs-card mt-12 p-6 sm:mt-14 sm:p-8" aria-labelledby="journey-title">
          <p className="cs-data-label">Your journey</p>
          <h2 id="journey-title" className="cs-section-title mt-3 text-2xl sm:text-3xl">Three steps to a lower footprint.</h2>
          <div className="mt-7 grid gap-5 md:grid-cols-3">
            {[
              { step: "01", title: "Discover", desc: "Calculate an indicative footprint with the AI prediction or transparent baseline.", href: "/explore", icon: Compass },
              { step: "02", title: "Reduce", desc: "Use optimization, what-if planning, and recommendations to find high-impact actions.", href: "/plan", icon: Target },
              { step: "03", title: "Track", desc: "Record activity, build streaks, and see your progress over time.", href: "/progress", icon: LineChart },
            ].map((s) => (
              <Link key={s.step} href={s.href} className="cs-card group flex flex-col p-6">
                <div className="flex items-start justify-between">
                  <span className="grid h-10 w-10 place-items-center rounded-xl bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300"><s.icon size={20} /></span>
                  <span className="font-mono text-xs font-medium tracking-[0.2em] text-emerald-600">{s.step}</span>
                </div>
                <h3 className="mt-5 text-xl font-bold tracking-[-0.05em] text-slate-900 group-hover:text-emerald-700 dark:text-white dark:group-hover:text-emerald-300">{s.title}</h3>
                <p className="mt-2 flex-1 text-sm leading-6 text-slate-500">{s.desc}</p>
                <span className="mt-5 inline-flex items-center text-sm font-bold text-emerald-700 dark:text-emerald-400">Start now <ArrowRight size={14} className="ml-1" aria-hidden="true" /></span>
              </Link>
            ))}
          </div>
        </section>
      </main>
    </RepoShell>
  );
}

const landingHubs = [
  { number: "01", title: "Explore", href: "/predict", icon: Compass, description: "Estimate your monthly footprint with a four-step questionnaire — the fixed-contract model and the documented formula baseline, side by side." },
  { number: "02", title: "Plan", href: "/whatif", icon: Target, description: "Turn a completed result into what-if comparisons, impact-ranked actions, and goal-based plans." },
  { number: "03", title: "Insights", href: "/insights", icon: LineChart, description: "Revisit every saved estimate, watch forecast readiness build from recorded activity, and export a printable report." },
  { number: "04", title: "Progress", href: "/quests", icon: Trophy, description: "Keep climate engagement visible with streaks, badges, and a privacy-aware leaderboard built on opt-in aggregates." },
];

const landingStats = [
  { value: "15", label: "Survey inputs per estimate" },
  { value: "02", label: "Evidence paths: model + baseline" },
  { value: "kg CO₂e", label: "Monthly estimate unit" },
];

function LandingStats() {
  return (
    <section className="pt-12" aria-label="CarbonSense in numbers">
      <dl className="grid gap-4 sm:grid-cols-3">
        {landingStats.map((s) => (
          <div key={s.label} className="cs-card flex flex-col gap-2 p-6">
            <dt className="cs-data-label">{s.label}</dt>
            <dd className="font-mono text-2xl font-medium tracking-[-0.04em] text-slate-900 sm:text-3xl dark:text-white">{s.value}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}

function LandingHubs() {
  return (
    <section className="pt-12 sm:pt-16" aria-labelledby="cs-hubs-title">
      <div className="max-w-2xl">
        <p className="cs-data-label">Inside the workspace</p>
        <h2 id="cs-hubs-title" className="cs-section-title mt-3 text-3xl sm:text-4xl">Four hubs, one climate workflow.</h2>
        <p className="cs-section-lede mt-4">Every tool lives in a hub — estimate first, then plan, then measure whether the plan moved the number.</p>
      </div>
      <div className="mt-9 grid gap-5 sm:grid-cols-2">
        {landingHubs.map(({ number, title, description, href, icon: Icon }) => (
          <article key={number} className="h-full">
            <Link href={href} className="cs-card group flex h-full flex-col p-6 sm:p-8">
              <div className="flex items-start justify-between">
                <span className="grid h-12 w-12 place-items-center rounded-2xl bg-emerald-50 text-emerald-700 transition-transform duration-200 group-hover:scale-110 dark:bg-emerald-950 dark:text-emerald-300"><Icon size={24} /></span>
                <p className="font-mono text-xs font-medium tracking-[0.2em] text-emerald-600">{number}</p>
              </div>
              <h3 className="mt-8 text-2xl font-bold tracking-[-0.05em] text-slate-900 dark:text-white">{title}</h3>
              <p className="mt-3 flex-1 text-base leading-relaxed text-slate-600 dark:text-slate-300">{description}</p>
              <span className="mt-8 inline-flex items-center text-sm font-bold text-emerald-700 transition-all group-hover:gap-2 dark:text-emerald-400">Open {title} <ArrowRight size={15} className="ml-1" aria-hidden="true" /></span>
            </Link>
          </article>
        ))}
      </div>
    </section>
  );
}

function LandingFooter() {
  const columns = [
    { heading: "Estimate", links: [{ href: "/predict", label: "AI prediction" }, { href: "/baseline", label: "Transparent baseline" }, { href: "/explore", label: "Explore hub" }] },
    { heading: "Plan", links: [{ href: "/whatif", label: "What-if" }, { href: "/result-recommendations", label: "My actions" }, { href: "/goals", label: "Goals" }] },
    { heading: "Track", links: [{ href: "/insights", label: "Forecast & history" }, { href: "/reports", label: "Reports" }, { href: "/quests", label: "CarbonQuest" }] },
    { heading: "Account", links: [{ href: "/register", label: "Create account" }, { href: "/login", label: "Sign in" }, { href: "/docs", label: "Methodology & limits" }] },
  ];
  return (
    <footer className="mt-16 border-t border-emerald-950/10 pb-10 pt-12 sm:mt-20 dark:border-white/10">
      <div className="mx-auto grid max-w-7xl gap-8 px-4 sm:gap-10 sm:px-6 lg:grid-cols-[1.4fr_repeat(4,1fr)] lg:px-8">
        <div>
          <p className="flex items-center gap-3">
            <span className="cs-brand-mark" aria-hidden="true"><span /><span /><span /></span>
            <span className="leading-tight"><span className="block font-bold tracking-[-0.065em] text-slate-900 dark:text-white">CarbonSense</span><span className="block font-mono text-[0.625rem] font-medium tracking-[0.17em] text-emerald-700 dark:text-emerald-400">CLIMATE INTELLIGENCE</span></span>
          </p>
          <p className="mt-4 max-w-xs text-sm leading-6 text-slate-500 dark:text-slate-400">Indicative personal carbon estimation with a transparent, documented baseline — built for clarity, not guesswork.</p>
        </div>
        {columns.map((col) => (
          <nav key={col.heading} aria-label={`${col.heading} links`}>
            <h3 className="cs-data-label">{col.heading}</h3>
            <ul className="mt-4 space-y-2.5">
              {col.links.map((l) => (
                <li key={l.href + l.label}><Link href={l.href} className="text-sm font-medium text-slate-600 transition-colors hover:text-emerald-700 dark:text-slate-400 dark:hover:text-emerald-300">{l.label}</Link></li>
              ))}
            </ul>
          </nav>
        ))}
      </div>
      <div className="mx-auto mt-12 flex max-w-7xl flex-col gap-2 border-t border-emerald-950/10 px-4 pt-6 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8 dark:border-white/10">
        <p className="font-mono text-xs tracking-wide text-slate-400 dark:text-slate-500">© 2026 CarbonSense · Estimates are indicative, not verified measurements.</p>
        <Link href="/docs" className="text-xs font-semibold text-emerald-700 hover:underline dark:text-emerald-400">How the numbers are produced</Link>
      </div>
    </footer>
  );
}

function GuestDashboard() {
  return (
    <RepoShell>
      <main id="main-content" className="cs-page">
        <section className="cs-hero grid min-h-[min(39rem,calc(100svh_-_4.5rem))] items-center gap-8 px-6 py-12 text-white sm:min-h-[min(41rem,calc(100svh_-_4.5rem))] sm:px-10 sm:py-16 lg:min-h-[min(48rem,calc(100svh_-_4.5rem))] lg:gap-10 lg:px-14 lg:py-20" aria-labelledby="cs-hero-title">
          <div className="cs-hero-bg" aria-hidden="true">
            <img src="/images/hero-forest.jpg" alt="" width={2400} height={1598} loading="eager" fetchPriority="high" decoding="async" />
          </div>
          <div className="cs-hero-content relative z-10 max-w-3xl">
            <p className="cs-hero-eyebrow">Personal climate intelligence</p>
            <h1 id="cs-hero-title" className="cs-hero-title mt-4 text-[clamp(2.75rem,1.1rem_+_4.5vw,4.6rem)] leading-[0.98]">See your carbon footprint clearly.</h1>
            <p className="cs-hero-lede mt-6">Estimate your monthly emissions with an AI model and a fully documented formula baseline — then turn the result into a plan you can actually measure.</p>
            <div className="mt-9 flex flex-col gap-3 sm:flex-row">
              <Link href="/baseline" className="cs-action inline-flex items-center justify-center rounded-2xl bg-emerald-400 px-7 py-4 text-base font-extrabold text-[#08241b] shadow-lg shadow-emerald-950/30 hover:bg-emerald-300">Calculate your baseline <ArrowRight size={18} className="ml-2" aria-hidden="true" /></Link>
              <Link href="/predict" className="cs-action-secondary inline-flex items-center justify-center rounded-2xl border border-white/35 bg-white/10 px-7 py-4 text-base font-bold text-white hover:bg-white/18">Explore AI prediction</Link>
            </div>
            <ul className="cs-hero-proof mt-10" aria-label="CarbonSense workflow">
              <li>Estimate</li>
              <li>Compare transparently</li>
              <li>Plan your next move</li>
            </ul>
          </div>
        </section>

        <LandingStats />

        <section className="pt-12 sm:pt-16" aria-labelledby="cs-journey-title">
          <div className="max-w-2xl">
            <p className="cs-data-label">The CarbonSense way</p>
            <h2 id="cs-journey-title" className="cs-section-title mt-3 text-3xl sm:text-4xl">Three steps, one evidence-aware workflow.</h2>
            <p className="cs-section-lede mt-4">Start with your estimate, understand the options available to you, then make the next action measurable.</p>
          </div>
          <div className="mt-9 grid gap-5 md:grid-cols-3">
            {[
              { number: "01", title: "Discover", description: "Calculate an indicative footprint with the transparent baseline or the fixed-contract model estimate.", href: "/baseline", icon: Compass },
              { number: "02", title: "Reduce", description: "Use what-if planning and impact-ranked actions to compare practical high-impact choices.", href: "/whatif", icon: Target },
              { number: "03", title: "Track", description: "Record activity and make progress visible over time in your private workspace.", href: "/history", icon: LineChart },
            ].map(({ number, title, description, href, icon: Icon }) => (
              <article key={number} className="h-full">
                <Link href={href} className="cs-card group flex h-full flex-col p-6 sm:p-8">
                  <div className="flex items-start justify-between">
                    <span className="grid h-12 w-12 place-items-center rounded-2xl bg-emerald-50 text-emerald-700 transition-transform duration-200 group-hover:scale-110 dark:bg-emerald-950 dark:text-emerald-300"><Icon size={24} /></span>
                    <p className="font-mono text-xs font-medium tracking-[0.2em] text-emerald-600">{number}</p>
                  </div>
                  <h3 className="mt-8 text-2xl font-bold tracking-[-0.05em] text-slate-900 dark:text-white">{title}</h3>
                  <p className="mt-3 flex-1 text-base leading-relaxed text-slate-600 dark:text-slate-300">{description}</p>
                  <span className="mt-8 inline-flex items-center text-sm font-bold text-emerald-700 transition-all group-hover:gap-2 dark:text-emerald-400">Start now <ArrowRight size={15} className="ml-1" /></span>
                </Link>
              </article>
            ))}
          </div>
        </section>

        <LandingHubs />
      </main>
      <LandingFooter />
    </RepoShell>
  );
}

export default function Dashboard() {
  const { isAuthenticated, loading, error } = useAuth();
  
  // Debug logging
  console.log('[Dashboard] Auth state:', { isAuthenticated, loading, error });
  
  // Show error state if auth check failed
  if (error) {
    console.error('[Dashboard] Auth error:', error);
  }
  
  // Show loading state with visible text
  if (loading) {
    console.log('[Dashboard] Rendering loading state...');
    return (
      <RepoShell>
        <main className="cs-page">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <div className="h-12 w-12 animate-spin rounded-full border-4 border-emerald-200 border-t-emerald-700 mx-auto" />
              <p className="mt-4 text-slate-600 dark:text-slate-300">Loading...</p>
            </div>
          </div>
        </main>
      </RepoShell>
    );
  }
  
  console.log('[Dashboard] Rendering final state:', isAuthenticated ? 'LoggedIn' : 'Guest');
  return isAuthenticated ? <LoggedInDashboard /> : <GuestDashboard />;
}
