import { describe, expect, it } from "vitest";
import { contractColumns, DERIVED_MODEL_COLUMN_COUNT, derivedColumns, DIRECT_MODEL_VALUE_COUNT, directlyEnteredModelColumns, TOTAL_INTERACTIVE_QUESTIONS } from "./predictContract";

describe("frozen Predict contract", () => {
  it("keeps the deployed 26-column, 12-direct, 9-derived model boundary intact", () => {
    expect(TOTAL_INTERACTIVE_QUESTIONS).toBe(15);
    expect(contractColumns).toHaveLength(26); // model contract unchanged; form asks 17
    expect(DIRECT_MODEL_VALUE_COUNT).toBe(14);
    expect(DERIVED_MODEL_COLUMN_COUNT).toBe(9);
    expect(directlyEnteredModelColumns).toHaveLength(17);
    expect(derivedColumns).toHaveLength(9);
    expect(contractColumns).toContain("recycle_paper");
    expect(directlyEnteredModelColumns).toContain("transport");
    // The contract must match the deployed GradientBoosting runtime: no
    // retired regional/interaction columns from the old 54-feature build.
    expect(contractColumns).not.toContain("region_grid_factor");
    expect(contractColumns).not.toContain("region");
    expect(contractColumns).not.toContain("energy_proxy");
  });
});
