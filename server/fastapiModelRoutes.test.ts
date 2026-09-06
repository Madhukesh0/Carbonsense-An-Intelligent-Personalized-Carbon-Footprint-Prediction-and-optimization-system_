import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const project = process.cwd();
const read = (relative: string) => readFileSync(resolve(project, relative), "utf8");

describe("FastAPI model and baseline migration", () => {
  it("serves the v2.5 runtime with integrity checks and the grid-factor contract", () => {
    const source = read("backend/app/services/prediction.py");
    expect(source).toContain("Artifact integrity check failed");
    expect(source).toContain("v2.5 artifact integrity check failed");
    expect(source).toContain("artifacts_v25");
    expect(source).toContain("GRID_FACTORS = {\"india\": 0.67013, \"us\": 0.38440, \"uk\": 0.21741}");
    expect(source).toContain("def run_prediction_v25");
    expect(source).toContain("conformal_prediction");
  });

  it("preserves the v2.5-aligned baseline factors and non-averaging comparison rule", () => {
    const source = read("backend/app/services/baseline.py");
    const route = read("backend/app/routers/model.py");
    expect(source).toContain('"id": "carbonsense-v25-aligned-cited-factors"');
    expect(source).toContain('"gridByCountry": {"india": 0.67013, "us": 0.38440, "uk": 0.21741}');
    expect(source).toContain('"transitKgPerPassengerKm": 0.02');
    expect(source).toContain("household_size");
    expect(route).toContain("does not average the AI estimate and transparent baseline");
  });

  it("defines protected prediction, explanation, baseline, and super-admin non-persistent preview routes", () => {
    const source = read("backend/app/routers/model.py");
    expect(source).toContain('@router.post("/predict")');
    expect(source).toContain('@router.post("/explain")');
    expect(source).toContain('@router.post("/baseline")');
    expect(source).toContain('require_roles("super_admin")');
    expect(source).toContain('"nonPersistent": True');
  });
});
