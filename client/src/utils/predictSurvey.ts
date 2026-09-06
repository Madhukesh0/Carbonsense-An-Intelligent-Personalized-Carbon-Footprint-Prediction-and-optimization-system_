import { surveyDefaults } from "@/store/survey";

export const surveySections = [
  { nav: "Travel", title: "How you move", summary: "Travel is usually the largest part of an individual footprint. Distance multiplied by a per-kilometre emission factor drives most of the estimate." },
  { nav: "Home energy", title: "How you power your home", summary: "Electricity and heating burn fuel on your behalf, and the grid mix where you live decides how much CO2 each kilowatt-hour releases." },
  { nav: "Food", title: "What you eat", summary: "Food emissions come mainly from how it is produced. Animal products, especially red meat, need far more land, feed, and energy per calorie than plants." },
  { nav: "Consumption & waste", title: "What you buy and throw away", summary: "Every product carries manufacturing and transport emissions, and waste releases methane and CO2 as it decomposes." },
] as const;

export type SurveyField = { key: keyof typeof surveyDefaults; label: string; description: string; choices?: readonly string[]; type?: "number"; unit?: string; currency?: "INR"; min?: number; max?: number; step?: number; role: "model" | "compound" | "context" };

// Every question below maps to a physical emission mechanism (fuel burn, grid
// electricity, industrial production, or waste decomposition) and is
// answerable from daily life. Fields the frozen dataset collected but that
// have no defensible emission mechanism (sex, body type, social activity, and
// the abstract "energy efficiency" scale) are no longer asked: the payload
// still sends the dataset's reference values so the frozen 44-feature model
// contract stays valid.
//
// The COUNTRY is deliberately NOT a question: it is context, not behaviour.
// It is chosen once via the grid selector in the form header (India / US /
// UK), which resolves the grid emission factor (0.670 / 0.384 / 0.217
// kgCO2e/kWh) applied to every electrical line. Switchable at any time.
export const fieldGroups: readonly (readonly SurveyField[])[] = [
  [
    { key: "transport", label: "Main travel mode", description: "Your everyday way of getting around. Vehicles burn fuel per kilometre, while public transport spreads one engine's emissions across many passengers.", choices: ["private", "public", "walk/bicycle"], role: "model" },
    { key: "vehicle_type", label: "Vehicle fuel", description: "What powers your main vehicle, if you have one. Petrol and diesel release CO2 directly; an electric car shifts those emissions to the power grid.", choices: ["none", "petrol", "diesel", "electric", "hybrid", "lpg"], role: "model" },
    { key: "vehicle_monthly_distance_km", label: "Distance driven / month", description: "Typical kilometres in your vehicle per month. Fuel burned - and CO2 released - scales directly with distance.", type: "number", unit: "km", min: 0, max: 10000, step: 1, role: "model" },
    { key: "frequency_of_traveling_by_air", label: "Flights", description: "How often you fly. Aircraft engines burn large amounts of fuel per passenger, so even a few flights can outweigh most daily habits.", choices: ["never", "rarely", "often", "very frequently"], role: "model" },
  ],
  [
    { key: "household_size", label: "People in your home", description: "People sharing your home. Electricity, heating, and waste are shared, so the estimate divides those lines per person - a 4-person home halves each member's home-energy footprint.", type: "number", unit: "people", min: 1, max: 10, step: 1, role: "model" },
    { key: "heating_energy_source", label: "Heating fuel", description: "What heats your home and water. Burning gas or wood releases CO2 directly; electric heating emits whatever your grid emits.", choices: ["electricity", "natural gas", "wood"], role: "model" },
    { key: "how_long_tv_pc_daily_hour", label: "TV / PC hours / day", description: "Daily screen time on plugged-in devices. Every hour draws grid electricity, and the emission depends on the grid mix above.", type: "number", unit: "hours", min: 0, max: 24, step: 0.5, role: "model" },
    { key: "how_long_internet_daily_hour", label: "Internet hours / day", description: "Daily connected time. Streaming and browsing run data centres and network equipment that draw grid electricity.", type: "number", unit: "hours", min: 0, max: 24, step: 0.5, role: "model" },
  ],
  [
    { key: "diet", label: "Diet pattern", description: "Your usual diet. Raising animals for food takes far more land, feed, and energy than growing plants, so meat-heavy diets emit the most per calorie.", choices: ["vegan", "vegetarian", "pescatarian", "omnivore"], role: "model" },
    { key: "monthly_grocery_bill", label: "Grocery spend / month", description: "Typical monthly food spending. As a spending proxy it scales with the total food you consume, plus its packaging and transport.", type: "number", currency: "INR", min: 0, max: 5000, step: 1, role: "model" },
  ],
  [
    { key: "how_many_new_clothes_monthly", label: "New clothing / month", description: "Newly bought clothing items per month. Manufacturing fabric, dyeing it, and shipping each item releases CO2 before you ever wear it.", type: "number", unit: "items", min: 0, max: 50, step: 1, role: "model" },
    { key: "waste_bag_size", label: "Waste bag size", description: "Your usual bin-bag size - a stand-in for how much waste your household produces each week.", choices: ["small", "medium", "large", "extra large"], role: "model" },
    { key: "waste_bag_weekly_count", label: "Waste bags / week", description: "Bags thrown out per week. Landfilled waste releases methane and CO2 as it decomposes.", type: "number", unit: "bags", min: 0, max: 20, step: 1, role: "model" },
    { key: "recycling", label: "Recycling", description: "Materials you recycle. Recycling avoids the emissions of producing the same material from virgin resources, so it lowers your footprint.", choices: ["paper", "plastic", "metal", "glass", "none"], role: "compound" },
    { key: "cooking_with", label: "Cooking appliances", description: "Appliances you cook with. They draw electricity or gas every time you use them, and which ones you use changes your kitchen's energy load.", choices: ["stove", "oven", "microwave", "grill", "airfryer", "none"], role: "compound" },
  ],
];

