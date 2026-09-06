import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("RoleAssistantWidget FastAPI migration", () => {
  const source = readFileSync(resolve(process.cwd(), "client/src/components/RoleAssistantWidget.tsx"), "utf8");

  it("sends bounded assistant messages to the FastAPI account-scoped route", () => {
    expect(source).toContain('"/assistant/chat"');
    expect(source).not.toContain("trpc.assistant.chat");
  });
});
