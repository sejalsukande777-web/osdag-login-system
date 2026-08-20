// Auth functions - these replace what I had to build by hand in the custom
// backend (hashing, JWT, revoked_tokens table). Appwrite's Account service
// does all of that internally, I just call these methods.

import { ID } from "appwrite";
import { account } from "./appwriteClient.js";

// registers a new user, then logs them in right away (register alone doesn't
// give you a session, so i just chain login after it)
export async function register(email, password, name) {
  await account.create(ID.unique(), email, password, name);
  return login(email, password);
}

// logs in and creates a session - appwrite handles this with its own
// cookie/token, i didn't have to write any jwt code for this side
export async function login(email, password) {
  return account.createEmailPasswordSession(email, password);
}

// logs out - deletes the session server side. this is basically the same
// idea as the revoked_tokens table i built by hand for the custom backend,
// except here it's one line since appwrite already tracks sessions itself
export async function logout() {
  return account.deleteSession("current");
}

// same as /me in my custom backend - returns whoever is currently logged in.
// no way to ask for someone else's id here either, same as before
export async function getMe() {
  return account.get();
}
