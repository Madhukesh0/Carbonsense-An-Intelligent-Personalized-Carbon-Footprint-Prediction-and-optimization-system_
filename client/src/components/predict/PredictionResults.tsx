import { useState } from "react";
import { Link } from "wouter";
import { ArrowRight, Check, CircleHelp, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import RepoShell from "@/components/RepoShell";
import {
  contributionEffect,
  contributionScale,
  rankContributions,
  surveyAnswersText,
} from "@/utils/predictionResults";

type PredictionResultsProps = {
  result: any;
  onReset: () => void;
};

export default function PredictionResults({ result, onReset }: PredictionResultsProps) {
  const [tab, setTab] = useState("prediction");
  const [computedBase, setComputedBase] = useState<any>(null);
  const [computingBase, setComputingBase] = useState(false);
  const [baseError, setBaseError] = useState<string | null>(null);
  const baselineResult = computedBase ?? result.base ?? null;
  const needsBaselineCompute = !baselineResult && !!result.submittedPayload;
  // v2.5 responses include `explanation`; guard against a missing SHAP block
  // so a runtime hiccup degrades to the number instead of crashing the page.
  if (!result?.shap?.contributions?.length) {
    result = { ...result, shap: { ...(result?.shap ?? {}), contributions: [], baseValue: result?.shap?.baseValue ?? 0 } };
  }
  if (!result?.base) {
    result = { ...result, base: { breakdown: {}, total: 0, sources: [], assumptions: [], factorSet: null, sourceReferences: [] } };
  }
  const rankedContributions = rankContributions(result.shap.contributions);
  const largestContribution = contributionScale(rankedContributions);
  const strongestInfluence = rankedContributions[0];
  const strongestEffect = contributionEffect(strongestInfluence?.direction);
  const answers: Record<string, unknown> = result.submittedAnswers ?? {};
  // Groups the questionnaire no longer asks (dataset reference values, no
  // emission mechanism) stay in the ranked breakdown but are excluded from
  // the plain-language "your answers" card, which only lists user choices.
  const notAsked = new Set(["profile_fields", "shower_frequency", "social_activity", "energy_efficiency"]);
  const pushUps = rankedContributions.filter((item: any) => item.shapValue > 0 && !notAsked.has(item.feature));
  const pushDowns = rankedContributions.filter((item: any) => item.shapValue < 0 && !notAsked.has(item.feature));
  const computeBaseline = async () => {
    setComputingBase(true);
    setBaseError(null);
    try {
      const response = await fetch("/api/v1/model/baseline-compute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ ...(result.submittedPayload ?? {}) }),
      });
      if (!response.ok) throw new Error(`Baseline computation failed (${response.status})`);
      setComputedBase(await response.json());
    } catch (error: any) {
      setBaseError(error?.message || "Baseline computation failed");
    } finally {
      setComputingBase(false);
    }
  };

  const exportReport = () => {
    document.title = `CarbonSense report · ${Math.round(result.predictedKg)} kgCO2e`;
    window.print();
    window.setTimeout(() => {
      document.title = "CarbonSense";
    }, 500);
  };

  const baselineAvailable = !!baselineResult && Number(baselineResult.total) > 0;
  const aiKg = Math.round(result.predictedKg);
  const baselineTotal = baselineAvailable ? Math.round(baselineResult.total) : null;
  const gapKg = baselineTotal !== null ? aiKg - baselineTotal : null;
  const gapPct = baselineTotal !== null && baselineTotal > 0 ? Math.round(Math.abs(gapKg!) / baselineTotal * 1000) / 10 : null;

  return (
    <RepoShell>
      <main className="mx-auto max-w-7xl px-4 py-10 lg:px-8">
        <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
          <div>
            <span className="text-sm font-semibold uppercase tracking-[.18em] text-[#157f54]">
              {result.qa?.nonPersistent ? "Model quality assurance preview" : "Your climate snapshot"}
            </span>
            <h1 className="mt-2 text-4xl font-semibold tracking-tight">
              A number you can work with.
            </h1>
            <p className="mt-3 text-slate-500">
              Region: <strong>{result.region}</strong> · Currency: <strong>{result.currency}</strong>
            </p>
            {result.qa?.nonPersistent && (
              <p className="mt-2 text-sm font-medium text-amber-700">
                Non-persistent fixed profile: no user record or footprint run is created.
              </p>
            )}
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={exportReport}>
              Export report
            </Button>
            <Button variant="outline" onClick={onReset}>
              Run another estimate
            </Button>
          </div>
        </div>

        <div className="mt-8 grid gap-5 lg:grid-cols-[1.2fr_.8fr]">
          <Card className="cs-signal-result border-0 p-7 text-white">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-[#b8d5cb]">Estimated monthly footprint</p>
                <p className="mt-4 text-6xl font-semibold tracking-[-.06em]">
                  {Math.round(result.predictedKg)}{" "}
                  <span className="text-xl font-normal text-[#b8d5cb]">kgCO₂e</span>
                </p>
                <p className="mt-3 text-sm text-[#b8d5cb]">
                  Indicative range {Math.round(result.uncertaintyRange.low)}–
                  {Math.round(result.uncertaintyRange.high)} kgCO₂e/month
                </p>
              </div>
              <span className="rounded-full border border-emerald-100/15 bg-emerald-300/10 px-3 py-1 font-mono text-[0.64rem] font-medium tracking-[0.09em] text-emerald-100">
                {result.modelVersion}
              </span>
            </div>
            <div className="mt-8 grid gap-3 sm:grid-cols-3">
              <div className="rounded-2xl bg-white/10 p-4">
                <p className="text-xs text-[#b8d5cb]">Dataset</p>
                <p className="mt-2 font-semibold">{result.datasetVersion}</p>
              </div>
              <div className="rounded-2xl bg-white/10 p-4">
                <p className="text-xs text-[#b8d5cb]">Input contract</p>
                <p className="mt-2 font-semibold">
                  {result.runtime?.rawFeatureCount ?? 26} → {result.runtime?.transformedFeatureCount ?? 44} features
                </p>
              </div>
              <div className="rounded-2xl bg-white/10 p-4">
                <p className="text-xs text-[#b8d5cb]">Live model</p>
                <p className="mt-2 font-semibold">{result.runtime?.engine ?? "Gradient Boosting"} inference</p>
                {result.inferenceMs !== undefined && (
                  <p className="mt-1 text-xs text-[#b8d5cb]">{result.inferenceMs} ms</p>
                )}
              </div>
            </div>
          </Card>
          <Card className="cs-card cs-instrument-card border-0 p-7">
            <div className="flex items-center gap-2 text-[#157f54]">
              <ShieldCheck size={18} />
              <span className="text-sm font-semibold">Method & data</span>
            </div>
            <p className="mt-4 text-lg font-semibold">Understand the method behind this result.</p>
            <p className="mt-3 text-sm leading-6 text-slate-500">
              Review the feature contract, current runtime, assumptions, dataset governance, and
              result interpretation in the CarbonSense methods.
            </p>
            <Link href="/about">
              <Button variant="link" className="mt-3 px-0 text-[#157f54]">
                Read the methodology <ArrowRight size={15} className="ml-2" />
              </Button>
            </Link>
          </Card>
        </div>

        <Card className="cs-card border-0 p-7">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[.16em] text-[#157f54]">
                Two methods, one factor set
              </p>
              <h2 className="mt-2 text-xl font-semibold">AI estimate vs transparent baseline</h2>
              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                Both numbers use the same cited emission factors (Ember 2025 grid, IPCC fuel
                chemistry, Scarborough diet, OWID air bands). The AI model learned the
                relationship from 10,000 factor-formula examples; the baseline multiplies your
                answers by the factors directly. The two numbers are never averaged.
              </p>
            </div>
            {gapPct !== null && (
              <span className={`rounded-full px-3 py-1 text-xs font-semibold ${gapPct <= 10 ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300" : "bg-amber-50 text-amber-800 dark:bg-amber-950/60 dark:text-amber-200"}`}>
                {gapPct <= 10 ? "Methods agree" : "Methods diverge"} · {gapPct}%
              </span>
            )}
          </div>
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl bg-[#173126] p-5 text-white">
              <p className="text-xs font-semibold uppercase tracking-[.12em] text-[#b8d5cb]">AI model estimate</p>
              <p className="mt-3 text-4xl font-semibold">{aiKg} <span className="text-base font-normal text-[#b8d5cb]">kgCO₂e</span></p>
              <p className="mt-2 text-xs leading-5 text-[#b8d5cb]">
                XGBoost on {result.datasetVersion} · uncertainty ±{Math.round(result.uncertaintyRange.high - result.predictedKg)} kg
              </p>
            </div>
            <div className="rounded-2xl bg-emerald-50 p-5 dark:bg-emerald-950/40">
              <p className="text-xs font-semibold uppercase tracking-[.12em] text-emerald-700 dark:text-emerald-300">Transparent baseline</p>
              {baselineAvailable ? (
                <>
                  <p className="mt-3 text-4xl font-semibold text-emerald-800 dark:text-emerald-200">{baselineTotal} <span className="text-base font-normal text-emerald-600/70 dark:text-emerald-400/70">kgCO₂e</span></p>
                  <p className="mt-2 text-xs leading-5 text-emerald-700/80 dark:text-emerald-300/80">
                    Published-factor formula over your answers · deterministic, fully auditable
                  </p>
                </>
              ) : (
                <>
                  <p className="mt-3 text-4xl font-semibold text-emerald-800/50 dark:text-emerald-200/50">— <span className="text-base font-normal text-emerald-600/50 dark:text-emerald-400/50">kgCO₂e</span></p>
                  <Button size="sm" className="mt-3 bg-[#157f54] hover:bg-[#106b47]" onClick={computeBaseline} disabled={computingBase}>
                    {computingBase ? "Calculating…" : "Calculate my baseline"}
                  </Button>
                  {baseError && <p role="alert" className="mt-2 text-xs text-red-600">{baseError}</p>}
                </>
              )}
            </div>
          </div>
          {baselineAvailable && (
            <div className="mt-5 rounded-xl bg-[#f6f8f7] p-4 dark:bg-emerald-950/30">
              <p className="text-sm leading-6 text-slate-600 dark:text-slate-300">
                {gapKg !== null && Math.abs(gapKg) <= 5
                  ? "The model and the formula land within 5 kg of each other on your answers — the learned relationship and the factor arithmetic agree almost exactly here."
                  : gapKg !== null && gapKg > 0
                    ? `The model sits ${Math.abs(gapKg)} kg above the formula for your answers. Learned tree interactions see more impact in this profile than the single-path factor arithmetic does; the truth window includes both.`
                    : gapKg !== null
                      ? `The model sits ${Math.abs(gapKg)} kg below the formula for your answers. Some factor lines (for example screening bands) count more than the learned trees do at these values; the truth window includes both.`
                      : ""}
                {" "}Check the Baseline tab for the line-by-line arithmetic.
              </p>
            </div>
          )}
        </Card>

        <Tabs value={tab} onValueChange={setTab} className="mt-8">
          <TabsList className="rounded-xl bg-[#e8f0ec] p-1">
            <TabsTrigger value="prediction" className="rounded-lg data-[state=active]:bg-white">
              AI prediction
            </TabsTrigger>
            <TabsTrigger value="baseline" className="rounded-lg data-[state=active]:bg-white">
              Baseline calculator
            </TabsTrigger>
          </TabsList>
          <TabsContent value="prediction">
            <Card className="cs-card cs-instrument-card mb-5 border-0 p-7">
              <p className="text-sm font-semibold uppercase tracking-[.16em] text-[#157f54]">
                Your answers, translated
              </p>
              <h2 className="mt-2 text-xl font-semibold">Which of your choices raised or lowered the estimate?</h2>
              <p className="mt-2 text-sm leading-6 text-slate-500">
                Each answer you submitted is compared with the average person in the model's training
                data. Positive amounts pushed your estimate above that average; negative amounts pulled
                it below.
              </p>
              <div className="mt-5 grid gap-4 md:grid-cols-2">
                <div className="rounded-2xl border border-[#f3ded5] bg-[#fdf6f2] p-5 dark:border-[#ba5b3d]/25 dark:bg-[#ba5b3d]/10">
                  <p className="text-sm font-semibold text-[#ba5b3d]">Pushed your estimate up</p>
                  {pushUps.length === 0 ? (
                    <p className="mt-3 text-sm text-slate-500">
                      Nothing pushed your estimate above the average profile.
                    </p>
                  ) : (
                    <ul className="mt-3 space-y-2.5">
                      {pushUps.map((item: any) => (
                        <li key={item.feature} className="flex items-start justify-between gap-3 text-sm">
                          <span className="leading-6 text-slate-700 dark:text-slate-200">
                            {surveyAnswersText(item.feature, answers)}
                          </span>
                          <span className="shrink-0 font-semibold text-[#ba5b3d]">
                            +{item.shapValue} kg
                          </span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
                <div className="rounded-2xl border border-[#dcebe3] bg-[#f2f9f5] p-5 dark:border-emerald-300/15 dark:bg-emerald-950/30">
                  <p className="text-sm font-semibold text-[#157f54]">Pulled your estimate down</p>
                  {pushDowns.length === 0 ? (
                    <p className="mt-3 text-sm text-slate-500">
                      Nothing pulled your estimate below the average profile.
                    </p>
                  ) : (
                    <ul className="mt-3 space-y-2.5">
                      {pushDowns.map((item: any) => (
                        <li key={item.feature} className="flex items-start justify-between gap-3 text-sm">
                          <span className="leading-6 text-slate-700 dark:text-slate-200">
                            {surveyAnswersText(item.feature, answers)}
                          </span>
                          <span className="shrink-0 font-semibold text-[#157f54]">
                            {item.shapValue} kg
                          </span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
              <p className="mt-4 text-xs leading-5 text-slate-500 dark:text-slate-400">
                Amounts are model contributions relative to the training-data average, not savings or
                offsets. They describe model behavior, not a direct or causal emissions measurement.
              </p>
            </Card>
            <div className="grid gap-5 py-5 lg:grid-cols-[1.3fr_.7fr]">
              <Card className="cs-card cs-instrument-card border-0 p-7">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <p className="text-sm font-semibold uppercase tracking-[.16em] text-[#157f54]">
                      Live model breakdown
                    </p>
                    <h2 className="mt-2 text-xl font-semibold">What is influencing this result?</h2>
                  </div>
                  <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-800">
                    Model recalculated
                  </span>
                </div>
                <p className="mt-2 text-sm text-slate-500">
                  Ranked from the answers you just submitted by the frozen model. Run
                  another estimate after changing a value to see the contribution order update.
                </p>
                {strongestInfluence && (
                  <div className="mt-5 rounded-2xl border border-emerald-900/10 bg-emerald-50/70 p-4 dark:border-emerald-300/15 dark:bg-emerald-950/30">
                    <p className="cs-data-label text-emerald-800 dark:text-emerald-200">
                      For this saved result
                    </p>
                    <p className="mt-2 text-sm leading-6 text-slate-700 dark:text-slate-200">
                      <span className="font-semibold">{strongestInfluence.label}</span> is the
                      strongest modeled influence in this submitted profile. It {strongestEffect}
                      the model estimate by approximately{" "}
                      <span className="font-semibold">
                        {Math.abs(strongestInfluence.shapValue).toFixed(1)} kgCO₂e
                      </span>{" "}
                      relative to the model’s base value.
                    </p>
                    <p className="mt-2 text-xs leading-5 text-slate-500 dark:text-slate-400">
                      This explanation is calculated from the live model inference for your
                      submitted answers. It describes model behavior, not a direct or causal
                      emissions measurement.
                    </p>
                  </div>
                )}
                <div className="mt-6 space-y-3">
                  {rankedContributions.map((item: any, index: number) => (
                    <div
                      key={item.feature}
                      className={`cs-contribution-row rounded-2xl border border-[#e4ece8] p-4 ${item.direction === "increases" ? "cs-contribution-row--increase" : "cs-contribution-row--decrease"}`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-medium">
                          <span className="mr-2 font-mono text-xs text-slate-400">0{index + 1}</span>
                          {item.label}
                        </span>
                        <span
                          className={
                            item.direction === "increases"
                              ? "font-semibold text-[#ba5b3d]"
                              : "font-semibold text-[#157f54]"
                          }
                        >
                          {item.shapValue > 0 ? "+" : ""}
                          {item.shapValue} kg
                        </span>
                      </div>
                      <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-slate-100">
                        <div
                          className={
                            item.direction === "increases"
                              ? "h-full rounded-full bg-[#ba5b3d]"
                              : "h-full rounded-full bg-[#157f54]"
                          }
                          style={{
                            width: `${Math.max(8, Math.round((Math.abs(item.shapValue) / largestContribution) * 100))}%`,
                          }}
                        />
                      </div>
                      <div className="mt-2 flex items-center justify-between text-xs text-slate-500">
                        <span>{item.direction === "increases" ? "Raises this result" : "Lowers this result"}</span>
                        <span>Model contribution</span>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
              <Card className="cs-feature-callout cs-action-panel cs-card border-0 p-7">
                <p className="cs-data-label">Model reconciliation</p>
                <p className="mt-4 text-4xl font-semibold">
                  {result.shap.reconciliation} <span className="text-base font-normal">kg</span>
                </p>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  Base value {result.shap.baseValue} + contribution values = predicted value.{" "}
                  {result.shap.note}
                </p>
                {result.disclaimer && (
                  <p className="mt-4 rounded-xl bg-amber-50 p-3 text-xs leading-5 text-amber-800 dark:bg-amber-950 dark:text-amber-200">
                    {result.disclaimer}
                  </p>
                )}
                <p className="mt-6 text-sm font-semibold text-slate-900 dark:text-white">
                  Turn this signal into one practical next step.
                </p>
                <Link href="/result-recommendations">
                  <Button className="mt-6 w-full bg-[#157f54] hover:bg-[#106b47]">
                    Get my recommendations <ArrowRight size={16} className="ml-2" />
                  </Button>
                </Link>
                {!result.qa?.nonPersistent && (
                  <Link href="/whatif">
                    <Button
                      variant="outline"
                      className="mt-3 w-full border-emerald-700 text-emerald-800 hover:bg-emerald-50"
                    >
                      Test a What-if scenario from this result <ArrowRight size={16} className="ml-2" />
                    </Button>
                  </Link>
                )}
              </Card>
            </div>
          </TabsContent>
          <TabsContent value="baseline">
            {needsBaselineCompute ? (
              <Card className="cs-card mx-auto max-w-3xl border-0 p-7 text-center">
                <h2 className="text-xl font-semibold">Transparent baseline</h2>
                <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-slate-500">
                  The transparent baseline is a separate, fully auditable calculation using
                  published emission factors - computed on demand from the same answers you
                  submitted, independent of the AI model. It is never averaged with the model
                  estimate.
                </p>
                <Button className="mt-5 bg-[#157f54] hover:bg-[#106b47]" onClick={computeBaseline} disabled={computingBase}>
                  {computingBase ? "Calculating…" : "Calculate my transparent baseline"}
                </Button>
                {baseError && <p role="alert" className="mt-4 text-sm text-red-600">{baseError}</p>}
              </Card>
            ) : (
            <div className="grid gap-5 py-5 lg:grid-cols-[1.2fr_.8fr]">
              <Card className="border-0 bg-white p-7 shadow-sm">
                <h2 className="text-xl font-semibold">Transparent baseline</h2>
                <p className="mt-1 text-xs text-slate-400">
                  {baselineResult.country ? `Country: ${baselineResult.country.toUpperCase()} · grid ${baselineResult.gridFactorKgPerKwh} kgCO2e/kWh · household ${baselineResult.householdSize}` : ""}
                </p>
                <div className="mt-6 space-y-3">
                  {Object.entries(baselineResult.breakdown).map(([label, value]: any) => (
                    <div key={label} className="rounded-xl bg-[#f6f8f7] p-4">
                      <div className="flex items-center justify-between">
                        <span className="capitalize font-medium text-slate-700">{label}</span>
                        <span className="font-semibold">{Math.round(value)} kg</span>
                      </div>
                      {baselineResult.arithmetic?.[label] && (
                        <p className="mt-1.5 text-xs text-slate-400">{baselineResult.arithmetic[label]}</p>
                      )}
                    </div>
                  ))}
                </div>
                <div className="mt-6 flex items-end justify-between border-t border-[#e4ece8] pt-5">
                  <span className="font-semibold">Rule-based total</span>
                  <span className="text-3xl font-semibold text-[#157f54]">
                    {Math.round(baselineResult.total)} kg
                  </span>
                </div>
              </Card>
              <Card className="border-0 bg-white p-7 shadow-sm">
                <div className="flex items-center gap-2 text-[#157f54]">
                  <CircleHelp size={18} />
                  <span className="font-semibold">Assumptions & sources</span>
                </div>
                <ul className="mt-5 space-y-3 text-sm leading-6 text-slate-600">
                  {baselineResult.assumptions.map((item: string) => (
                    <li key={item} className="flex gap-2">
                      <Check size={16} className="mt-1 shrink-0 text-[#157f54]" />
                      {item}
                    </li>
                  ))}
                </ul>
                <div className="mt-6 rounded-2xl bg-[#f6f8f7] p-4 text-sm">
                  <p className="font-semibold">Sources</p>
                  <p className="mt-2 text-slate-500">{baselineResult.sources.join(" · ")}</p>
                  {baselineResult.factorSet && (
                    <p className="mt-3 font-mono text-xs tracking-[0.04em] text-slate-500">
                      Factor set: {baselineResult.factorSet.label}
                    </p>
                  )}
                  {baselineResult.sourceReferences?.length > 0 && (
                    <div className="mt-3 space-y-2 text-xs leading-5">
                      <p className="font-semibold text-slate-700">Primary source links</p>
                      {baselineResult.sourceReferences.map(
                        (source: { label: string; url: string; coverage: string }) => (
                          <a
                            key={source.url}
                            href={source.url}
                            target="_blank"
                            rel="noreferrer"
                            className="block text-[#157f54] underline underline-offset-2"
                          >
                            {source.label}
                            <span className="block text-slate-500 no-underline">{source.coverage}</span>
                          </a>
                        )
                      )}
                    </div>
                  )}
                </div>
              </Card>
            </div>
            )}
          </TabsContent>
        </Tabs>
      </main>
    </RepoShell>
  );
}
