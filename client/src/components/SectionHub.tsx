import { Link } from "wouter";

export function SectionHub({ title, description, href, action = "Open tool" }: { title: string; description: string; href: string; action?: string }) {
  return <article className="rounded-2xl border border-border bg-white p-5 shadow-sm"><h3 className="text-lg font-semibold text-foreground">{title}</h3><p className="mt-2 text-sm leading-6 text-muted-foreground">{description}</p><Link href={href} className="mt-4 inline-flex text-sm font-semibold text-primary hover:underline">{action} →</Link></article>;
}
