import { spawn } from "node:child_process";
import { resolve } from "node:path";

export type LedgerForecastRow = {
  activityDate: Date | string;
  co2Kg: number;
};

export type MonthlyLedgerPoint = {
  ds: string;
  y: number;
};

export type LedgerHistorySummary = {
  months: MonthlyLedgerPoint[];
  distinctActivityDays: number;
};

export type ProphetEligibility = {
  eligible: boolean;
  reason: string | null;
  completeMonths: number;
  distinctActivityDays: number;
  requiredCompleteMonths: number;
  requiredDistinctActivityDays: number;
};

export type ProphetForecastPoint = {
  ds: string;
  yhat: number;
  yhatLower: number;
  yhatUpper: number;
};

export type ProphetForecastResult = {
  engine: "prophet";
  packageVersion: string;
  horizonMonths: number;
  intervalWidth: number;
  points: ProphetForecastPoint[];
};

export const PROPHET_MIN_COMPLETE_MONTHS = 12;
export const PROPHET_MIN_DISTINCT_ACTIVITY_DAYS = 90;
export const PROPHET_HORIZON_MONTHS = 6;

function dateKey(date: Date) {
  return date.toISOString().slice(0, 10);
}

function monthKey(date: Date) {
  return `${date.getUTCFullYear()}-${String(date.getUTCMonth() + 1).padStart(2, "0")}-01`;
}

function isConsecutiveMonthlySeries(months: MonthlyLedgerPoint[]) {
  if (months.length < 2) return true;
  for (let index = 1; index < months.length; index += 1) {
    const previous = new Date(`${months[index - 1]!.ds}T00:00:00.000Z`);
    const current = new Date(`${months[index]!.ds}T00:00:00.000Z`);
    const expected = Date.UTC(previous.getUTCFullYear(), previous.getUTCMonth() + 1, 1);
    if (current.getTime() !== expected) return false;
  }
  return true;
}

/**
 * Aggregate only completed UTC calendar months. The live month is deliberately
 * excluded because an unfinished month would make a time-series target partial.
 */
export function summarizeLedgerForProphet(rows: LedgerForecastRow[], now = new Date()): LedgerHistorySummary {
  const currentMonthStart = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), 1);
  const monthTotals = new Map<string, number>();
  const activityDays = new Set<string>();

  for (const row of rows) {
    const date = new Date(row.activityDate);
    if (!Number.isFinite(date.getTime()) || !Number.isFinite(row.co2Kg) || row.co2Kg < 0) continue;
    if (date.getTime() >= currentMonthStart) continue;
    const key = monthKey(date);
    monthTotals.set(key, (monthTotals.get(key) ?? 0) + row.co2Kg);
    activityDays.add(dateKey(date));
  }

  return {
    months: Array.from(monthTotals.entries())
      .map(([ds, y]) => ({ ds, y: Math.round(y * 100) / 100 }))
      .sort((left, right) => left.ds.localeCompare(right.ds)),
    distinctActivityDays: activityDays.size,
  };
}

export function assessProphetEligibility(summary: LedgerHistorySummary): ProphetEligibility {
  const completeMonths = summary.months.length;
  if (completeMonths < PROPHET_MIN_COMPLETE_MONTHS) {
    return {
      eligible: false,
      reason: `Prophet needs at least ${PROPHET_MIN_COMPLETE_MONTHS} completed months of recorded history; ${completeMonths} are currently available.`,
      completeMonths,
      distinctActivityDays: summary.distinctActivityDays,
      requiredCompleteMonths: PROPHET_MIN_COMPLETE_MONTHS,
      requiredDistinctActivityDays: PROPHET_MIN_DISTINCT_ACTIVITY_DAYS,
    };
  }
  if (!isConsecutiveMonthlySeries(summary.months)) {
    return {
      eligible: false,
      reason: "Prophet needs uninterrupted completed monthly totals. Record activity in every month before using the model-based forecast.",
      completeMonths,
      distinctActivityDays: summary.distinctActivityDays,
      requiredCompleteMonths: PROPHET_MIN_COMPLETE_MONTHS,
      requiredDistinctActivityDays: PROPHET_MIN_DISTINCT_ACTIVITY_DAYS,
    };
  }
  if (summary.distinctActivityDays < PROPHET_MIN_DISTINCT_ACTIVITY_DAYS) {
    return {
      eligible: false,
      reason: `Prophet needs activity recorded on at least ${PROPHET_MIN_DISTINCT_ACTIVITY_DAYS} distinct days; ${summary.distinctActivityDays} are currently available.`,
      completeMonths,
      distinctActivityDays: summary.distinctActivityDays,
      requiredCompleteMonths: PROPHET_MIN_COMPLETE_MONTHS,
      requiredDistinctActivityDays: PROPHET_MIN_DISTINCT_ACTIVITY_DAYS,
    };
  }
  return {
    eligible: true,
    reason: null,
    completeMonths,
    distinctActivityDays: summary.distinctActivityDays,
    requiredCompleteMonths: PROPHET_MIN_COMPLETE_MONTHS,
    requiredDistinctActivityDays: PROPHET_MIN_DISTINCT_ACTIVITY_DAYS,
  };
}

export async function runProphetForecast(history: MonthlyLedgerPoint[], horizonMonths = PROPHET_HORIZON_MONTHS): Promise<ProphetForecastResult> {
  const workerPath = resolve(process.cwd(), "server/model_runtime/prophet_forecast.py");
  const payload = JSON.stringify({ history, horizonMonths });

  const isWin = process.platform === "win32";
  const pythonCommand = process.env.PYTHON_EXECUTABLE || (isWin ? "py" : "python3");
  const pythonArgs = isWin ? ["-3.12", workerPath] : [workerPath];
  return new Promise((resolvePromise, rejectPromise) => {
    const child = spawn(pythonCommand, pythonArgs, { stdio: ["pipe", "pipe", "pipe"] });
    let stdout = "";
    let stderr = "";
    const timer = setTimeout(() => {
      child.kill("SIGKILL");
      rejectPromise(new Error("Prophet forecast exceeded the 20-second request budget."));
    }, 20_000);

    child.stdout.on("data", chunk => { stdout += String(chunk); });
    child.stderr.on("data", chunk => { stderr += String(chunk); });
    child.on("error", error => {
      clearTimeout(timer);
      rejectPromise(error);
    });
    child.on("close", code => {
      clearTimeout(timer);
      if (code !== 0) {
        rejectPromise(new Error(`Prophet worker failed (${code}): ${stderr.trim() || "no error details"}`));
        return;
      }
      try {
        const parsed = JSON.parse(stdout) as ProphetForecastResult & { error?: string };
        if (parsed.error) throw new Error(parsed.error);
        if (parsed.engine !== "prophet" || parsed.points.length !== horizonMonths) {
          throw new Error("Prophet worker returned an invalid forecast payload.");
        }
        for (const point of parsed.points) {
          if (![point.yhat, point.yhatLower, point.yhatUpper].every(Number.isFinite)) {
            throw new Error("Prophet worker returned a non-finite forecast value.");
          }
        }
        resolvePromise(parsed);
      } catch (error) {
        rejectPromise(error instanceof Error ? error : new Error("Unable to parse the Prophet worker response."));
      }
    });
    child.stdin.end(payload);
  });
}
