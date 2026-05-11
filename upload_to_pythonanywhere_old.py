import os
import sys
import requests


USER = "naomi"
REMOTE_PATH = "/home/naomi/latest.json"
API_URL = f"https://www.pythonanywhere.com/api/v0/user/{USER}/files/path{REMOTE_PATH}"

def main():
    token = os.environ.get("PYAW_TOKEN")
    if not token:
        print("PYAW_TOKEN is not set", file=sys.stderr)
        sys.exit(2)

    local_path = "latest.json"
    if not os.path.exists(local_path):
        print("latest.json not found", file=sys.stderr)
        sys.exit(2)

    headers = {"Authorization": f"Token {token}"}

    # Files API: POST multipart with field name "content"
    with open(local_path, "rb") as f:
        files = {"content": f}
        r = requests.post(API_URL, headers=headers, files=files, timeout=60)

    if r.status_code >= 400:
        print(f"Upload failed: {r.status_code} {r.text}", file=sys.stderr)
        sys.exit(1)

    print("uploaded latest.json")

if __name__ == "__main__":
    main()
