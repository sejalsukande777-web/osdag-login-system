// Sets up the Appwrite client that every other file here uses.
// Fill in your own values below, or better - load them from environment
// variables if you're bundling this with something like Vite (import.meta.env)
// or Webpack (process.env). Keeping it simple here since this is meant to be
// dropped straight into the provided testing client (index.html).

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
