export type ScenarioRun = {
  runType: string;
  inputPayload: unknown;
  predictedKg: number;
  baselineKg: number | null;
  createdAt: Date | string;
};

export function findLatestCompletedScenario<T extends ScenarioRun>(runs: T[]): T | null {
  for (const baselineRun of runs) {
    if (baselineRun.runType !== "baseline" || baselineRun.baselineKg === null) continue;
    const baselinePayload = JSON.stringify(baselineRun.inputPayload);
    const matchingPrediction = runs.find(run => run.runType === "prediction" && JSON.stringify(run.inputPayload) === baselinePayload);
    if (matchingPrediction) return baselineRun;
  }
  return null;
}
