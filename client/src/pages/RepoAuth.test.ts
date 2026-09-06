import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

describe("repository-style authentication routes", () => {
  const authPage = readFileSync(resolve(process.cwd(), "client/src/pages/auth/AuthPage.tsx"), "utf8");
  const appRouter = readFileSync(resolve(process.cwd(), "client/src/App.tsx"), "utf8");
  const authRouter = readFileSync(resolve(process.cwd(), "backend/app/routers/auth.py"), "utf8");
  const security = readFileSync(resolve(process.cwd(), "backend/app/core/security.py"), "utf8");

  it("exposes reference-style login, registration, and recovery routes", () => {
    expect(appRouter).toContain('path="/login"');
    expect(appRouter).toContain('path="/register"');
    expect(appRouter).toContain('path="/forgot-password"');
    expect(authPage).toContain("Welcome back.");
    expect(authPage).toContain("Get started.");
    expect(authPage).toContain("Forgot password?");
  });

  it("uses native FastAPI credential endpoints instead of the retired provider flow", () => {
    expect(authPage).toContain("fastApi.auth.login");
    expect(authPage).toContain("fastApi.auth.register");
    expect(authPage).not.toContain("Continue securely with Google / Manus");
    expect(authRouter).toContain('"password_hash": hash_password(payload.password)');
    expect(authRouter).toContain("set_session_cookies");
  });

  it("makes account creation and the verified storage boundary visible without browser-stored credentials", () => {
    // AuthPage wraps this sentence across source lines; normalize whitespace.
    const normalizedAuthPage = authPage.replace(/\s+/g, " ");
    expect(normalizedAuthPage).toContain("Create a CarbonSense account");
    expect(normalizedAuthPage).toContain("MongoDB Atlas — native account credentials");
    expect(normalizedAuthPage).toContain("carbonsense_fastapi.users");
    expect(normalizedAuthPage).toContain("Argon2 password hash");
    expect(normalizedAuthPage).toContain("HTTP-only session cookie");
    expect(normalizedAuthPage).toContain("neither your password nor a long-lived session is stored in browser storage");
    expect(security).toContain("PasswordHasher");
    expect(security).toContain("session_hash(claims[\"sid\"])");
  });
});
