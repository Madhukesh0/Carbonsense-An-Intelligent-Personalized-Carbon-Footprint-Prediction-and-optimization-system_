import { Link } from "wouter";

export function SectionHub({ title, description, href, action = "Open tool" }: { title: string; description: string; href: string; action?: string }) {
  return <article className="rounded-2xl border border-emerald-950/10 bg-white p-5 shadow-sm"><h3 className="text-lg font-semibold text-slate-900">{title}</h3><p className="mt-2 text-sm leading-6 text-slate-500">{description}</p><Link href={href} className="mt-4 inline-flex text-sm font-semibold text-emerald-700 hover:underline">{action} →</Link></article>;
}
