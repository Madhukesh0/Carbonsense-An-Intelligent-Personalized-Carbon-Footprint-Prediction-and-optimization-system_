type Slice = { label: string; value: number; color: string };

export function BreakdownDonutChart({ slices, label = "Breakdown" }: { slices: Slice[]; label?: string }) {
  const total = Math.max(1, slices.reduce((sum, slice) => sum + Math.max(0, slice.value), 0));
  let offset = 0;
  return <div className="flex items-center gap-5"><svg viewBox="0 0 42 42" className="h-28 w-28 -rotate-90" role="img" aria-label={label}>{slices.map(slice => { const dash = (Math.max(0, slice.value) / total) * 100; const part = <circle key={slice.label} cx="21" cy="21" r="15.9" fill="transparent" stroke={slice.color} strokeWidth="5" strokeDasharray={`${dash} ${100 - dash}`} strokeDashoffset={-offset} />; offset += dash; return part; })}</svg><ul className="space-y-2 text-sm">{slices.map(slice => <li key={slice.label} className="flex items-center gap-2 text-slate-600"><i className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: slice.color }} />{slice.label}: {Math.round(slice.value)}</li>)}</ul></div>;
}
