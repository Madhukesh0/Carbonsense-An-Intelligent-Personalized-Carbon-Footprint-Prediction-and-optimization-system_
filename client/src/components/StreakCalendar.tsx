export function StreakCalendar({ activeDays, days = 28 }: { activeDays: number[]; days?: number }) {
  return <div className="grid grid-cols-7 gap-1.5" aria-label="Recorded activity days">{Array.from({ length: days }, (_, index) => <span key={index} title={`Day ${index + 1}`} className={`h-4 rounded-sm ${activeDays.includes(index + 1) ? "bg-primary/90" : "bg-primary/10"}`} />)}</div>;
}
