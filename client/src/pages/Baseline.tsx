import { ArrowLeft, ArrowRight, Check } from "lucide-react";
import { Link } from "wouter";
import { useMemo, useState } from "react";
import RepoShell from "@/components/RepoShell";
import { gridCountries, GRID_FACTORS, type GridCountry } from "@/utils/gridCountries";
import { calculateAlignedBaseline, V25_FACTORS, alignedBaselineDefaults, type AlignedBaselineInput } from "@/lib/v25Baseline";

/**
 * Transparent baseline calculator on the v2.5-aligned cited factor set —
 * the same coefficients the deployed XGBoost model and the dataset target
 * use (Ember 2025 grid, IPCC 2006 fuel chemistry, Scarborough 2023 diet,
 * OWID air bands, EEA clothing, IPCC waste). No DESNZ-only legacy values.
 */

type VehicleFuel = "petrol" | "diesel" | "hybrid" | "lpg" | "electric";
type Diet = "vegan" | "vegetarian" | "pescatarian" | "omnivore";
type AirBand = "never" | "rarely" | "often" | "very frequently";
type BagSize = "small" | "medium" | "large" | "extra large";

const SOURCE_LINES = [
  "Ember/OWID carbon-intensity dataset (2025) — India/US/UK grid factors, identical to the model's inputs",
  "IPCC 2006 Vol.2 fuel chemistry — petrol 2.31 kg/L, diesel 2.68 kg/L at mid-range fleet economy",
  "Scarborough 2023 diet bands — 90/115/120/215 kg per month",
  "OWID air-travel bands — 0/60/180/420 kg per month · EEA clothing ~18 kg/garment · IPCC Vol.5 waste 0.65 kg/kg",
];

type PageInput = Omit<AlignedBaselineInput, "country" | "renewableHeavy">;

const defaults: PageInput = {
  vehicleMonthlyDistanceKm: 300,
  vehicleFuel: "petrol",
  tvHours: 4,
  internetHours: 4,
  heating: "electricity",
  diet: "omnivore",
  groceryBill: 200,
  newClothes: 2,
  bagSize: "medium",
  bagsPerWeek: 3,
  recycling: ["paper"],
  cooking: ["stove", "oven"],
  air: "rarely",
};

const fmt = (value: number) => Math.round(value * 10) / 10;

