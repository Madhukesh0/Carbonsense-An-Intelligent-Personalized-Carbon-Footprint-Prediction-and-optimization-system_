import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("Assistant FastAPI page", () => {
  const source = readFileSync(resolve(process.cwd(), "client/src/pages/Assistant.tsx"), "utf8");
  const appSource = readFileSync(resolve(process.cwd(), "client/src/App.tsx"), "utf8");

  it("keeps assistant responses authenticated, private, and evidence-bounded", () => {
    expect(source).toContain('useFastApiMutation<AssistantReply, { message: string }>("/assistant/chat")');
    expect(source).toContain('return <RepoAuthPage mode="login" />');
    expect(source).toContain("do not claim a verified emissions reduction");
    expect(appSource).toContain('path="/assistant" component={Assistant}');
  });
});
