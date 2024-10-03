import csv
from pathlib import Path
from atwiki import AtWikiAPI, AtWikiURI

OUTPUT_DIR = Path("dump")
TSV_FILE = OUTPUT_DIR / 'page_names.tsv'

api = AtWikiAPI(
    AtWikiURI('https://w.atwiki.jp/hmiku/'),
    sleep=0
)

# Read existing page IDs from the TSV file if it exists
existing_page_names = {}
if TSV_FILE.exists():
    with open(TSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            existing_page_names[row['id']] = row['name']
import math
max_page_id = max(map(int, existing_page_names.keys()))
start_from = math.floor(max_page_id / 100)
print(max_page_id)

# Open the TSV file in append mode to add new entries
with open(TSV_FILE, 'a', encoding='utf-8') as f:
    # If file is newly created, write the header
    if not existing_page_names:
        f.write("id\tname\n")

    for page in api.get_list(_start=start_from):
        page_id = page['id']
        page_name = page['name']

        # Skip already existing IDs
        if str(page_id) not in existing_page_names:
            existing_page_names[page_id] = page_name
            f.write(f"{page_id}\t{page_name}\n")
            print(f"Added {page_id}: {page_name}")
        else:
            print(f"Skipped {page_id}: {page_name} (already exists)")
