import { describe, expect, it } from "vitest";
import { getMongoCredentialAccounts, validateMongoConnection } from "./mongoAuth";

describe("MongoDB Atlas secret configuration", () => {
  it("connects using the securely configured MONGODB_URI without writing test data", async () => {
    await expect(validateMongoConnection()).resolves.toMatchObject({ connected: true, database: "carbonsense_fastapi" });
  }, 15_000);

  it("opens the dedicated native-credential collection without inserting test accounts", async () => {
    const collection = await getMongoCredentialAccounts();
    expect(collection.collectionName).toBe("credential_accounts");
  }, 15_000);
});
