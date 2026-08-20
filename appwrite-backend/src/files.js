// File access functions. The isolation here works differently than the
// custom backend - instead of me writing "WHERE owner_id = current_user.id"
// in a SQL query, Appwrite enforces it at the database level using row
// permissions (set when each row was created/seeded). The owner_id filter
// below is still useful for listing "my files" efficiently, but even without
// it, Appwrite would refuse to hand back another user's row if I tried.

import { databases, DATABASE_ID, FILES_TABLE_ID, Query } from "./appwriteClient.js";
import { getMe } from "./auth.js";

// gets only the logged-in user's files. filtering by owner_id here so i'm
// not fetching stuff i don't need, but the actual security comes from
// appwrite's row permissions, not this filter - this is just for convenience
export async function listMyFiles() {
  const me = await getMe();
  return databases.listDocuments(DATABASE_ID, FILES_TABLE_ID, [
    Query.equal("owner_id", me.$id),
  ]);
}

// gets one file by id. if it's not mine, appwrite just throws a 404 on its
// own because of the row permissions - i didn't have to write an ownership
// check here like i did in file_routes.py for the custom backend. this is
// honestly the biggest difference between the two versions
export async function getFile(fileId) {
  return databases.getDocument(DATABASE_ID, FILES_TABLE_ID, fileId);
}
