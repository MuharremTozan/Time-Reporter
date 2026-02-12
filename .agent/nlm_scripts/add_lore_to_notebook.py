import os
import sys
import json
from pathlib import Path
from notebooklm_tools.core.client import NotebookLMClient
from notebooklm_tools.core.auth import load_cached_tokens

def add_lore():
    notebook_id = "d2e6f23f-33e0-4311-8f22-17c5b1848813"
    base_dir = Path(r"c:/Storage/The Travels of Wanderer/World Building")
    
    files = [
        "Work_Log/Gunluk/3Subat.md",
        "Work_Log/Gunluk/4Subat.md",
        "Work_Log/Gunluk/5Subat.md",
        "Work_Log/Gunluk/6Subat.md",
        "Work_Log/Gunluk/7Subat.md",
        "Work_Log/Haftalik Ozet/25-31Ocak.md"
    ]

    tokens = load_cached_tokens()
    if not tokens:
        print("Error: No cached tokens found.")
        return

    with NotebookLMClient(
        cookies=tokens.cookies,
        csrf_token=tokens.csrf_token,
        session_id=tokens.session_id
    ) as client:
        for rel_path in files:
            file_path = base_dir / rel_path
            if not file_path.exists():
                print(f"Warning: File not found: {file_path}")
                continue
                
            title = file_path.stem.replace("_", " ")
            print(f"Adding source: {title}...")
            
            try:
                content = file_path.read_text(encoding="utf-8")
                if len(content.strip()) < 10:
                    print(f"Skipping empty/short file: {rel_path}")
                    continue
                    
                result = client.add_text_source(notebook_id, content, title=title, wait=True)
                if result:
                    print(f"Successfully added: {title} (ID: {result['id']})")
                else:
                    print(f"Failed to add: {title}")
            except Exception as e:
                print(f"Error adding {rel_path}: {e}")

if __name__ == "__main__":
    add_lore()
