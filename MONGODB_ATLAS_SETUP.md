# CarbonSense MongoDB Atlas Setup

This guide creates a **free MongoDB Atlas deployment** for the CarbonSense GitHub-style native login. It keeps the existing application data and Manus OAuth in place while preparing MongoDB to store native credential records.

> Do not paste your MongoDB password or full connection string into normal chat messages. The connection string will be entered through the secure project-secret form after setup.

## 1. Sign in and create a project

1. Open [MongoDB Atlas](https://cloud.mongodb.com/) and sign in to your existing account.
2. Select **New Project**.
3. Name it **CarbonSense** and create the project.

## 2. Create a free deployment

1. In the new project, choose **Create** or **Build a Database**.
2. Select the **Free** option, sometimes labelled **M0**.
3. Choose a cloud provider and a region close to you or your likely users.
4. Keep the default cluster name or rename it to **CarbonSenseCluster**.
5. Click **Create Deployment** and wait until its status is ready.

Free Atlas deployments are intended for small-scale development and one free deployment is allowed per Atlas project. [1]

## 3. Create the application database user

1. In the left navigation, open **Database & Network Access**, then the **Database Users** tab.
2. Select **Add New Database User** and choose **Password** authentication.
3. Use a username such as `carbonsense_app`.
4. Use **Autogenerate Secure Password**, save it in a password manager, and do not share it in chat.
5. Under privileges, choose **Read and write to any database** for the first integration test. Once the connection is working, we will narrow it to **readWrite** access for only the `carbonsense` database.
6. Save the user.

Atlas database users are separate from your Atlas website account, and their permissions are controlled by database roles. [2]

## 4. Configure network access

1. Open **Database & Network Access**, then **Network Access**.
2. Click **Add IP Address**.
3. For testing from your own computer, choose **Add My Current IP Address**.
4. For the Manus-hosted CarbonSense server, we may need the temporary entry `0.0.0.0/0`, because its outbound IP address is not guaranteed to be fixed. If you use this setting, keep the application user restricted to the `carbonsense` database and retain the generated password only in the secure secret store.
5. Save the access-list entry.

Atlas requires both an allowed network address and a database user before an application can connect. [3]

## 5. Copy the application connection string

1. Return to **Database** or **Clusters**.
2. On `CarbonSenseCluster`, select **Connect**.
3. Choose **Drivers** and select **Node.js**.
4. Copy the `mongodb+srv://...` URI template.
5. Replace the placeholders with the database-user username and password, and set the database name to `carbonsense`.

The final value should follow this pattern:

```text
mongodb+srv://carbonsense_app:<YOUR_PASSWORD>@<YOUR_CLUSTER_HOST>/carbonsense?retryWrites=true&w=majority&appName=CarbonSense
```

If you typed a password that contains special characters such as `@`, `:`, `/`, or `#`, it must be URL-encoded in the URI. Using Atlas’s generated password avoids this common mistake.

## 6. Give the URI to CarbonSense securely

When you have the complete URI, reply **“MongoDB URI ready.”** I will open the secure `MONGODB_URI` field in the CarbonSense project. Enter the complete URI there, not in ordinary chat. Then I will test the connection and move the GitHub-style native login lookup to MongoDB.

## 7. Important: Replace the temporary Atlas Admin user

Atlas automatically created an **Atlas Admin** database user during initial connection setup. CarbonSense has now used that account only to verify the new database connection. Do not retain it as the long-term application credential.

1. Open **Database & Network Access** → **Database Users** → **Add New Database User**.
2. Create `carbonsense_app` with a generated strong password.
3. Assign the `readWrite` role for the `carbonsense` database only. Do not assign `Atlas Admin`.
4. Build a new Drivers connection URI using this new database user and securely update `MONGODB_URI` in CarbonSense.
5. After the updated connection succeeds, delete the temporary Atlas Admin database user if no other approved application needs it.

This follows the principle of least privilege: the running application can create and read its own `credential_accounts` collection but cannot administer the Atlas project or unrelated databases.

## Current CarbonSense integration status

The GitHub-style native registration and login flow now stores only **salted scrypt password hashes**, normalized emails, and the existing CarbonSense `openId` link in the MongoDB `carbonsense.credential_accounts` collection. The existing managed database remains the source for roles, private activity history, organization isolation, and Manus OAuth user records. Existing native credentials in the managed database are copied to MongoDB on their next successful login, allowing a gradual migration without forcing users to reset passwords.

## References

[1] [MongoDB Atlas — Deploy a Free Cluster](https://www.mongodb.com/docs/atlas/tutorial/deploy-free-tier-cluster/)

[2] [MongoDB Atlas — Configure Database Users](https://www.mongodb.com/docs/atlas/security-add-mongodb-users/)

[3] [MongoDB Atlas — Connect to a Database Deployment](https://www.mongodb.com/docs/atlas/connect-to-database-deployment/)
