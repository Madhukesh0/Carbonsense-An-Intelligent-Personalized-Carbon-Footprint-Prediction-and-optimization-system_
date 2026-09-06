const regions = ["Africa", "Americas", "Asia", "Europe", "Oceania"] as const;

export function ContinentsPicker({ value, onChange }: { value?: string; onChange: (region?: string) => void }) {
  return <div className="flex flex-wrap gap-2" aria-label="Aggregate region filter"><button type="button" onClick={() => onChange(undefined)} className={`rounded-full px-3 py-1.5 text-sm ${!value ? "bg-emerald-700 text-white" : "bg-emerald-50 text-emerald-800"}`}>All regions</button>{regions.map(region => <button type="button" key={region} onClick={() => onChange(region)} className={`rounded-full px-3 py-1.5 text-sm ${value === region ? "bg-emerald-700 text-white" : "bg-emerald-50 text-emerald-800"}`}>{region}</button>)}</div>;
}
