"""
Seeds 3 test users + their files directly through Appwrite's server SDK,
instead of creating them by hand in the console like I did the first time
around. This is the Appwrite equivalent of custom-backend/seed.py.

Needs an API key with 'users.write' and 'databases.write' scopes - create
one under your Appwrite project's Settings > API Keys, then put it in .env.

Run with: python seed.py
"""
import os
from dotenv import load_dotenv
from appwrite.client import Client
from appwrite.services.users import Users
from appwrite.services.tables_db import TablesDB
from appwrite.id import ID
from appwrite.permission import Permission
from appwrite.role import Role
from appwrite.query import Query
from appwrite.exception import AppwriteException

load_dotenv()

client = Client()
client.set_endpoint(os.getenv("APPWRITE_ENDPOINT", "https://sgp.cloud.appwrite.io/v1"))
client.set_project(os.getenv("APPWRITE_PROJECT_ID"))
client.set_key(os.getenv("APPWRITE_API_KEY"))

users = Users(client)
databases = TablesDB(client)

DATABASE_ID = "osdag-database"
FILES_TABLE_ID = "files"

TEST_USERS = [
    {
        "email": "himanshu@example.com",
        "password": "HimanshuTest123",
        "name": "Himanshu Gupta",
        "files": [{"filename": "himanshu_notes.txt", "content": "Himanshu's private notes."}],
    },
    {
        "email": "sejal@example.com",
        "password": "SejalTest123",
        "name": "Sejal Sukande",
        "files": [{"filename": "sejal_report.txt", "content": "Sejal's quarterly report draft."}],
    },
    {
        "email": "aryan@example.com",
        "password": "AryanTest123",
        "name": "Aryan Tambe",
        "files": [{"filename": "aryan_ideas.txt", "content": "Aryan's project idea list."}],
    },
]


def seed():
    for entry in TEST_USERS:
        # create the user, skip if it already exists (re-running this script
        # shouldn't blow up if you've already seeded once)
        try:
            user = users.create(
                user_id=ID.unique(),
                email=entry["email"],
                password=entry["password"],
                name=entry["name"],
            )
            user_id = user.id
            print(f"Created user {entry['email']} (id: {user_id})")
        except AppwriteException as e:
            if "already exists" in str(e).lower():
                # look up the existing user's id instead of failing
                existing = users.list(queries=[Query.equal("email", [entry["email"]])])
                user_id = existing.users[0].id
                print(f"User {entry['email']} already exists (id: {user_id}), reusing it")
            else:
                raise

        # create their file rows, each locked to just this one user
        for f in entry["files"]:
            try:
                databases.create_row(
                    database_id=DATABASE_ID,
                    table_id=FILES_TABLE_ID,
                    row_id=ID.unique(),
                    data={
                        "owner_id": user_id,
                        "filename": f["filename"],
                        "content": f["content"],
                    },
                    permissions=[
                        Permission.read(Role.user(user_id)),
                        Permission.update(Role.user(user_id)),
                        Permission.delete(Role.user(user_id)),
                    ],
                )
                print(f"  -> created file {f['filename']}")
            except AppwriteException as e:
                print(f"  -> skipped file {f['filename']}: {e}")


if __name__ == "__main__":
    seed()
    print("\nSeeding complete.")


