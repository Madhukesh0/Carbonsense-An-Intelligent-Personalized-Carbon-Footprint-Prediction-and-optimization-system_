import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const source = (relativePath: string) => readFileSync(resolve(process.cwd(), relativePath), "utf8");

describe("reorganized CarbonSense interface", () => {
  const app = source("client/src/App.tsx");
  const onboarding = source("client/src/components/onboarding/FirstUsePath.tsx");
  const adminDashboard = source("client/src/pages/admin/Dashboard.tsx");
  const adminUsers = source("client/src/pages/admin/Users.tsx");
  const insights = source("client/src/pages/Insights.tsx");
  const progress = source("client/src/pages/Progress.tsx");
  const reports = source("client/src/pages/Reports.tsx");

  it("adopts organized page modules for native authentication, core workspaces, and administration", () => {
    expect(app).toContain('import Login from "./pages/auth/Login"');
    expect(app).toContain('import Register from "./pages/auth/Register"');
    expect(app).toContain('import AdminDashboard from "./pages/admin/Dashboard"');
    expect(app).toContain('import AdminUsers from "./pages/admin/Users"');
    expect(app).toContain('import Predict from "./pages/Predict"');
    expect(app).toContain('import About from "./pages/About"');
    expect(app).toContain('<Route path="/admin" component={AdminDashboard} />');
    expect(app).toContain('<Route path="/admin/users" component={AdminUsers} />');
    expect(app).toContain('<Route path="/baseline" component={Baseline} />');
    expect(app).toContain('<Route path="/predict" component={Predict} />');
    expect(app).toContain('<Route path="/docs" component={About} />');
    expect(app).toContain('<Route path="/insights" component={Insights} />');
  });

  it("uses FastAPI account-scoped history as the only onboarding completion evidence", () => {
    expect(onboarding).toContain('useFastApiQuery<{ id: string }[]>(["insights", "history"], "/insights/history", isAuthenticated)');
    expect(onboarding).toContain("const hasEstimate = runs.length > 0");
    expect(onboarding).toContain("const hasFollowUp = runs.length > 1");
    expect(onboarding).toContain("Completion reflects saved estimate history only");
    expect(onboarding).not.toContain("trpc.history");
  });

  it("uses FastAPI aggregate-only administrator contracts in the real target dashboard", () => {
    expect(adminDashboard).toContain('"/admin/dashboard"');
    expect(adminDashboard).toContain('`/organization/contributors${filters.size');
    expect(adminDashboard).toContain('"/organization/summaries"');
    expect(adminDashboard).toContain("every figure uses opt-in aggregate records only");
    expect(adminDashboard).toContain("No private histories or individual identities are shown");
    expect(adminDashboard).not.toContain("trpc.");
  });

  it("keeps FastAPI super-admin role and activation controls in the target admin page", () => {
    expect(adminUsers).toContain('"/admin/users"');
    expect(adminUsers).toContain("fastApi.admin.updateRole");
    expect(adminUsers).toContain("fastApi.admin.updateActive");
    expect(adminUsers).toContain("Super-admin access is required");
    expect(adminUsers).not.toContain("trpc.");
  });

  it("keeps migrated personal data pages on authenticated FastAPI endpoints", () => {
    expect(insights).toContain('"/insights/history"');
    expect(progress).toContain('"/activity/quest-summary"');
    expect(reports).toContain('"/reports/mine"');
  });
});
