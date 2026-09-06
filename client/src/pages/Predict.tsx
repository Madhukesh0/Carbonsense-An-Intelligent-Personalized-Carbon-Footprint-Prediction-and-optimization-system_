import { useState } from "react";
import { useLocation } from "wouter";
import { ArrowRight, Check, ChevronRight } from "lucide-react";
import { useAuth } from "@/_core/hooks/useAuth";
import PredictionResults from "@/components/predict/PredictionResults";
import { gridCountries, GRID_FACTORS, type GridCountry } from "@/utils/gridCountries";
import RepoAuthPage from "@/components/RepoAuthPage";
import RepoShell from "@/components/RepoShell";
import WorkspaceTabs from "@/components/navigation/WorkspaceTabs";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { useFastApiMutation } from "@/hooks/useFastApi";
import { validateSurvey } from "@/lib/surveyValidation";
import { useSurvey } from "@/store/survey";
import {
  contractColumns,
  DERIVED_MODEL_COLUMN_COUNT,
  DIRECT_MODEL_VALUE_COUNT,
  directlyEnteredModelColumns,
  TOTAL_INTERACTIVE_QUESTIONS,
} from "@/utils/predictContract";
import {
  cardChoiceKeys,
  choiceVisuals,
  fieldGroups,
  formatSurveyChoice,
  formatSurveyValue,
  type GroceryDisplayCurrency,
  segmentedChoiceKeys,
  surveySections as sections,
  type SurveyField,
} from "@/utils/predictSurvey";

