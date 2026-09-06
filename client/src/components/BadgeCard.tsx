import { Award } from "lucide-react";

export function BadgeCard({ label, detail }: { label: string; detail: string }) {
  return <article className="rounded-2xl border border-emerald-950/10 bg-white p-4 shadow-sm"><Award className="text-emerald-700" size={20} /><h3 className="mt-3 font-semibold text-slate-900">{label}</h3><p className="mt-1 text-sm leading-5 text-slate-500">{detail}</p></article>;
}
