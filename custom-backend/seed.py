"""
Seeds the database with 3 test users, each with their own sample files.
Run with: python seed.py  (after setting up your .env and creating the database)
"""
from app.database import SessionLocal, Base, engine
from app.models import User, UserFile
from app.auth import hash_password

Base.metadata.create_all(bind=engine)

TEST_USERS = [
    {
        "email": "alice@example.com",
        "password": "AlicePassword123",
        "full_name": "Alice Anderson",
        "files": [
            {"filename": "alice_resume.txt", "content": "Alice's resume content goes here."},
            {"filename": "alice_notes.txt", "content": "Some private notes belonging to Alice."},
        ],
    },
    {
        "email": "bob@example.com",
        "password": "BobPassword123",
        "full_name": "Bob Baker",
        "files": [
            {"filename": "bob_report.txt", "content": "Bob's quarterly report draft."},
        ],
    },
    {
        "email": "carol@example.com",
        "password": "CarolPassword123",
        "full_name": "Carol Chen",
        "files": [
            {"filename": "carol_budget.txt", "content": "Carol's personal budget sheet."},
            {"filename": "carol_ideas.txt", "content": "Carol's project idea list."},
        ],
    },
]


def seed():
    db = SessionLocal()
    try:
        for entry in TEST_USERS:
            existing = db.query(User).filter(User.email == entry["email"]).first()
            if existing:
                print(f"Skipping {entry['email']} — already exists.")
                continue

            user = User(
                email=entry["email"],
                hashed_password=hash_password(entry["password"]),
                full_name=entry["full_name"],
            )
            db.add(user)
            db.flush()  # get user.id before commit

            for f in entry["files"]:
                db.add(UserFile(owner_id=user.id, filename=f["filename"], content=f["content"]))

            db.commit()
            print(f"Created {entry['email']} (password: {entry['password']}) with {len(entry['files'])} file(s).")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
    print("\nSeeding complete. Use the emails/passwords above to test login and per-user isolation.")
