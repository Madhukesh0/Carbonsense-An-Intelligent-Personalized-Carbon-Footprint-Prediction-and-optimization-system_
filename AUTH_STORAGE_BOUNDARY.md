# CarbonSense Account Storage Boundary

## Verified native email/password registration path

| Data category | Storage location | Verified behavior |
|---|---|---|
| Native credential record | MongoDB Atlas cluster, `carbonsense.credential_accounts` | Stores email, salted scrypt password hash, opaque native account ID, and timestamps. A unique index protects email and account ID. Plaintext passwords are not stored. |
| Profile and CarbonSense application data | Managed CarbonSense application database | Stores user profile and role fields, plus application records such as footprint runs, activity, goals, recommendations, reports, and governance history. Normal native registration does not write a native password hash here. |
| Browser after sign-in | Secure HTTP-only session cookie | The sign-in page holds typed values only in React memory while it is open. It does not persist credentials in browser local or session storage. The session cookie is HTTP-only, same-site none, and secure on HTTPS requests. |
| Google / Manus sign-in | Google and Manus authentication flow | Google authentication is handled by Google and Manus. CarbonSense receives an authenticated account identity and issues the application session; it does not receive the user's Google password. |

## Visual validation

Desktop checks of `/login` and `/register` confirmed a prominent **Create a CarbonSense account** action, the Google / Manus alternative-sign-in control, and an expandable storage-boundary panel. The panel is initially concise but provides explicit detail before a user registers or signs in.

Mobile checks at 390 px confirmed that the account-creation action, native credential form, Google / Manus control, and storage-boundary disclosure remain visible in a single vertical flow without horizontal overflow.
