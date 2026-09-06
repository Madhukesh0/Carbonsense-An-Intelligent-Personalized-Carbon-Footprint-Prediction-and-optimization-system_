import { ArrowRight, Check, Circle, Compass, LineChart, Route, Target } from "lucide-react";
import { Link } from "wouter";
import { useAuth } from "@/_core/hooks/useAuth";
import { useFastApiQuery } from "@/hooks/useFastApi";

type Step = {
  id: "estimate" | "driver" | "plan" | "followup";
  number: string;
  title: string;
  body: string;
  href: string;
  action: string;
  icon: typeof Compass;
  complete: boolean;
};

export default function RepoFirstUsePath() {
  const { isAuthenticated } = useAuth();
  const history = useFastApiQuery<{ id: string }[]>(["insights", "history"], "/insights/history", isAuthenticated);
  const runs = history.data ?? [];
  const hasEstimate = runs.length > 0;
  const hasFollowUp = runs.length > 1;
  const completedCount = [hasEstimate, hasEstimate, false, hasFollowUp].filter(Boolean).length;

  const steps: Step[] = [
    {
      id: "estimate",
      number: "01",
      title: "Run an estimate",
      body: hasEstimate ? "Your account has a recorded estimate." : "Use the AI survey or transparent baseline to start a private record.",
      href: hasEstimate ? "/history" : "/predict",
      action: hasEstimate ? "View estimate" : "Start estimate",
      icon: Compass,
      complete: hasEstimate,
    },
    {
      id: "driver",
      number: "02",
      title: "Review a top driver",
      body: hasEstimate ? "Open your latest result to see the displayed modeled input groups and transparent categories." : "A completed estimate unlocks an explainable result view.",
      href: hasEstimate ? "/history" : "/predict",
      action: hasEstimate ? "Review result" : "Complete estimate first",
      icon: LineChart,
      complete: hasEstimate,
    },
    {
      id: "plan",
      number: "03",
      title: "Choose a planning tool",
      body: hasEstimate ? "Use the result-led Optimizer, What-if, or Net-Zero pathway. Each keeps method boundaries visible." : "Planning tools are available after a completed AI and transparent baseline result pair.",
      href: hasEstimate ? "/plan" : "/baseline",
      action: hasEstimate ? "Open planning" : "Calculate baseline",
      icon: Target,
      complete: false,
    },
    {
      id: "followup",
      number: "04",
      title: "Record a follow-up",
      body: hasFollowUp ? "You have more than one recorded estimate; Insights can now show your account-scoped history." : "Return after a meaningful change to create a second comparison point.",
      href: hasFollowUp ? "/insights" : "/predict",
      action: hasFollowUp ? "Open Insights" : "Record follow-up",
      icon: Route,
      complete: hasFollowUp,
    },
  ];

  return (
    <section className="cs-first-use-path cs-card mt-8" aria-labelledby="first-use-title">
      <div className="cs-first-use-heading">
        <div>
          <p className="cs-data-label">A three-minute first use</p>
          <h2 id="first-use-title" className="mt-2 text-2xl font-bold tracking-[-0.05em] text-slate-900 dark:text-white">Start with one signal. Build from real records.</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600 dark:text-slate-300">This guide follows existing CarbonSense workflows. Completion reflects saved estimate history only; planning and recognition never imply verified emissions reductions.</p>
        </div>
        <div className="cs-first-use-count" aria-label={`${completedCount} of 4 onboarding steps have supporting account evidence`}>
          <b>{completedCount}/4</b><span>evidence-backed</span>
        </div>
      </div>
      {history.isLoading ? <div className="mt-6 h-32 animate-pulse rounded-2xl bg-emerald-50 dark:bg-emerald-950/40" /> : <ol className="cs-first-use-steps mt-7">{steps.map(step => {
        const Icon = step.icon;
        return <li key={step.id} className={`cs-first-use-step ${step.complete ? "is-complete" : ""}`}>
          <div className="cs-first-use-step-top"><span className="cs-first-use-number">{step.complete ? <Check size={15} aria-label="Completed from account record" /> : step.number}</span><Icon size={18} aria-hidden="true" /></div>
          <h3 className="mt-5 font-bold tracking-[-0.03em] text-slate-900 dark:text-white">{step.title}</h3>
          <p className="mt-2 flex-1 text-sm leading-6 text-slate-600 dark:text-slate-300">{step.body}</p>
          <Link href={step.href} className="cs-action mt-5 inline-flex items-center text-sm font-bold text-emerald-700 hover:underline dark:text-emerald-300">{step.action} <ArrowRight size={15} className="ml-1" /></Link>
        </li>;
      })}</ol>}
      {history.isError ? <p className="mt-5 text-xs leading-5 text-slate-500 dark:text-slate-400">Your progress will appear when private history storage is available. You can still start an estimate now.</p> : null}
    </section>
  );
}