export default function Predict() {
  const { value, set, toggle } = useSurvey();
  const [location] = useLocation();
  const isBaselineRoute = location === "/baseline";
  const auth = useAuth();
  const [step, setStep] = useState(0);
  const [groceryCurrency, setGroceryCurrency] = useState<GroceryDisplayCurrency>("INR");
  const [gridCountry, setGridCountry] = useState<GridCountry>("india");
  const [renewableHeavy, setRenewableHeavy] = useState(false);
  const activeGridFactor = renewableHeavy
    ? GRID_FACTORS[gridCountry].renewableHeavy
    : GRID_FACTORS[gridCountry].mixed;
  const [clientError, setClientError] = useState<string | null>(null);
  const prediction = useFastApiMutation<any, typeof value>("/model/predict");
  const baseline = useFastApiMutation<any, typeof value>("/model/baseline");
  const [result, setResult] = useState<any>(null);
  const [submitting, setSubmitting] = useState(false);

  const submit = async () => {
    const validationError = validateSurvey(value);
    if (validationError) {
      setClientError(validationError);
      return;
    }
    setClientError(null);
    setSubmitting(true);
    try {
      const startedAt = performance.now();
      const submitted = { ...value, country: gridCountry };
      const predicted = await prediction.mutateAsync(submitted);
      const elapsedMs = Math.round(performance.now() - startedAt);
      setResult({
        ...predicted,
        shap: predicted.explanation,
        submittedPayload: submitted,
        region: value.region,
        gridCountry,
        gridFactor: activeGridFactor,
        currency: value.currency,
        inferenceMs: elapsedMs,
      });
    } catch (err: any) {
      const message = err instanceof Error ? err.message : "Prediction failed";
      setClientError(
        message.includes("Failed to fetch")
          ? "Could not reach the prediction service. Please check your connection and try again."
          : message.includes("500")
            ? "The prediction service encountered an internal error. Please try again with different inputs."
            : message,
      );
    } finally {
      setSubmitting(false);
    }
  };

  if (!auth.loading && !auth.isAuthenticated) return <RepoAuthPage mode="login" />;
  if (result) return <PredictionResults result={result} onReset={() => setResult(null)} />;

  const isBusy = submitting || prediction.isPending;

  return (
    <RepoShell title="Estimate">
      <main className="cs-page">
        <div className="cs-card p-7 sm:p-9">
          <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
            <div>
              <span className="cs-kicker text-emerald-700 dark:text-emerald-400">
                {isBaselineRoute ? "Transparent baseline" : "AI prediction"}
              </span>
              <h1 className="mt-3 text-4xl font-extrabold tracking-tight sm:text-5xl text-slate-900 dark:text-white">
                {isBaselineRoute ? "Calculate with clear assumptions." : "Build your climate snapshot."}
              </h1>
              <p className="mt-3 max-w-2xl text-base leading-7 text-slate-600 dark:text-slate-300">
                Answer {TOTAL_INTERACTIVE_QUESTIONS} questions - your country sets the carbon
                intensity of every electrical line, your household size divides shared energy, and
                every other answer maps to a real emission mechanism: fuel burned in vehicles,
                grid electricity, food production, manufacturing, or waste decomposition.
              </p>
              <p className="mt-2 max-w-2xl text-xs leading-5 text-slate-400 dark:text-slate-500">
                Contract-only fields the source dataset required but that lack an emission mechanism
                (age, gender, body type, social activity) are not asked; the model receives their
                neutral reference values.
              </p>
            </div>
            <div className="flex flex-col gap-3">
              <div className="rounded-2xl border border-[#dce8e3] bg-white px-4 py-3 text-sm dark:border-emerald-300/15 dark:bg-emerald-950/40">
                <p className="cs-data-label text-slate-500 dark:text-slate-400">Electricity grid</p>
                <div className="mt-2 flex gap-1.5">
                  {(Object.keys(gridCountries) as GridCountry[]).map(key => (
                    <button
                      key={key}
                      type="button"
                      onClick={() => setGridCountry(key)}
                      className={
                        gridCountry === key
                          ? "rounded-lg bg-[#157f54] px-3 py-1.5 text-xs font-semibold text-white"
                          : "rounded-lg bg-[#f0f5f2] px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-[#e2ede7] dark:bg-emerald-950/60 dark:text-slate-300"
                      }
                      title={`Grid factor ${GRID_FACTORS[key].mixed.toFixed(3)} kgCO2e/kWh`}
                    >
                      {gridCountries[key].flag} {gridCountries[key].label}
                    </button>
                  ))}
                </div>
                <label className="mt-2.5 flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
                  <input
                    type="checkbox"
                    checked={renewableHeavy}
                    onChange={event => setRenewableHeavy(event.target.checked)}
                    className="h-3.5 w-3.5 accent-[#157f54]"
                  />
                  Renewable-heavy supply (green tariff / rooftop solar)
                </label>
                <p className="mt-1.5 font-mono text-[0.68rem] text-slate-400 dark:text-slate-500">
                  grid factor {activeGridFactor.toFixed(3)} kgCO2e/kWh
                </p>
              </div>
              <div className="rounded-2xl bg-emerald-50 px-4 py-3 text-sm dark:bg-emerald-950">
                <span className="font-semibold text-emerald-700 dark:text-emerald-300">{step + 1}</span>
              <span className="text-slate-400"> / {sections.length}</span>
                <span className="ml-3 text-slate-600 dark:text-slate-300">{sections[step].nav}</span>
              </div>
            </div>
          </div>
          <WorkspaceTabs route={location} />
          <Progress className="mt-8 h-2 bg-[#dce8e3]" value={((step + 1) / sections.length) * 100} />
          <details className="mt-5 rounded-2xl border border-[#dce8e3] bg-white px-5 py-4">
            <summary className="cursor-pointer text-sm font-semibold text-[#157f54]">
              View the exact 26-column contract
            </summary>
            <div className="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {contractColumns.map((column, index) => (
                <div
                  key={column}
                  className="flex items-center justify-between rounded-lg bg-[#f6f8f7] px-3 py-2 text-xs"
                >
                  <span className="truncate text-slate-600">
                    {index + 1}. {column}
                  </span>
                  <span className="ml-2 shrink-0 font-medium text-[#157f54]">
                    {directlyEnteredModelColumns.has(column) ? "entered" : "calculated"}
                  </span>
                </div>
              ))}
            </div>
            <p className="mt-4 text-xs leading-5 text-slate-500">
              The 16 calculated columns are intentionally read-only. Editing them would break the
              frozen feature-engineering contract; they update only from your interactive source
              answers.
            </p>
          </details>

          <Card className="mt-8 border-0 bg-white/90 p-5 shadow-[0_10px_35px_rgba(20,67,50,.06)] dark:bg-[#173126]/90 sm:p-8">
            <div className="mb-7 flex flex-col justify-between gap-3 border-b border-emerald-950/10 pb-5 sm:flex-row sm:items-end dark:border-white/10">
              <div>
                <p className="cs-data-label">Interactive source answers</p>
                <h2 className="mt-2 text-xl font-bold tracking-[-.04em] text-slate-900 dark:text-white">
                  {sections[step].title}
                </h2>
                <p className="mt-2 max-w-2xl text-base leading-relaxed text-slate-600 dark:text-slate-300">
                  {sections[step].summary} Every selection is editable before calculation;
                  compound choices generate several contract columns.
                </p>
              </div>
              <span className="font-mono text-xs tracking-[0.12em] text-emerald-700 dark:text-emerald-300">
                {fieldGroups[step].length} QUESTIONS IN THIS STEP
              </span>
            </div>
            <div className="cs-survey-stack">
              {fieldGroups[step].map((field: SurveyField) => {
                const isCompound = field.key === "recycling" || field.key === "cooking_with";
                const compoundKey = isCompound ? (field.key as "recycling" | "cooking_with") : null;
                const isTile = cardChoiceKeys.has(field.key);
                const isSegmented = segmentedChoiceKeys.has(field.key);

                return (
                  <section key={field.key} className="cs-survey-question">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <Label
                          htmlFor={`survey-${field.key}`}
                          className="text-base font-bold tracking-[-0.025em] text-[#102a2d] dark:text-white"
                        >
                          {field.label}
                        </Label>
                        <p
                          id={`survey-${field.key}-help`}
                          className="mt-1 max-w-2xl text-base leading-relaxed text-slate-500 dark:text-slate-400"
                        >
                          {field.description}
                        </p>
                      </div>
                      <span className="cs-survey-role">
                        {field.role === "compound"
                          ? "multi-select"
                          : field.role === "context"
                            ? "context"
                            : "model input"}
                      </span>
                    </div>
                    {field.choices ? (
                      <div
                        id={`survey-${field.key}`}
                        role={isCompound ? "group" : "radiogroup"}
                        aria-describedby={`survey-${field.key}-help`}
                        className={`cs-choice-group mt-5 ${isTile ? "cs-choice-group--tiles" : isSegmented ? "cs-choice-group--segments" : "cs-choice-group--chips"}`}
                      >
                        {field.choices.map((choice: string) => {
                          const selected = isCompound
                            ? value[field.key].includes(choice)
                            : value[field.key] === choice;
                          const visual = choiceVisuals[field.key]?.[choice];
                          return (
                            <button
                              type="button"
                              key={choice}
                              onClick={() =>
                                compoundKey ? toggle(compoundKey, choice) : set(field.key, choice)
                              }
                              aria-pressed={selected}
                              className={`cs-choice-control ${isTile ? "cs-choice-tile" : isSegmented ? "cs-choice-segment" : "cs-choice-chip"} ${selected ? "is-selected" : ""}`}
                            >
                              {visual?.icon && (
                                <span className="cs-choice-icon" aria-hidden="true">
                                  {selected && isCompound ? <Check size={15} /> : visual.icon}
                                </span>
                              )}
                              <span className="cs-choice-label">{formatSurveyChoice(choice, field)}</span>
                              {isTile && visual?.detail && (
                                <span className="cs-choice-detail">{visual.detail}</span>
                              )}
                            </button>
                          );
                        })}
                      </div>
                    ) : (
                      <div className="cs-range-control mt-5">
                        <div className="flex flex-wrap items-center justify-between gap-3">
                          <span className="cs-range-label">Choose a typical value</span>
                          <div className="flex items-center gap-2">
                            <span className="cs-range-value">
                              {formatSurveyValue(value[field.key], field, groceryCurrency)}
                            </span>
                            {field.currency && (
                              <label className="flex items-center gap-1.5">
                                <span className="sr-only">Grocery spending display currency</span>
                                <select
                                  value={groceryCurrency}
                                  onChange={(event) =>
                                    setGroceryCurrency(event.target.value as GroceryDisplayCurrency)
                                  }
                                  className="cs-select h-8 rounded-lg px-2 text-xs font-semibold text-emerald-800 dark:text-emerald-200"
                                >
                                  <option value="INR">INR</option>
                                  <option value="USD">USD</option>
                                  <option value="EUR">EUR</option>
                                  <option value="GBP">GBP</option>
                                </select>
                              </label>
                            )}
                          </div>
                        </div>
                        <input
                          id={`survey-${field.key}`}
                          type="range"
                          min={field.min}
                          max={field.max}
                          step={field.step}
                          value={value[field.key]}
                          aria-describedby={`survey-${field.key}-help`}
                          onChange={(event) => set(field.key, Number(event.target.value))}
                          className="cs-range mt-4 w-full"
                        />
                        <div className="mt-2 flex justify-between text-xs text-slate-400">
                          <span>{formatSurveyValue(field.min ?? 0, field, groceryCurrency)}</span>
                          <span>{formatSurveyValue(field.max ?? 0, field, groceryCurrency)}</span>
                        </div>
                        <div className="mt-4 flex flex-wrap items-center gap-x-3 gap-y-2">
                          <div className="flex max-w-[14rem] items-center rounded-xl border border-emerald-950/10 bg-white/80 focus-within:border-emerald-600 focus-within:ring-2 focus-within:ring-emerald-600/15 dark:border-white/10 dark:bg-white/5">
                            <Input
                              id={`survey-${field.key}-exact`}
                              type="number"
                              min={field.min}
                              max={field.max}
                              step={field.step}
                              value={value[field.key]}
                              aria-label={`Exact ${field.label}`}
                              onChange={(event) =>
                                set(field.key, event.target.value === "" ? "" : Number(event.target.value))
                              }
                              className="h-10 border-0 bg-transparent shadow-none focus-visible:ring-0"
                            />
                            <span className="mr-3 shrink-0 font-mono text-xs text-slate-500">
                              {field.currency ? groceryCurrency : field.unit}
                            </span>
                          </div>
                          {field.currency && (
                            <p className="text-xs leading-5 text-slate-500 dark:text-slate-400">
                              Display only — changing currency does not convert or alter the numeric
                              model input.
                            </p>
                          )}
                        </div>
                      </div>
                    )}
                  </section>
                );
              })}
            </div>
            <div className="mt-9 flex justify-between">
              <Button variant="outline" disabled={step === 0} onClick={() => setStep(Math.max(0, step - 1))}>
                Back
              </Button>
              {step < sections.length - 1 ? (
                <Button className="bg-[#157f54] hover:bg-[#106b47]" onClick={() => setStep(step + 1)}>
                  Continue <ChevronRight size={16} className="ml-2" />
                </Button>
              ) : (
                <Button
                  className="bg-[#157f54] hover:bg-[#106b47]"
                  onClick={submit}
                  disabled={isBusy}
                >
                  {isBusy ? (
                    <>
                      <span className="mr-2 inline-block h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                      Running inference…
                    </>
                  ) : (
                    <>
                      Calculate my estimate
                      <ArrowRight size={16} className="ml-2" />
                    </>
                  )}
                </Button>
              )}
            </div>
            {(clientError || prediction.error) && (
              <p
                role="alert"
                aria-live="polite"
                className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-base text-red-700"
              >
                {clientError || prediction.error?.message}
              </p>
            )}
          </Card>
        </div>
      </main>
    </RepoShell>
  );
}
