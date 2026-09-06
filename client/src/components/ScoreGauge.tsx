export function ScoreGauge({ score, maximum = 100, label = "Progress score" }: { score: number; maximum?: number; label?: string }) {
  const percent = Math.max(0, Math.min(100, (score / Math.max(1, maximum)) * 100));
  return <div className="relative grid h-32 w-32 place-items-center rounded-full" style={{ background: `conic-gradient(#05845a ${percent}%, #e5eee9 0)` }} role="img" aria-label={`${label}: ${Math.round(percent)} percent`}><div className="grid h-24 w-24 place-items-center rounded-full bg-white text-center"><strong className="text-2xl text-slate-900">{Math.round(percent)}%</strong><span className="text-[10px] uppercase tracking-wider text-slate-500">{label}</span></div></div>;
}
