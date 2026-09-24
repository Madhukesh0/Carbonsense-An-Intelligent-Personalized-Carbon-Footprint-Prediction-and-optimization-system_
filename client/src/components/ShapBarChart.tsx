export function ShapBarChart({ rows }: { rows: { label: string; value: number }[] }) {
  const max = Math.max(1, ...rows.map(row => Math.abs(row.value)));
  return <div className="space-y-3">{rows.map(row => <div key={row.label}><div className="flex justify-between gap-3 text-sm"><span className="text-muted-foreground">{row.label}</span><strong className={row.value >= 0 ? "text-rose-700" : "text-primary"}>{row.value >= 0 ? "+" : ""}{Math.round(row.value)}</strong></div><div className="mt-1 h-2 overflow-hidden rounded-full bg-muted"><div className={`h-full rounded-full ${row.value >= 0 ? "bg-rose-500" : "bg-primary/90"}`} style={{ width: `${Math.abs(row.value) / max * 100}%` }} /></div></div>)}</div>;
}
