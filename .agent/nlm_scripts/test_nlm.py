import os
import json
from notebooklm_tools.core.client import NotebookLMClient

profile_dir = r"C:\Users\muhar\.notebooklm-mcp-cli\profiles\default"
cookies_path = os.path.join(profile_dir, "cookies.json")

if not os.path.exists(cookies_path):
    print("Cookies file not found.")
    exit(1)

with open(cookies_path, "r", encoding="utf-8") as f:
    cookies = json.load(f)

client = NotebookLMClient(cookies=cookies)
try:
    notebooks = client.list_notebooks()
    print(f"Success! Found {len(notebooks)} notebooks.")
    for nb in notebooks:
        print(f"- {nb['title']} ({nb['id']})")
except Exception as e:
    print(f"Error: {e}")
