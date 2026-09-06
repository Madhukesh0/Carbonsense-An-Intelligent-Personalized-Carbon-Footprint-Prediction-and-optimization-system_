import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const landingSource = readFileSync(resolve(process.cwd(), "client/src/pages/Dashboard.tsx"), "utf8");
const interfaceStyles = readFileSync(resolve(process.cwd(), "client/src/repo-interface.css"), "utf8");

describe("RepoLanding home hero", () => {
  it("uses a CarbonSense-specific visual and retains the core entry points", () => {
    expect(landingSource).toContain("/manus-storage/carbonsense-project-hero_31f48737.jpg");
    expect(landingSource).toContain("Personal climate intelligence");
    expect(landingSource).toContain("Calculate your baseline");
    expect(landingSource).toContain("Explore AI prediction");
    expect(landingSource).toContain("Estimate");
    expect(landingSource).toContain("Compare transparently");
    expect(landingSource).toContain("Plan your next move");
  });

  it("keeps the hero visual text-safe and responsive", () => {
    expect(interfaceStyles).toContain(".cs-hero-bg::after");
    expect(interfaceStyles).toContain(".cs-hero-proof");
    expect(interfaceStyles).toContain("@media (max-width: 639px) { .cs-hero-bg img");
  });
});
