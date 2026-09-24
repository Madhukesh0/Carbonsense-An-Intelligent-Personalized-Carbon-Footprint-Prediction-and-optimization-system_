import { Link } from "wouter";

const workspaceTabs = {
  explore: [{ href: "/predict", label: "AI prediction", icon: "◌" }, { href: "/baseline", label: "Transparent baseline", icon: "⌁" }],
  plan: [{ href: "/whatif", label: "What-if", icon: "↺" }, { href: "/result-recommendations", label: "My actions", icon: "✦" }, { href: "/my-recommendations", label: "Accepted", icon: "✓" }],
  insights: [{ href: "/forecast", label: "Forecast", icon: "⌁" }, { href: "/history", label: "History", icon: "▤" }],
  progress: [{ href: "/quests", label: "CarbonQuest", icon: "✦" }, { href: "/contributors", label: "Contributors", icon: "◉" }],
  admin: [{ href: "/admin", label: "Organization overview", icon: "◉" }, { href: "/admin/users", label: "User access", icon: "▤" }],
};

export default function WorkspaceTabs({ route }: { route: string }) {
  const group = route.startsWith("/admin") ? "admin" : ["/predict", "/baseline", "/explore"].includes(route) ? "explore" : ["/whatif", "/goals", "/recommendations", "/result-recommendations", "/my-recommendations", "/plan"].includes(route) ? "plan" : ["/forecast", "/history", "/reports", "/insights"].includes(route) ? "insights" : "progress";
  return <nav aria-label="Workspace tools" className="mt-7 flex gap-2 overflow-x-auto rounded-2xl border border-border bg-white/70 p-1.5 backdrop-blur dark:border-white/10 dark:bg-white/5">{workspaceTabs[group].map((tab) => <Link key={tab.href} href={tab.href} className={`cs-hub-tab shrink-0 px-3.5 py-2 text-sm font-semibold ${route === tab.href ? "bg-primary/10 text-primary shadow-sm dark:bg-primary/20" : "text-muted-foreground hover:bg-muted hover:text-foreground dark:hover:bg-white/10 dark:hover:text-primary-foreground"}`}><span className="mr-1.5" aria-hidden="true">{tab.icon}</span>{tab.label}</Link>)}</nav>;
}
