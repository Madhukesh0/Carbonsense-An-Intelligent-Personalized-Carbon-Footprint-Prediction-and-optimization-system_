import { describe, expect, it } from "vitest";
import { hashPassword, verifyPassword } from "./passwordAuth";

describe("native credential password protection", () => {
  it("stores a salted versioned hash and verifies only the original password", async () => {
    const hash = await hashPassword("CorrectHorseBatteryStaple!2026");
    expect(hash).toMatch(/^scrypt\$[a-f0-9]{32}\$[a-f0-9]{128}$/);
    expect(hash).not.toContain("CorrectHorseBatteryStaple!2026");
    await expect(verifyPassword("CorrectHorseBatteryStaple!2026", hash)).resolves.toBe(true);
    await expect(verifyPassword("incorrect-password", hash)).resolves.toBe(false);
  });
});
