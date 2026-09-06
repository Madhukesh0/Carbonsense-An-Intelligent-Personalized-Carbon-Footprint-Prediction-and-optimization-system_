import { MongoClient } from "mongodb";
import mysql from "mysql2/promise";

const mongoUri = process.env.MONGODB_URI;
const databaseUrl = process.env.DATABASE_URL;
if (!mongoUri || !databaseUrl) throw new Error("MONGODB_URI and DATABASE_URL are required.");

const mysqlUrl = new URL(databaseUrl);
const connection = await mysql.createConnection(databaseUrl);
const [rows] = await connection.execute("SELECT id, openId FROM users WHERE email LIKE 'mongo-auth-%@example.test'");
const openIds = rows.map((row) => row.openId);
if (rows.length) {
  const ids = rows.map((row) => row.id);
  const placeholders = ids.map(() => "?").join(",");
  await connection.execute(`DELETE FROM credential_accounts WHERE userId IN (${placeholders})`, ids);
  await connection.execute(`DELETE FROM users WHERE id IN (${placeholders})`, ids);
}
await connection.end();

const client = new MongoClient(mongoUri, { serverSelectionTimeoutMS: 10_000 });
await client.connect();
const collection = client.db().collection("credential_accounts");
const result = await collection.deleteMany({ $or: [{ email: { $regex: "^mongo-auth-.*@example\\.test$" } }, ...(openIds.length ? [{ openId: { $in: openIds } }] : [])] });
await client.close();
console.log(`Removed ${rows.length} temporary SQL user(s) and ${result.deletedCount} temporary MongoDB credential(s).`);
