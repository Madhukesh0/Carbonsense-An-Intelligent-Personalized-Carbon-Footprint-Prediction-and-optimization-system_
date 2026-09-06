import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it, vi } from "vitest";

const mockState = vi.hoisted(() => ({
  health: { data: undefined as any, isError: false, isLoading: false },
}));

vi.mock("@/_core/hooks/useAuth", () => ({
  useAuth: () => ({ user: { name: "Test member", country: "India" }, isAuthenticated: true }),
}));
vi.mock("@/hooks/useFastApi", () => ({
  useFastApiQuery: (_key: unknown, path: string) => {
    if (path === "/health") return mockState.health;
    if (path === "/model/info") return { data: { targetDefinition: "formula-derived synthetic monthly kgCO2e estimate", modelVersion: "xgb-final-54f-v2" }, isError: false, isLoading: false };
    return { data: [], isError: false, isLoading: false };
  },
  useFastApiMutation: () => ({ mutate: () => undefined, isPending: false }),
}));
vi.mock("@/components/RepoShell", () => ({ default: ({ children }: { children: unknown }) => createElement("div", null, children) }));
vi.mock("@/components/RepoAuthPage", () => ({ default: () => createElement("div", null, "auth") }));

import RepoReportCenter from "./RepoReportCenter";

describe("RepoReportCenter service-health rendering", () => {
  beforeEach(() => {
    mockState.health = { data: undefined, isError: false, isLoading: false };
  });

  it("renders live health and model-boundary metadata when the health query succeeds", () => {
    mockState.health = { data: { status: "ok", database: "mongodb" }, isError: false, isLoading: false };
    const html = renderToStaticMarkup(createElement(RepoReportCenter));
    expect(html).toContain("CarbonSense service ready");
    expect(html).toContain("FastAPI reports a MongoDB connection");
    expect(html).toContain("xgb-final-54f-v2");
    expect(html).toContain("not a direct emissions measurement");
  });

  it("renders an explicit unavailable state when the health query fails", () => {
    mockState.health = { data: undefined, isError: true, isLoading: false };
    const html = renderToStaticMarkup(createElement(RepoReportCenter));
    expect(html).toContain("Service status unavailable");
    expect(html).toContain("The service-health check could not be completed");
  });
});
