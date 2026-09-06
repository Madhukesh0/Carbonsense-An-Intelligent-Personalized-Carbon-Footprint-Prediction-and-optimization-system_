import { useAuth } from "@/_core/hooks/useAuth";
import { useTheme } from "@/contexts/ThemeContext";
import { BarChart3, Bell, Compass, Menu, Moon, Route, ShieldCheck, Sparkles, Sun, Target, Trophy, UserRound, X } from "lucide-react";
import { useState } from "react";
import { Link, useLocation } from "wouter";
import RoleAssistantWidget from "../RoleAssistantWidget";

type RepoShellProps = { children: React.ReactNode; title?: string };

const hubLinks = [
  { href: "/explore", label: "Explore", icon: Compass },
  { href: "/plan", label: "Plan", icon: Route },
  { href: "/insights", label: "Insights", icon: BarChart3 },
  { href: "/progress", label: "Progress", icon: Trophy },
];
const docsLink = { href: "/docs", label: "Docs", icon: Sparkles };

const childRoutes: Record<string, string[]> = {
  "/explore": ["/predict", "/baseline"],
  "/plan": ["/whatif", "/goals", "/recommendations", "/result-recommendations", "/my-recommendations"],
  "/insights": ["/forecast", "/history", "/reports"],
  "/progress": ["/quests", "/contributors", "/privacy", "/profile", "/reminders", "/organization"],
};

function isActive(href: string, location: string) {
  return location === href || childRoutes[href]?.includes(location) || false;
}

