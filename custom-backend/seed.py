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
        "email": "himanshu@example.com",
        "password": "HimanshuPassword123",
        "full_name": "Himanshu Gupta",
        "files": [
            {"filename": "himanshu_resume.txt", "content": "Himanshu's resume content goes here."},
            {"filename": "himanshu_notes.txt", "content": "Some private notes belonging to Himanshu."},
        ],
    },
    {
        "email": "sejal@example.com",
        "password": "SejalPassword123",
        "full_name": "Sejal sukande",
        "files": [
            {"filename": "sejal_report.txt", "content": "Sejal's quarterly report draft."},
        ],
    },
    {
        "email": "aryan@example.com",
        "password": "aryanPassword123",
        "full_name": "aryan tambe",
        "files": [
            {"filename": "aryan_budget.txt", "content": "Aryan's personal budget sheet."},
            {"filename": "aryan_ideas.txt", "content": "Aryan's project idea list."},
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
