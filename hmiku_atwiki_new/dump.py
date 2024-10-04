import time
import math
from pathlib import Path
from atwiki import AtWikiAPI, AtWikiURI
from urllib.error import HTTPError

REQUEST_INTERVAL = 8
MAX_RETRIES = 5
OUTPUT_DIR = Path("dump")
OUTPUT_DIR.mkdir(exist_ok=True)

api = AtWikiAPI(
    AtWikiURI('https://w.atwiki.jp/hmiku/'),
    sleep=REQUEST_INTERVAL
)

# known_404_pages = set()
# not_found_file = OUTPUT_DIR / '404_pages.txt'
# if not_found_file.exists():
#     with open(not_found_file, 'r') as f:
#         known_404_pages = {int(line.strip()) for line in f if line.strip().isdigit()}

max_page_id = max(int(file.stem) for file in OUTPUT_DIR.glob("*.wiki"))
start_from = math.floor(max_page_id / 100 + 1)


print("Fetching the list of pages...")
page_list = api.get_list(_start=start_from)

for page in page_list:
    page_id = page['id']
    page_name = page['name']
    filename = OUTPUT_DIR / f"{page_id}.wiki"

    # if page_id in known_404_pages:
    #     print(f"Page {page_id} is known to be 404. Skipping.")
    #     continue

    if filename.exists():
        print(f"Page {page_id} already downloaded. Skipping.")
        continue

    retries = 0

    while retries < MAX_RETRIES:
        try:
            source = api.get_source(page_id)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(source)
            print(f"Downloaded page {page_id}: {page_name}")
            break
        except HTTPError as e:
            # if e.code == 404:
                # with open(not_found_file, 'a') as f:
                #     f.write(f"{page_id}\n")
                # print(f"Page {page_id} not found (404).")
            # else:
            # print(f"Page {page_id} got HTTP Error ({e.code})")
            retries += 1
            # wait_time = REQUEST_INTERVAL * (2 ** (retries - 1))
            wait_time = 480
            print(f"Failed to download page {page_id} (attempt {retries}): {e}")
            print(f"Waiting {wait_time} seconds before retrying...")
            time.sleep(wait_time)
        except Exception as e:
            print("Unknown error", e)
            break
            
    else:
        print(f"Failed to download page {page_id} after {MAX_RETRIES} attempts. Skipping.")
