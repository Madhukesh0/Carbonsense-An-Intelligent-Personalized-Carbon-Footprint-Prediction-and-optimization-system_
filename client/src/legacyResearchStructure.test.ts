import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("legacy research structure compatibility", () => {
  const root = process.cwd();

  it("retains the supplied research data, models, reports, and safe retraining entrypoints", () => {
    for (const path of ["data/DATA_CARD.md", "data/processed/train_X.csv", "models/trained/best_carbon_model.joblib", "reports/README.md", "retrain.py", "retrain_regional.py"]) {
      expect(existsSync(resolve(root, path))).toBe(true);
    }
  });

  it("provides the requested Wren-inspired frontend compatibility tree without duplicating active source", () => {
    for (const path of [
      "carbonsense-frontend-wren-inspired/carbonsense-frontend/src/App.jsx",
      "carbonsense-frontend-wren-inspired/carbonsense-frontend/src/pages/Predict.jsx",
      "carbonsense-frontend-wren-inspired/carbonsense-frontend/src/pages/Explore.jsx",
      "carbonsense-frontend-wren-inspired/carbonsense-frontend/src/pages/Baseline.jsx",
      "carbonsense-frontend-wren-inspired/carbonsense-frontend/src/pages/Dashboard.jsx",
    ]) expect(existsSync(resolve(root, path))).toBe(true);
  });
});
