export function HorizontalBarChart({ rows }: { rows: { label: string; value: number }[] }) {
  const max = Math.max(1, ...rows.map(row => row.value));
  return <div className="space-y-3">{rows.map(row => <div key={row.label}><div className="mb-1 flex justify-between gap-3 text-sm"><span className="text-muted-foreground">{row.label}</span><strong className="text-foreground">{Math.round(row.value)}</strong></div><div className="h-2 overflow-hidden rounded-full bg-primary/10"><div className="h-full rounded-full bg-primary/90" style={{ width: `${Math.max(0, (row.value / max) * 100)}%` }} /></div></div>)}</div>;
}
