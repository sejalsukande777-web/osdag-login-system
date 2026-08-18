# Osdag Login System — Screening Task

Two implementations of the same login/file-access system, as required by the task.

- **`custom-backend/`** — FastAPI + PostgreSQL. Done, tested it myself end to end.
- **`appwrite-backend/`** — Still working on this one.

Check each folder's README for setup steps and my reasoning on the design decisions.

## What's done so far (custom-backend)

- [x] Registration
- [x] Login (JWT)
- [x] Logout that actually invalidates the token server-side, not just on the client
- [x] `/me` returns only your own data
- [x] `/files` returns only your own files
- [x] `/files/:id` correctly blocks access to someone else's file (returns 404, same as a file that doesn't exist)
- [x] 3 seeded test users with their own files
- [x] Passwords hashed, never stored plain
- [x] Same generic error for wrong password / unknown email, so you can't tell which
- [x] Account locks after too many failed logins
- [x] All protected routes check the token the same way

Tested all of this against a real local Postgres db — logged in as two different users and confirmed one can't touch the other's files, and confirmed logout actually kills the token.

## appwrite-backend
Not started yet, that's next.
