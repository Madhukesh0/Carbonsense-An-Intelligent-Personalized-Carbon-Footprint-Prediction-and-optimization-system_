export function HorizontalBarChart({ rows }: { rows: { label: string; value: number }[] }) {
  const max = Math.max(1, ...rows.map(row => row.value));
  return <div className="space-y-3">{rows.map(row => <div key={row.label}><div className="mb-1 flex justify-between gap-3 text-sm"><span className="text-slate-600">{row.label}</span><strong className="text-slate-900">{Math.round(row.value)}</strong></div><div className="h-2 overflow-hidden rounded-full bg-emerald-950/10"><div className="h-full rounded-full bg-emerald-600" style={{ width: `${Math.max(0, (row.value / max) * 100)}%` }} /></div></div>)}</div>;
}
