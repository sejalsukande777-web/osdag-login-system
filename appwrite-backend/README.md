# Osdag Login System — Appwrite Backend

This is the second implementation of the login system task, using Appwrite instead of my own FastAPI code.

## Setup

1. Create an Appwrite Cloud account at cloud.appwrite.io, create a new project.
2. Under Auth, enable Email/Password sign-in (on by default).
3. Under Databases, create a database and a `files` table with these columns:
   - `owner_id` (string, required)
   - `filename` (string, required)
   - `content` (string, optional)
4. Turn on **Row security** in the table's Settings, and add a table-level permission: role "All users" (any logged-in user), Create only.
5. Copy `.env.example` to `.env`, fill in your endpoint, project ID, and an API key (Settings > API Keys, scopes `users.write` and `databases.write`).
6. Install the Python deps for the seed script: `pip install -r requirements.txt`
7. Run `python seed.py` to create 3 test users and their files.
8. For the client-side code: `npm install`, then use the functions in `src/auth.js` and `src/files.js` (built for the provided testing client, but works in any JS project using the Appwrite Web SDK).

## What Appwrite handled automatically vs. what I configured myself

This is the part I actually learned the most from, since I built both versions myself and could directly compare.

**Appwrite handled automatically:**
- Password hashing — I never touch a raw password or write any hashing code, Appwrite's Account service does it internally.
- Session management — `login()` just calls `account.createEmailPasswordSession()` and Appwrite manages the whole session lifecycle. I don't generate any tokens myself.
- Real logout — In my custom backend I had to build a whole `revoked_tokens` table and check it on every request just to make logout actually kill a JWT. In Appwrite, `account.deleteSession("current")` just works — I tested it and confirmed the same session is immediately rejected (401) on the next request, with zero extra code from me.
- Ownership enforcement on individual files — in my custom backend, `/files/{file_id}` has to manually check `if file.owner_id != current_user.id` and return a 404. In Appwrite, I don't write that check at all — the database itself refuses to return someone else's row because of the row-level permissions set when it was created. I actually tested this live: logged in as one user and tried to fetch another user's file by ID directly, and Appwrite returned a 404 on its own, no code from me involved in that decision.
- Account lockout / rate limiting on login — Appwrite has built-in abuse protection on auth endpoints, so I didn't have to build the failed-attempt counter and lockout logic I wrote by hand in the custom backend.

**What I configured myself:**
- The `files` table schema (which columns exist, which are required).
- Row Security being turned on for the table (it's off by default — if I hadn't enabled it, row-level permissions wouldn't have been enforced at all).
- The specific permission on each file row — when I create a file (in `seed.py` or through the console), I have to explicitly say "only this one user can read/update/delete this row." Appwrite doesn't guess this from the `owner_id` column, it only cares about the actual permissions attached to the row. I actually got this wrong on my first attempt in the console — I picked "All users" instead of a specific single user for a row's permissions and had to catch that mistake before it caused a real isolation bug.
- The table-level "Create" permission so any logged-in user is allowed to make new file rows (this is separate from row-level permissions, which control who can read/update/delete a row after it exists).
- The `owner_id` filter in `listMyFiles()` — Appwrite doesn't automatically give you "just my rows," I still had to write a query filtering by the current user's ID for that endpoint to make sense.

## If I had more time
- Add file upload to Appwrite Storage instead of storing content as plain text in the database.
- Add proper error handling / user-facing messages in the JS functions (right now errors just bubble up from the SDK as-is).
- Write actual integration tests instead of the one-off Python scripts I used to manually verify the flow.

## How I actually tested this

I didn't just trust the console UI — I wrote small Python scripts using `requests` to call the Appwrite REST API directly, logging in as one seeded user and trying to access another user's file. Confirmed:
- Login works and returns a valid session
- `GET /account` returns only the logged-in user's own profile
- Listing files with an `owner_id` filter returns only that user's files
- Directly requesting another user's file by ID returns a 404
- Logging out and then reusing the same session returns 401

All of this was tested against the real Appwrite Cloud project, not a local mock.