export default function RepoShell({ children }: RepoShellProps) {
  const { user, isAuthenticated, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [location] = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  const links = isAuthenticated
    ? [...hubLinks, docsLink]
    : [
        { href: "/", label: "Dashboard", icon: "" },
        { href: "/docs", label: "Docs", icon: Sparkles },
      ];
  const canSeeAdmin = ["org_admin", "super_admin"].includes(user?.role || "");

  return <div className="cs-app-shell min-h-screen text-slate-900 transition-colors dark:text-slate-100">
    <header className="sticky top-0 z-40 border-b border-emerald-950/10 bg-white/78 backdrop-blur-2xl dark:border-white/10 dark:bg-[#10201b]/80">
      <div className="mx-auto flex h-[4.5rem] max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link href="/" className="cs-brand-link group flex items-center gap-3" onClick={() => setMenuOpen(false)}>
          <span className="cs-brand-mark" aria-hidden="true"><span /><span /><span /></span>
          <span className="leading-tight"><span className="block font-bold tracking-[-0.065em] text-slate-900 transition-colors group-hover:text-emerald-700 dark:text-white">CarbonSense</span><span className="block font-mono text-[0.625rem] font-medium tracking-[0.17em] text-emerald-700 dark:text-emerald-400">CLIMATE INTELLIGENCE</span></span>
        </Link>

        <nav className="hidden items-center gap-1.5 md:flex" aria-label="Primary navigation">
          {links.map((link) => { const Icon = link.icon; return <Link key={link.href} href={link.href} aria-current={isActive(link.href, location) ? "page" : undefined} className={`cs-nav-link flex items-center gap-1.5 px-3.5 py-2 text-sm font-semibold ${isActive(link.href, location) ? "bg-emerald-100 text-emerald-800 shadow-sm dark:bg-emerald-950 dark:text-emerald-300" : "text-slate-500 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-white/10 dark:hover:text-white"}`}>
            {Icon && <Icon aria-hidden="true" size={14} strokeWidth={2.25} />}{link.label}
          </Link>; })}
          {canSeeAdmin && <Link href="/admin" className={`ml-1 cs-nav-link flex items-center gap-1.5 px-3.5 py-2 text-sm font-semibold ${location.startsWith("/admin") ? "bg-amber-100 text-amber-800 shadow-sm dark:bg-amber-950 dark:text-amber-300" : "bg-slate-100 text-slate-600 hover:bg-amber-100 dark:bg-white/10 dark:text-slate-300 dark:hover:bg-amber-950"}`}><ShieldCheck size={14} />Admin</Link>}
        </nav>

        <div className="flex items-center gap-1.5">
          {isAuthenticated ? <><span className="cs-account-chip hidden items-center gap-1.5 rounded-xl px-2.5 py-1.5 text-xs font-semibold text-emerald-800 sm:flex dark:text-emerald-200"><UserRound size={13} />{user?.name || "Workspace"}</span><button onClick={() => logout()} className="hidden rounded-xl px-2.5 py-1.5 text-xs font-semibold text-slate-500 transition-colors hover:bg-red-50 hover:text-red-600 sm:block dark:text-slate-400 dark:hover:bg-red-950">Sign out</button></> : <div className="hidden items-center gap-2 sm:flex"><Link href="/login" className="rounded-xl px-2.5 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-white/10">Sign in</Link><Link href="/register" className="cs-action rounded-xl bg-emerald-700 px-3.5 py-2 text-xs font-semibold text-white shadow-md shadow-emerald-800/20 hover:bg-emerald-600">Get started</Link></div>}
          <button onClick={() => toggleTheme?.()} className="grid h-8 w-8 place-items-center rounded-xl text-slate-600 transition-colors hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-white/10" aria-label="Toggle dark mode">{theme === "dark" ? <Sun size={17} className="text-amber-400" /> : <Moon size={17} />}</button>
          <button onClick={() => setMenuOpen((open) => !open)} className="grid h-8 w-8 place-items-center rounded-xl text-slate-700 hover:bg-slate-100 md:hidden dark:text-slate-200 dark:hover:bg-white/10" aria-expanded={menuOpen} aria-label={menuOpen ? "Close menu" : "Open menu"}>{menuOpen ? <X size={18} /> : <Menu size={18} />}</button>
        </div>
      </div>
    </header>

    {menuOpen && <div className="fixed inset-0 z-30 bg-slate-950/40 px-4 pt-[5.25rem] backdrop-blur-sm md:hidden" onClick={() => setMenuOpen(false)}><nav className="cs-mobile-menu mx-auto max-w-md rounded-3xl border border-emerald-950/10 bg-white p-3 dark:border-white/10 dark:bg-[#13261f]" aria-label="Mobile navigation" onClick={(event) => event.stopPropagation()}>{links.map((link) => { const Icon = link.icon; return <Link key={link.href} href={link.href} onClick={() => setMenuOpen(false)} className={`flex items-center gap-3 rounded-2xl px-4 py-3.5 text-lg font-semibold ${isActive(link.href, location) ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300" : "text-slate-700 hover:bg-slate-50 dark:text-slate-200 dark:hover:bg-white/10"}`}><span className="grid w-5 place-items-center">{Icon ? <Icon size={18} /> : <Sparkles size={18} />}</span>{link.label}</Link>; })}{canSeeAdmin && <Link href="/admin" onClick={() => setMenuOpen(false)} className="mt-1 flex items-center gap-3 rounded-2xl bg-amber-50 px-4 py-3.5 text-lg font-semibold text-amber-800 dark:bg-amber-950 dark:text-amber-300"><ShieldCheck size={19} />Admin</Link>}<div className="my-3 border-t border-slate-200 dark:border-white/10" />{isAuthenticated ? <button onClick={() => { logout(); setMenuOpen(false); }} className="w-full rounded-2xl px-4 py-3.5 text-left text-lg font-semibold text-red-600 hover:bg-red-50 dark:hover:bg-red-950">Sign out</button> : <div className="grid grid-cols-2 gap-2"><Link href="/login" onClick={() => setMenuOpen(false)} className="rounded-2xl border border-emerald-950/15 px-4 py-3.5 text-center text-lg font-semibold text-emerald-800 dark:border-white/15 dark:text-emerald-200">Sign in</Link><Link href="/register" onClick={() => setMenuOpen(false)} className="rounded-2xl bg-emerald-700 px-4 py-3.5 text-center text-lg font-semibold text-white">Get started</Link></div>}</nav></div>}

    {children}
    {isAuthenticated && <RoleAssistantWidget role={(user?.role || "individual") as "individual" | "org_admin" | "super_admin"} />}
  </div>;
}
