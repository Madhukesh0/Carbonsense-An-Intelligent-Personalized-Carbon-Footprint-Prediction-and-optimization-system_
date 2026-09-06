import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const requirements = readFileSync(resolve(process.cwd(), "requirements.txt"), "utf8");
const dockerfile = readFileSync(resolve(process.cwd(), "Dockerfile"), "utf8");

describe("production Python runtime", () => {
  it("uses Python 3.12 for the pinned XGBoost runtime and keeps a compatible NumPy pin", () => {
    expect(dockerfile).toContain("FROM python:3.12-slim");
    expect(dockerfile).toContain("setup_22.x");
    expect(requirements).toMatch(/^numpy==2\.4\.6$/m);
    expect(requirements).not.toContain("numpy==2.5.1");
    expect(requirements).toMatch(/^xgboost==3\.4\.1$/m);
  });
});