export default function RepoExploreBaseline() {
  const [country, setCountry] = useState<GridCountry>("india");
  const [renewableHeavy, setRenewableHeavy] = useState(false);
  const [input, setInput] = useState<PageInput>(defaults);
  const set = <K extends keyof PageInput>(key: K, value: PageInput[K]) =>
    setInput(current => ({ ...current, [key]: value }));

  const grid = renewableHeavy ? GRID_FACTORS[country].renewableHeavy : GRID_FACTORS[country].mixed;
  const groceryFactor = V25_FACTORS.groceryByCountry[country];

  const calculated = useMemo(
    () => calculateAlignedBaseline({ ...input, country, renewableHeavy }),
    [input, country, renewableHeavy],
  );

  const calculatedLines = [
    { key: "transport", label: "🚗 Transport", detail: calculated.arithmetic.transport, value: calculated.breakdown.transport },
    { key: "home_energy", label: "🏠 Home energy", detail: calculated.arithmetic.home_energy, value: calculated.breakdown.home_energy },
    { key: "food", label: "🍽️ Food", detail: calculated.arithmetic.food, value: calculated.breakdown.food },
    { key: "waste", label: "🗑️ Waste", detail: calculated.arithmetic.waste, value: calculated.breakdown.waste },
    { key: "clothing", label: "👕 Clothing", detail: calculated.arithmetic.clothing, value: calculated.breakdown.clothing },
    { key: "cooking", label: "🍳 Cooking", detail: calculated.arithmetic.cooking, value: calculated.breakdown.cooking },
    { key: "air_travel", label: "✈️ Air travel", detail: calculated.arithmetic.air_travel, value: calculated.breakdown.air_travel },
  ];
  const largest = Math.max(1, ...calculatedLines.map(line => line.value));
  const toggleCooking = (item: string) =>
    set("cooking", input.cooking.includes(item) ? input.cooking.filter(c => c !== item) : [...input.cooking, item]);

  return <RepoShell><main className="cs-page cs-explore-baseline-page">
    <header className="max-w-3xl">
      <Link href="/explore" className="inline-flex items-center text-sm font-bold text-emerald-700 hover:underline dark:text-emerald-300"><ArrowLeft size={15} className="mr-1" /> Dashboard</Link>
      <p className="cs-kicker mt-7">Explore workspace</p>
      <h1 className="mt-3 text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white sm:text-5xl">Explore your footprint.</h1>
      <p className="mt-3 text-base leading-7 text-slate-600 dark:text-slate-300">Two ways to calculate your carbon footprint — AI-powered prediction or a transparent, source-backed baseline. Both now use the same v2.5 cited factor set.</p>
    </header>

    <nav aria-label="Footprint calculation method" className="cs-explore-method-slider mt-9 grid grid-cols-2 rounded-2xl bg-white/75 p-1.5 shadow-sm ring-1 ring-emerald-950/5 dark:bg-white/5 dark:ring-white/10">
      <Link href="/predict" className="cs-action flex items-center justify-center rounded-xl px-4 py-3 text-sm font-bold text-slate-500 hover:bg-slate-50 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-white/10 dark:hover:text-white"><span className="mr-2" aria-hidden="true">◌</span> AI Prediction</Link>
      <Link href="/baseline" aria-current="page" className="flex items-center justify-center rounded-xl bg-white px-4 py-3 text-sm font-bold text-emerald-800 shadow-sm dark:bg-emerald-950 dark:text-emerald-200"><span className="mr-2" aria-hidden="true">⌁</span> Baseline Calculator</Link>
    </nav>

    <section className="mt-8 grid items-start gap-6 xl:grid-cols-[minmax(0,1.16fr)_minmax(20rem,.74fr)]">
      <article className="cs-card cs-explore-input-card p-6 sm:p-9">
        <div className="flex flex-wrap items-start justify-between gap-4 border-b border-emerald-950/10 pb-6 dark:border-white/10">
          <div>
            <p className="cs-data-label">Step 1 — country & supply</p>
            <h2 className="mt-3 text-3xl font-bold tracking-[-0.055em] text-slate-900 dark:text-white">Where your power comes from.</h2>
            <p className="mt-3 max-w-xl text-base leading-relaxed text-slate-600 dark:text-slate-300">Your country sets the grid and grocery factors used by both the AI model and this baseline.</p>
          </div>
          <span className="rounded-full bg-emerald-50 px-3 py-1.5 text-xs font-bold text-emerald-700 dark:bg-emerald-950 dark:text-emerald-200">Grid {grid} kgCO₂e/kWh</span>
        </div>
        <div className="mt-6 flex flex-wrap gap-2">
          {(Object.keys(gridCountries) as GridCountry[]).map(key => (
            <button key={key} type="button" onClick={() => setCountry(key)}
              className={`rounded-xl px-4 py-2.5 text-sm font-bold ring-1 transition ${country === key ? "bg-emerald-700 text-white ring-emerald-700" : "bg-white text-slate-600 ring-emerald-950/10 hover:bg-emerald-50 dark:bg-white/5 dark:text-slate-300 dark:ring-white/10"}`}>
              {key === "india" ? "🇮🇳 India" : key === "us" ? "🇺🇸 United States" : "🇬🇧 United Kingdom"}
            </button>
          ))}
        </div>
        <label className="mt-4 flex cursor-pointer items-center gap-3 rounded-xl bg-emerald-50/70 px-4 py-3 text-sm dark:bg-emerald-950/40">
          <input type="checkbox" checked={renewableHeavy} onChange={event => setRenewableHeavy(event.target.checked)} className="h-4 w-4 accent-emerald-700" />
          <span className="font-semibold text-slate-700 dark:text-slate-200">Renewable-heavy supply (green tariff / rooftop solar)</span>
          <span className="ml-auto font-mono text-xs text-emerald-700 dark:text-emerald-300">{GRID_FACTORS[country].renewableHeavy} kgCO₂e/kWh</span>
        </label>

        <div className="mt-8 border-b border-emerald-950/10 pb-6 dark:border-white/10">
          <p className="cs-data-label">Step 2 — transport</p>
          <Slider label="🚗 Distance driven / month" unit="km" max={3000} step={25} value={input.vehicleMonthlyDistanceKm} onChange={value => set("vehicleMonthlyDistanceKm", value)} hint={`× ${Math.round(calculated.vehicleKgPerKm * 10000) / 10000} kg/km (IPCC fuel chemistry, ${input.vehicleFuel})`} />
          <div className="mt-3 flex flex-wrap gap-2">
            {(["petrol", "diesel", "hybrid", "lpg", "electric"] as VehicleFuel[]).map(fuel => (
              <button key={fuel} type="button" onClick={() => set("vehicleFuel", fuel)}
                className={`rounded-lg px-3 py-1.5 text-xs font-bold capitalize ring-1 transition ${input.vehicleFuel === fuel ? "bg-emerald-700 text-white ring-emerald-700" : "bg-white text-slate-600 ring-emerald-950/10 dark:bg-white/5 dark:text-slate-300 dark:ring-white/10"}`}>{fuel}</button>
            ))}
          </div>
        </div>

        <div className="mt-8 border-b border-emerald-950/10 pb-6 dark:border-white/10">
          <p className="cs-data-label">Step 3 — home energy</p>
          <Slider label="📺 TV / PC hours / day" unit="h" max={24} step={0.5} value={input.tvHours} onChange={value => set("tvHours", value)} hint="× 75 W device convention" />
          <Slider label="🌐 Internet hours / day" unit="h" max={24} step={0.5} value={input.internetHours} onChange={value => set("internetHours", value)} hint="× 40 W router + network share" />
          <div className="mt-3 flex flex-wrap gap-2">
            {(["electricity", "natural gas", "wood"] as const).map(heat => (
              <button key={heat} type="button" onClick={() => set("heating", heat)}
                className={`rounded-lg px-3 py-1.5 text-xs font-bold capitalize ring-1 transition ${input.heating === heat ? "bg-emerald-700 text-white ring-emerald-700" : "bg-white text-slate-600 ring-emerald-950/10 dark:bg-white/5 dark:text-slate-300 dark:ring-white/10"}`}>{heat}</button>
            ))}
          </div>
        </div>

        <div className="mt-8 border-b border-emerald-950/10 pb-6 dark:border-white/10">
          <p className="cs-data-label">Step 4 — food</p>
          <div className="flex flex-wrap gap-2">
            {(["vegan", "vegetarian", "pescatarian", "omnivore"] as Diet[]).map(diet => (
              <button key={diet} type="button" onClick={() => set("diet", diet)}
                className={`rounded-lg px-3 py-1.5 text-xs font-bold capitalize ring-1 transition ${input.diet === diet ? "bg-emerald-700 text-white ring-emerald-700" : "bg-white text-slate-600 ring-emerald-950/10 dark:bg-white/5 dark:text-slate-300 dark:ring-white/10"}`}>{diet} · {V25_FACTORS.dietBand[diet]} kg</button>
            ))}
          </div>
          <div className="mt-4"><Slider label="🛒 Grocery spend / month" unit={country === "india" ? "₹" : country === "uk" ? "£" : "$"} max={2000} step={10} value={input.groceryBill} onChange={value => set("groceryBill", value)} hint={`× ${groceryFactor} kg per currency unit (price-level calibrated)`} /></div>
        </div>

        <div className="mt-8 border-b border-emerald-950/10 pb-6 dark:border-white/10">
          <p className="cs-data-label">Step 5 — waste & consumption</p>
          <Slider label="🗑️ Waste bags / week" unit="bags" max={20} step={1} value={input.bagsPerWeek} onChange={value => set("bagsPerWeek", value)} hint={`× ${V25_FACTORS.bagMassKg[input.bagSize]} kg bag × 0.65 kg/kg (IPCC)`} />
          <div className="mt-3 flex flex-wrap gap-2">
            {(["small", "medium", "large", "extra large"] as BagSize[]).map(size => (
              <button key={size} type="button" onClick={() => set("bagSize", size)}
                className={`rounded-lg px-3 py-1.5 text-xs font-bold capitalize ring-1 transition ${input.bagSize === size ? "bg-emerald-700 text-white ring-emerald-700" : "bg-white text-slate-600 ring-emerald-950/10 dark:bg-white/5 dark:text-slate-300 dark:ring-white/10"}`}>{size}</button>
            ))}
          </div>
          <div className="mt-4"><Slider label="👕 New clothing / month" unit="items" max={30} step={1} value={input.newClothes} onChange={value => set("newClothes", value)} hint="× 18 kg per item (EEA textiles)" /></div>
          <div className="mt-3 flex flex-wrap gap-2">
            {(["paper", "plastic", "metal", "glass"] as const).map(item => {
              const active = input.recycling.includes(item);
              return (
                <button key={item} type="button" onClick={() =>
                  set("recycling", active ? input.recycling.filter(r => r !== item) : [...input.recycling, item])}
                  className={`rounded-lg px-3 py-1.5 text-xs font-bold capitalize ring-1 transition ${active ? "bg-emerald-700 text-white ring-emerald-700" : "bg-white text-slate-600 ring-emerald-950/10 dark:bg-white/5 dark:text-slate-300 dark:ring-white/10"}`}>♻️ {item} (−{V25_FACTORS.recyclingCreditKg[item]} kg)</button>
              );
            })}
          </div>
        </div>

        <div className="mt-8 border-b border-emerald-950/10 pb-6 dark:border-white/10">
          <p className="cs-data-label">Step 6 — cooking & flights</p>
          <div className="flex flex-wrap gap-2">
            {(["stove", "oven", "microwave", "grill", "airfryer"] as const).map(item => (
              <button key={item} type="button" onClick={() => toggleCooking(item)}
                className={`rounded-lg px-3 py-1.5 text-xs font-bold capitalize ring-1 transition ${input.cooking.includes(item) ? "bg-emerald-700 text-white ring-emerald-700" : "bg-white text-slate-600 ring-emerald-950/10 dark:bg-white/5 dark:text-slate-300 dark:ring-white/10"}`}>{item}</button>
            ))}
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            {(["never", "rarely", "often", "very frequently"] as AirBand[]).map(band => (
              <button key={band} type="button" onClick={() => set("air", band)}
                className={`rounded-lg px-3 py-1.5 text-xs font-bold ring-1 transition ${input.air === band ? "bg-emerald-700 text-white ring-emerald-700" : "bg-white text-slate-600 ring-emerald-950/10 dark:bg-white/5 dark:text-slate-300 dark:ring-white/10"}`}>✈️ {band} · {V25_FACTORS.airBand[band]} kg</button>
            ))}
          </div>
        </div>
      </article>

      <aside id="live-baseline" className="xl:sticky xl:top-24"><section className="cs-card cs-explore-live-card p-6 sm:p-7"><div className="flex items-center justify-between"><p className="font-mono text-xs tracking-[0.14em] text-slate-500">LIVE ESTIMATE</p><span className="flex items-center gap-1.5 text-xs font-bold text-emerald-600"><span className="h-2 w-2 rounded-full bg-emerald-400" /> LIVE</span></div><div aria-live="polite" className="mt-5"><p className="text-5xl font-extrabold tracking-[-0.065em] text-emerald-600">{Math.round(calculated.total)} <span className="text-xl font-semibold text-slate-400">kgCO₂e</span></p><p className="mt-2 text-sm text-slate-500">v2.5-aligned transparent baseline · per person / month</p></div><div className="mt-7 space-y-4">{calculatedLines.map(line => <div key={line.key}><div className="flex items-center justify-between gap-3 text-sm"><span className="min-w-0 truncate text-slate-700 dark:text-slate-200">{line.label}</span><span className="shrink-0 font-mono font-bold text-slate-700 dark:text-slate-200">{fmt(line.value)} kg</span></div><div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100 dark:bg-white/10"><div className="h-full rounded-full bg-emerald-500 transition-[width] duration-200" style={{ width: `${Math.max(line.value ? 4 : 0, Math.round(line.value / largest * 100))}%` }} /></div><p className="mt-1 text-xs text-slate-400">{line.detail}</p></div>)}</div><div className="mt-8 border-t border-slate-100 pt-5 dark:border-white/10"><p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">Source-bound factors</p><p className="mt-2 text-xs leading-5 text-slate-500">Every coefficient here is the same cited value the v2.5 dataset and the deployed model use — Ember 2025 grid, IPCC 2006 fuel chemistry, Scarborough 2023 diet, OWID air bands.</p><ul className="mt-3 space-y-1.5">{SOURCE_LINES.map(line => <li key={line} className="flex gap-2 text-xs font-medium text-emerald-800 dark:text-emerald-200"><Check size={14} className="mt-0.5 shrink-0" />{line}</li>)}</ul></div></section></aside>
    </section>
  </main></RepoShell>;
}

function Slider({ label, unit, max, step, value, onChange, hint }: { label: string; unit: string; max: number; step: number; value: number; onChange: (value: number) => void; hint: string }) {
  return <div className="mt-4">
    <div className="flex flex-wrap items-center justify-between gap-3">
      <label className="font-bold text-slate-900 dark:text-white">{label}</label>
      <div className="flex items-center gap-2">
        <output className="rounded-lg bg-emerald-50 px-2.5 py-1.5 font-mono text-sm font-bold text-emerald-700 dark:bg-emerald-950 dark:text-emerald-200">{value} <span className="text-xs font-semibold">{unit}</span></output>
        <span className="text-xs text-slate-400">{hint}</span>
      </div>
    </div>
    <input aria-label={label} className="cs-range mt-4 w-full" type="range" min={0} max={max} step={step} value={value} onChange={event => onChange(Number(event.target.value))} />
    <div className="mt-2 flex justify-between text-xs text-slate-400"><span>0</span><span>{max.toLocaleString()} {unit}</span></div>
  </div>;
}
