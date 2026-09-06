import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("active FastAPI runtime cutover", () => {
  const app = readFileSync(resolve(process.cwd(), "client/src/App.tsx"), "utf8");
  const main = readFileSync(resolve(process.cwd(), "client/src/main.tsx"), "utf8");
  const nodeHost = readFileSync(resolve(process.cwd(), "server/_core/index.ts"), "utf8");

  it("uses a NotFound fallback and React Query without an active tRPC provider", () => {
    expect(app).toContain("<Route component={NotFound} />");
    expect(app).not.toContain("<Route component={Home} />");
    expect(main).toContain("<QueryClientProvider client={queryClient}>");
    expect(main).not.toContain("trpc.Provider");
    expect(main).not.toContain("httpBatchLink");
    expect(nodeHost).toContain('app.use("/api/v1", proxyFastApi)');
    expect(nodeHost).not.toContain("createExpressMiddleware");
    expect(nodeHost).not.toContain('"/api/trpc"');
  });
});
