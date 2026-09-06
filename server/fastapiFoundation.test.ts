import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const project = process.cwd();
const read = (relative: string) => readFileSync(resolve(project, relative), "utf8");

describe("FastAPI migration foundation", () => {
  it("defines a FastAPI lifespan with MongoDB initialization and versioned routers", () => {
    const source = read("backend/app/main.py");
    expect(source).toContain("await connect_mongo()");
    expect(source).toContain('prefix="/api/v1"');
    expect(source).toContain("app.include_router(auth.router");
    expect(source).toContain("app.include_router(health.router");
  });

  it("uses secure JWT session cookies, CSRF validation, Argon2, and role dependencies", () => {
    const source = read("backend/app/core/security.py");
    const auth = read("backend/app/routers/auth.py");
    expect(source).toContain("PasswordHasher()");
    expect(source).toContain("HS256");
    expect(source).toContain("require_csrf");
    expect(auth).toContain("httponly=True");
    expect(source).toContain("ROLE_VALUES");
  });

  it("creates MongoDB indexes for ownership, sessions, consent-safe application records, and audits", () => {
    const source = read("backend/app/db/mongo.py");
    expect(source).toContain('database.users.create_index("email", unique=True)');
    expect(source).toContain("database.sessions.create_index");
    expect(source).toContain("database.footprint_runs.create_index");
    expect(source).toContain("database.governance_audit_logs.create_index");
  });
});
