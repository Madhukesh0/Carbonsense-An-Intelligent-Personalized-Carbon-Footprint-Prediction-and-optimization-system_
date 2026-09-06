import { Collection, MongoClient, ServerApiVersion } from "mongodb";
import { ENV } from "./_core/env";

export interface User {
  id: number;
  openId: string;
  name: string | null;
  email: string | null;
  loginMethod: string | null;
  role: "individual" | "org_admin" | "super_admin";
  organizationId: string | null;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
  lastSignedIn: Date;
}

type InsertUser = {
  openId: string;
  name?: string | null;
  email?: string | null;
  loginMethod?: string | null;
  lastSignedIn?: Date;
  role?: string;
};

let client: MongoClient | null = null;
let usersCollection: Collection | null = null;

function getDatabaseName(uri: string) {
  try {
    const pathname = new URL(uri).pathname.replace(/^\//, "");
    return pathname.split("/")[0] || "carbonsense";
  } catch {
    return "carbonsense";
  }
}

async function getUsersCollection(): Promise<Collection> {
  if (usersCollection) return usersCollection;

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
  const db = client.db(getDatabaseName(ENV.mongoDbUri));
  usersCollection = db.collection("users");

  await usersCollection.createIndex({ openId: 1 }, { unique: true });

  return usersCollection;
}

export async function upsertUser(user: InsertUser): Promise<void> {
  if (!user.openId) {
    throw new Error("User openId is required for upsert");
  }

  try {
    const collection = await getUsersCollection();
    const now = new Date();
    const updateFields: Record<string, unknown> = { updatedAt: now };

    if (user.name !== undefined) updateFields.name = user.name;
    if (user.email !== undefined) updateFields.email = user.email;
    if (user.loginMethod !== undefined) updateFields.loginMethod = user.loginMethod;
    if (user.lastSignedIn !== undefined) updateFields.lastSignedIn = user.lastSignedIn;
    if (user.role !== undefined) {
      updateFields.role = user.role;
    } else if (user.openId === ENV.ownerOpenId) {
      updateFields.role = "super_admin";
    }

    await collection.updateOne(
      { openId: user.openId },
      {
        $set: updateFields,
        $setOnInsert: {
          openId: user.openId,
          role: updateFields.role || "individual",
          isActive: true,
          createdAt: now,
        },
      },
      { upsert: true }
    );
  } catch (error) {
    console.error("[Database] Failed to upsert user:", error);
    throw error;
  }
}

export async function getUserByOpenId(openId: string): Promise<User | undefined> {
  try {
    const collection = await getUsersCollection();
    const doc = await collection.findOne({ openId });
    if (!doc) return undefined;

    return {
      id: 0,
      openId: doc.openId as string,
      name: (doc.name as string) ?? null,
      email: (doc.email as string) ?? null,
      loginMethod: (doc.loginMethod as string) ?? null,
      role: (doc.role as User["role"]) ?? "individual",
      organizationId: (doc.organizationId as string) ?? null,
      isActive: (doc.isActive as boolean) ?? true,
      createdAt: (doc.createdAt as Date) ?? new Date(),
      updatedAt: (doc.updatedAt as Date) ?? new Date(),
      lastSignedIn: (doc.lastSignedIn as Date) ?? new Date(),
    };
  } catch (error) {
    console.error("[Database] Failed to get user:", error);
    return undefined;
  }
}
