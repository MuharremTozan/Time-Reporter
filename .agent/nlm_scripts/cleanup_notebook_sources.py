import os
import sys
import json
from notebooklm_tools.core.client import NotebookLMClient
from notebooklm_tools.core.auth import load_cached_tokens

def cleanup_notebook():
    notebook_id = "d2e6f23f-33e0-4311-8f22-17c5b1848813"
    
    # Files to be removed based on their titles in the notebook
    titles_to_remove = [
        "25-31Ocak",
        "3Subat",
        "4Subat",
        "5Subat",
        "6Subat",
        "7Subat"
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
        print(f"Fetching sources for notebook: {notebook_id}...")
        sources = client.get_notebook_sources_with_types(notebook_id)
        
        removed_count = 0
        for source in sources:
            if source['title'] in titles_to_remove:
                print(f"Deleting source: {source['title']} (ID: {source['id']})...")
                try:
                    # Correcting the call: delete_source only takes source_id, not notebook_id
                    client.delete_source(source['id'])
                    print(f"Successfully deleted: {source['title']}")
                    removed_count += 1
                except Exception as e:
                    print(f"Error deleting {source['title']}: {e}")
        
        print(f"\nCleanup complete. Total sources removed: {removed_count}")

if __name__ == "__main__":
    cleanup_notebook()
