import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

describe("ContributorAggregateMap", () => {
  const source = readFileSync(resolve(process.cwd(), "client/src/components/charts/WorldMap.tsx"), "utf8");

  it("uses the supplied zoomable map component with country-level aggregate markers", () => {
    expect(source).toContain('import { MapView } from "@/components/Map"');
    expect(source).toContain("Zoomable world map of consented aggregate contributor coverage");
    expect(source).toContain("COUNTRY_CENTERS");
    expect(source).toContain("AdvancedMarkerElement");
    expect(source).toContain("Country-level aggregates only");
    expect(source).not.toContain("WorldMapEmptyBackdrop");
  });

  it("keeps map content aggregate-only and makes markers update from the supplied country rows", () => {
    expect(source).toContain("countryRows.map");
    expect(source).toContain("consenting member");
    expect(source).not.toContain("No consented aggregate coverage for this selection.");
    expect(source).not.toContain("individual location");
  });
});
