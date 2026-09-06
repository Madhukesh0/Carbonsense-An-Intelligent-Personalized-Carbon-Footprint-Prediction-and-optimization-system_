import { describe, expect, it } from "vitest";
import {
  assessProphetEligibility,
  PROPHET_MIN_COMPLETE_MONTHS,
  PROPHET_MIN_DISTINCT_ACTIVITY_DAYS,
  summarizeLedgerForProphet,
} from "./prophetForecast";

const monthStart = (year: number, monthIndex: number) => new Date(Date.UTC(year, monthIndex, 1));

describe("Prophet activity-history policy", () => {
  it("aggregates recorded ledger rows by completed UTC month and excludes the live partial month", () => {
    const now = new Date(Date.UTC(2026, 7, 21));
    const summary = summarizeLedgerForProphet([
      { activityDate: new Date(Date.UTC(2026, 5, 2)), co2Kg: 12 },
      { activityDate: new Date(Date.UTC(2026, 5, 8)), co2Kg: 8 },
      { activityDate: new Date(Date.UTC(2026, 6, 4)), co2Kg: 20 },
      { activityDate: new Date(Date.UTC(2026, 7, 4)), co2Kg: 99 },
    ], now);

    expect(summary.months).toEqual([
      { ds: "2026-06-01", y: 20 },
      { ds: "2026-07-01", y: 20 },
    ]);
    expect(summary.distinctActivityDays).toBe(3);
  });

  it("does not activate Prophet for a short or interrupted personal history", () => {
    const shortHistory = { months: [{ ds: "2026-01-01", y: 400 }], distinctActivityDays: 1 };
    const shortAssessment = assessProphetEligibility(shortHistory);
    expect(shortAssessment.eligible).toBe(false);
    expect(shortAssessment.reason).toContain(`${PROPHET_MIN_COMPLETE_MONTHS} completed months`);

    const interruptedHistory = {
      months: Array.from({ length: 12 }, (_, index) => ({ ds: monthStart(2025, index === 6 ? 7 : index).toISOString().slice(0, 10), y: 420 - index })),
      distinctActivityDays: PROPHET_MIN_DISTINCT_ACTIVITY_DAYS,
    };
    const interruptedAssessment = assessProphetEligibility(interruptedHistory);
    expect(interruptedAssessment.eligible).toBe(false);
    expect(interruptedAssessment.reason).toContain("uninterrupted");
  });

  it("activates Prophet only after the required monthly coverage and activity-day evidence are available", () => {
    const completeHistory = {
      months: Array.from({ length: PROPHET_MIN_COMPLETE_MONTHS }, (_, index) => ({ ds: monthStart(2025, index).toISOString().slice(0, 10), y: 420 - index * 2 })),
      distinctActivityDays: PROPHET_MIN_DISTINCT_ACTIVITY_DAYS,
    };
    const assessment = assessProphetEligibility(completeHistory);
    expect(assessment).toMatchObject({
      eligible: true,
      reason: null,
      completeMonths: PROPHET_MIN_COMPLETE_MONTHS,
      distinctActivityDays: PROPHET_MIN_DISTINCT_ACTIVITY_DAYS,
    });
  });
});
