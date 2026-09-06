# GitHub Repository Authentication Reference

**Reference reviewed:** CarbonSense GitHub frontend login, registration, password-recovery, protected-route, and authentication API components.

## User-facing patterns reproduced

| Repository pattern | CarbonSense implementation |
|---|---|
| `/login` card with email, password, recovery link, and registration entry | Repository-style `/login` screen with native email/password sign-in and a secure Manus sign-in alternative |
| `/register` with individual/organization selection, profile fields, and country | Repository-style `/register` screen with individual/organization selection, name, email, password, country, and explicit approval boundary |
| `/forgot-password` recovery screen | Recovery page explains supported secure options rather than using knowledge-based security questions |
| Public authentication routes and protected workspace routes | Public `/login`, `/register`, and `/forgot-password` routes with existing protected workspace procedures retained |
| JWT-backed authenticated application state | The existing signed session cookie is reused after native login so tRPC role guards and user isolation remain unchanged |

## Security decisions

The reference repository contains offline demo accounts, password-like test credentials, and account-recovery security questions. CarbonSense deliberately does **not** reproduce those parts. Native passwords are stored as salted, versioned scrypt hashes. The UI offers Manus OAuth as a secure alternative. Organization selection does not grant organization roles automatically; administrator approval remains necessary.

## Visual verification

On 19 August 2026, anonymous-session browser captures confirmed the login and registration pages render with the reconstructed brand shell, centered authentication cards, responsive controls, recovery link, account-type selector, secure Manus option, and administrator-approval disclosure.
