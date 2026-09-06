import { Collection, MongoClient, MongoServerError, ServerApiVersion } from "mongodb";
import { ENV } from "./_core/env";

let client: MongoClient | null = null;
let credentialIndexesReady = false;

export type MongoCredentialAccount = {
  email: string;
  passwordHash: string;
  openId: string;
  createdAt: Date;
  updatedAt: Date;
};

function getDatabaseName(uri: string) {
  try {
    const pathname = new URL(uri).pathname.replace(/^\//, "");
    return pathname.split("/")[0] || "carbonsense";
  } catch {
    return "carbonsense";
  }
}

export async function getMongoAuthDatabase() {
  if (!ENV.mongoDbUri) {
    throw new Error("MONGODB_URI is not configured.");
  }

  if (!client) {
    client = new MongoClient(ENV.mongoDbUri, {
      serverApi: { version: ServerApiVersion.v1, strict: true, deprecationErrors: true },
      maxPoolSize: 10,
      minPoolSize: 0,
      serverSelectionTimeoutMS: 8_000,
    });
  }

  await client.connect();
  return client.db(getDatabaseName(ENV.mongoDbUri));
}

/** Lightweight health check used only to validate the securely stored URI. */
export async function validateMongoConnection() {
  const db = await getMongoAuthDatabase();
  await db.command({ ping: 1 });
  return { connected: true as const, database: db.databaseName };
}

export async function getMongoCredentialAccounts(): Promise<Collection<MongoCredentialAccount>> {
  const collection = (await getMongoAuthDatabase()).collection<MongoCredentialAccount>("credential_accounts");
  if (!credentialIndexesReady) {
    await collection.createIndexes([
      { key: { email: 1 }, name: "credential_accounts_email_unique", unique: true },
      { key: { openId: 1 }, name: "credential_accounts_open_id_unique", unique: true },
    ]);
    credentialIndexesReady = true;
  }
  return collection;
}

export async function findMongoCredentialByEmail(email: string) {
  return (await getMongoCredentialAccounts()).findOne({ email });
}

export async function createMongoCredential(input: Omit<MongoCredentialAccount, "createdAt" | "updatedAt">) {
  const now = new Date();
  try {
    await (await getMongoCredentialAccounts()).insertOne({ ...input, createdAt: now, updatedAt: now });
  } catch (error) {
    if (error instanceof MongoServerError && error.code === 11000) {
      throw new Error("A native credential account already exists for this email.");
    }
    throw error;
  }
}

export async function removeMongoCredentialByOpenId(openId: string) {
  await (await getMongoCredentialAccounts()).deleteOne({ openId });
}
