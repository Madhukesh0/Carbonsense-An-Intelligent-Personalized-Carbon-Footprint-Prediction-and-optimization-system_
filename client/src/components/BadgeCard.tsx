import { Award } from "lucide-react";

export function BadgeCard({ label, detail }: { label: string; detail: string }) {
  return <article className="rounded-2xl border border-border bg-white p-4 shadow-sm"><Award className="text-primary" size={20} /><h3 className="mt-3 font-semibold text-foreground">{label}</h3><p className="mt-1 text-sm leading-5 text-muted-foreground">{detail}</p></article>;
}
