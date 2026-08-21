# Osdag Login System — Custom Backend (FastAPI + PostgreSQL)

This is my custom backend implementation for the login system task. Built with FastAPI and PostgreSQL.

## Setup

1. Install PostgreSQL and create a database:
   ```bash
   createdb osdag_login
   ```

2. Install dependencies:
   ```bash
   cd custom-backend
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and fill it in:
   ```bash
   cp .env.example .env
   ```
   Set `JWT_SECRET_KEY` to something random, and make sure `DATABASE_URL` matches your local Postgres.

4. Seed 3 test users:
   ```bash
   python seed.py
   ```
   This prints out each seeded user's email/password so you can log in and test.

5. Run it:
   ```bash
   uvicorn app.main:app --reload
   ```
   Docs at `http://localhost:8000/docs`.

## Endpoints

| Method | Path | Needs auth? | What it does |
|---|---|---|---|
| POST | `/auth/register` | No | Register |
| POST | `/auth/login` | No | Log in, get a JWT back |
| POST | `/auth/logout` | Yes | Invalidates the current token |
| GET | `/me` | Yes | Your own profile |
| GET | `/files` | Yes | Your own files only |
| GET | `/files/{file_id}` | Yes | One file, only if it's yours |

Protected routes need `Authorization: Bearer <token>`.

## Why I made the choices I made

### JWT or sessions?
I went with JWT instead of server-side sessions mainly because it's simpler to set up for something this size — I didn't want to add a whole session store just for this. The downside is a JWT is normally valid until it expires no matter what, even if you "log out" — so I had to handle that separately (see below). If this were a bigger system with multiple services I'd probably lean towards sessions since revoking access centrally would matter more, but for one API I think JWT was the right call here.

### How logout actually works
This one took me a bit to figure out. A plain JWT doesn't care if you "logged out" — it's just a piece of data that's valid until its expiry, so if you don't do anything extra, someone could technically keep using an old token after "logging out" on the frontend. To fix that, every token I hand out has a random `jti` in it. When someone logs out, I save that `jti` into a `revoked_tokens` table. Then every protected route checks the incoming token's `jti` against that table before trusting it. So logout actually kills the session on the server, not just clears it from the browser.

### How I'm keeping users' data separate
The main thing I did here was make sure nothing ever trusts an ID coming from the request — the user's identity always comes from the JWT itself, never from the URL or body. So `/me` just returns whoever the token says you are, no way to ask for someone else. `/files` filters by `owner_id` right in the SQL query. For `/files/{file_id}`, I check two things — does the file exist, and does it belong to you — and return the exact same 404 either way. I thought about using 403 for "this file exists but isn't yours," but that would basically confirm to someone that a given file_id is real, just not theirs, which leaks info about other accounts. Same 404 for both cases avoids that.

### Appwrite comparison
Check `appwrite-backend/README.md` — I'll fill in the "what Appwrite did for me vs what I built myself" comparison there once that half is done.

### If I had more time
- Refresh tokens, so access tokens could expire faster without people getting logged out constantly
- A cleanup job for the revoked_tokens table (right now old rows just sit there forever)
- Actual file uploads instead of seeded text — the task said seeded files were fine so I kept it simple
- Rate limiting by IP too, not just per-account, so someone can't brute-force across a bunch of different accounts
- Logging failed logins somewhere so it could actually be reviewed later

## Testing with the seeded users

After `python seed.py`, you can log in as:
- `alice@example.com` / `AlicePassword123`
- `bob@example.com` / `BobPassword123`
- `carol@example.com` / `CarolPassword123`

I tested this myself by logging in as two different users and trying to fetch one user's file using the other user's token — confirmed it gets rejected with a 404, and confirmed a token stops working right after logout.
