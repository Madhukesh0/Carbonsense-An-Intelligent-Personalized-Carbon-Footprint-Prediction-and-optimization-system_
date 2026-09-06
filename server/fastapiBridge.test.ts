import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("FastAPI development bridge", () => {
  const source = readFileSync(resolve(process.cwd(), "server/_core/index.ts"), "utf8");

  it("starts the MongoDB-backed FastAPI process and proxies versioned API calls same-origin", () => {
    expect(source).toContain('"backend.app.main:app"');
    expect(source).toContain('app.use("/api/v1", proxyFastApi)');
    expect(source).toContain("COOKIE_SECURE");
    expect(source).toContain("req.originalUrl");
    expect(source).toContain("serializedBody");
    expect(source).toContain("proxy.end(serializedBody)");
  });
});
