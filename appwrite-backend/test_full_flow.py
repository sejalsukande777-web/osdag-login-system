"""
Full test of the Appwrite implementation - login, /me equivalent, list my files,
cross-user isolation, and logout.

Run with: python test_full_flow.py
"""
import requests
import json

ENDPOINT = "https://sgp.cloud.appwrite.io/v1"
PROJECT_ID = "6a85bdaf002e9a5e7cee"
DATABASE_ID = "osdag-database"
TABLE_ID = "files"

SEJAL_EMAIL = "sejal@example.com"
SEJAL_PASSWORD = "SejalTest123"

ARYAN_FILE_ROW_ID = "6a86088a002f8cf136d9"

session = requests.Session()
session.headers.update({
    "X-Appwrite-Project": PROJECT_ID,
    "Content-Type": "application/json",
})


def section(title):
    print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")


section("Step 1: Log in as Sejal")
login_resp = session.post(
    f"{ENDPOINT}/account/sessions/email",
    json={"email": SEJAL_EMAIL, "password": SEJAL_PASSWORD},
)
print("Status:", login_resp.status_code)
if login_resp.status_code >= 300:
    print("Login failed:", login_resp.text)
    exit()
sejal_user_id = login_resp.json()["userId"]
print(f"Logged in. Sejal's user ID: {sejal_user_id}")

section("Step 2: Get Sejal's own account info (equivalent to /me)")
me_resp = session.get(f"{ENDPOINT}/account")
print("Status:", me_resp.status_code)
print("Response:", json.dumps(me_resp.json(), indent=2))

section("Step 3: List Sejal's own files (query filtered by owner_id)")
query_string = json.dumps({"method": "equal", "attribute": "owner_id", "values": [sejal_user_id]})
list_resp = session.get(
    f"{ENDPOINT}/databases/{DATABASE_ID}/collections/{TABLE_ID}/documents",
    params={"queries[]": query_string},
)
print("Status:", list_resp.status_code)
print("Response:", json.dumps(list_resp.json(), indent=2))
if list_resp.status_code == 200:
    total = list_resp.json().get("total", 0)
    docs = list_resp.json().get("documents", [])
    print(f"\nSejal sees {total} file(s), all with owner_id == her own ID: {all(d.get('owner_id') == sejal_user_id for d in docs)}")

section("Step 4: Sejal tries to fetch Aryan's file directly (should fail)")
file_resp = session.get(
    f"{ENDPOINT}/databases/{DATABASE_ID}/collections/{TABLE_ID}/documents/{ARYAN_FILE_ROW_ID}",
)
print("Status:", file_resp.status_code)
if file_resp.status_code in (401, 403, 404):
    print("PASS: blocked correctly.")
else:
    print("FAIL: Sejal could access Aryan's file!")
    print(file_resp.text)

section("Step 5: Logout (delete current session)")
logout_resp = session.delete(f"{ENDPOINT}/account/sessions/current")
print("Status:", logout_resp.status_code)
print("Response:", logout_resp.text if logout_resp.text else "(empty - success)")

section("Step 6: Try /account again with the same session (should now fail)")
me_after_logout = session.get(f"{ENDPOINT}/account")
print("Status:", me_after_logout.status_code)
if me_after_logout.status_code in (401, 403):
    print("PASS: session correctly invalidated after logout.")
else:
    print("FAIL: session still works after logout!")
    print(me_after_logout.text)

section("ALL TESTS COMPLETE")
