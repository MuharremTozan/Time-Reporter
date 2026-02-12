import os
import json
import time
import sys
from notebooklm_tools.core.client import NotebookLMClient

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Auth
profile_dir = r"C:\Users\muhar\.notebooklm-mcp-cli\profiles\default"
cookies_path = os.path.join(profile_dir, "cookies.json")

with open(cookies_path, "r", encoding="utf-8") as f:
    cookies = json.load(f)

client = NotebookLMClient(cookies=cookies)

source_nb_id = "5ea52422-527a-43a0-be42-0e80e1f7898a"  # TASLAK - Gezgin
target_nb_id = "5d859cad-8c28-42c0-ad74-211c3216e0bb"  # ESKI HIKAYELER

print(f"Fetching sources from {source_nb_id}...")
sources = client.get_notebook_sources_with_types(source_nb_id)

copied_count = 0
for src in sources:
    src_id = src['id']
    src_title = src['title']
    print(f"Processing {src_title} ({src_id})...")
    
    try:
        # Get content (returns dict: {'content': ..., 'title': ...})
        source_data = client.get_source_fulltext(src_id)
        raw_text = source_data.get('content', '')
        
        if not raw_text:
            print(f"Warning: No content found for {src_title}")
            continue
            
        print(f"Adding {src_title} to target notebook (Length: {len(raw_text)} chars)...")
        # Add to target
        result = client.add_text_source(target_nb_id, raw_text, title=src_title)
        
        if result and 'id' in result:
            print(f"Successfully copied: {src_title} (New ID: {result['id']})")
            copied_count += 1
        else:
            print(f"Failed to copy {src_title}: API returned {result}")
        
        # Small delay to avoid rate limiting
        time.sleep(1.5)
    except Exception as e:
        print(f"Error copying {src_title}: {e}")

print(f"\nFinished! Total copied: {copied_count}/{len(sources)}")

# Final verification
nb_list = client.list_notebooks()
for nb in nb_list:
    if nb['id'] == target_nb_id:
        print(f"Final source count for ESKI HIKAYELER: {nb.get('source_count', 'unknown')}")
