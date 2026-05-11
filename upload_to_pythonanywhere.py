from dotenv import load_dotenv
import os
import sys
import requests

load_dotenv()

USER = "stockhome"
REMOTE_PATH = f"/home/{USER}/latest.json"
API_URL = f"https://www.pythonanywhere.com/api/v0/user/{USER}/files/path{REMOTE_PATH}"

def main():
    token = os.environ.get("PYAW_TOKEN")

    print("=== DEBUG ===")
    print("TOKEN:", token)
    print("LEN:", len(token) if token else None)
    print("USER:", USER)
    print("URL:", API_URL)
    print("=============")

    if not token:
        print("PYAW_TOKEN is not set", file=sys.stderr)
        sys.exit(2)

    local_path = "latest.json"
    if not os.path.exists(local_path):
        print("latest.json not found", file=sys.stderr)
        sys.exit(2)

    headers = {"Authorization": f"Token {token}"}

    with open(local_path, "rb") as f:
        files = {"content": f}
        r = requests.post(API_URL, headers=headers, files=files, timeout=60)

    print("STATUS:", r.status_code)
    print("RESPONSE:", r.text)

    if r.status_code >= 400:
        sys.exit(1)

    print("uploaded latest.json")

if __name__ == "__main__":
    main()