type ChoiceVisual = { icon?: string; label?: string; detail?: string };
const groceryDisplayCurrencies = { INR: { label: "Indian rupee (₹)", symbol: "₹", locale: "en-IN" }, USD: { label: "US dollar ($)", symbol: "$", locale: "en-US" }, EUR: { label: "Euro (€)", symbol: "€", locale: "de-DE" }, GBP: { label: "British pound (£)", symbol: "£", locale: "en-GB" } } as const;
export type GroceryDisplayCurrency = keyof typeof groceryDisplayCurrencies;
export const cardChoiceKeys = new Set<keyof typeof surveyDefaults>(["diet", "transport", "heating_energy_source"]);
export const segmentedChoiceKeys = new Set<keyof typeof surveyDefaults>(["frequency_of_traveling_by_air", "waste_bag_size"]);
export const choiceVisuals: Partial<Record<keyof typeof surveyDefaults, Record<string, ChoiceVisual>>> = { country: { india: { label: 'India' }, china: { label: 'China' }, us: { label: 'United States' }, germany: { label: 'Germany' }, japan: { label: 'Japan' }, uk: { label: 'United Kingdom' }, france: { label: 'France' }, canada: { label: 'Canada' }, brazil: { label: 'Brazil' }, australia: { label: 'Australia' }, russia: { label: 'Russia' }, south_korea: { label: 'South Korea' }, saudi_arabia: { label: 'Saudi Arabia' }, indonesia: { label: 'Indonesia' }, uae: { label: 'UAE' }, singapore: { label: 'Singapore' }, netherlands: { label: 'Netherlands' } }, diet: { vegan: { icon: "🌱", detail: "Plant-based" }, vegetarian: { icon: "🥗", detail: "No meat" }, pescatarian: { icon: "🐟", detail: "Fish, no meat" }, omnivore: { icon: "🍽", detail: "Mixed diet" } }, transport: { private: { icon: "🚗", label: "Private travel", detail: "Own / shared vehicle" }, public: { icon: "🚌", label: "Public transport", detail: "Bus, train or metro" }, "walk/bicycle": { icon: "🚲", label: "Walk / bicycle", detail: "Active travel" } }, heating_energy_source: { electricity: { icon: "⚡", label: "Electricity" }, "natural gas": { icon: "🔥", label: "Natural gas" }, wood: { icon: "🪵", label: "Wood" } }, vehicle_type: { none: { icon: "—", label: "No vehicle" }, petrol: { icon: "⛽", label: "Petrol" }, diesel: { icon: "🛢", label: "Diesel" }, electric: { icon: "⚡", label: "Electric" }, hybrid: { icon: "🔋", label: "Hybrid" }, lpg: { icon: "🔥", label: "LPG" } }, region: { mixed: { label: "Mixed grid" }, renewable_heavy: { label: "Renewable-heavy" } }, cooking_with: { stove: { icon: "✓", label: "Stove" }, oven: { icon: "✓", label: "Oven" }, microwave: { icon: "✓", label: "Microwave" }, grill: { icon: "+", label: "Grill" }, airfryer: { icon: "+", label: "Air fryer" }, none: { icon: "—", label: "None" } }, recycling: { paper: { icon: "✓", label: "Paper" }, plastic: { icon: "✓", label: "Plastic" }, metal: { icon: "+", label: "Metal" }, glass: { icon: "+", label: "Glass" }, none: { icon: "—", label: "None" } } };
export function formatSurveyChoice(value: string, field: SurveyField) { return choiceVisuals[field.key]?.[value]?.label ?? value.replace(/_/g, " "); }
export function formatSurveyValue(value: number | string, field: SurveyField, groceryCurrency: GroceryDisplayCurrency = "INR") { if (field.currency === "INR") { const currency = groceryDisplayCurrencies[groceryCurrency]; return `${currency.symbol}${Number(value).toLocaleString(currency.locale)}`; } return `${value}${field.unit ? ` ${field.unit}` : ""}`; }
