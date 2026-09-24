const regions = ["Africa", "Americas", "Asia", "Europe", "Oceania"] as const;

export function ContinentsPicker({ value, onChange }: { value?: string; onChange: (region?: string) => void }) {
  return <div className="flex flex-wrap gap-2" aria-label="Aggregate region filter"><button type="button" onClick={() => onChange(undefined)} className={`rounded-full px-3 py-1.5 text-sm ${!value ? "bg-primary text-primary-foreground" : "bg-primary/8 text-primary"}`}>All regions</button>{regions.map(region => <button type="button" key={region} onClick={() => onChange(region)} className={`rounded-full px-3 py-1.5 text-sm ${value === region ? "bg-primary text-primary-foreground" : "bg-primary/8 text-primary"}`}>{region}</button>)}</div>;
}
