
import { Client, Account, Databases, Query } from "appwrite";

const client = new Client()
  .setEndpoint("https://sgp.cloud.appwrite.io/v1")   // your Appwrite API endpoint
  .setProject("6a85bdaf002e9a5e7cee");                // your Appwrite project ID

export const account = new Account(client);
export const databases = new Databases(client);
export { Query };

// these two just save me from retyping the same strings everywhere
export const DATABASE_ID = "osdag-database";
export const FILES_TABLE_ID = "files";
