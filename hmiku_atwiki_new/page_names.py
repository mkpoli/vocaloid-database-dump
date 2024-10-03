from pathlib import Path
from atwiki import AtWikiAPI, AtWikiURI

OUTPUT_DIR = Path("dump")

api = AtWikiAPI(
    AtWikiURI('https://w.atwiki.jp/hmiku/'),
)

page_names = {}

with open(OUTPUT_DIR / 'page_names.tsv', 'w') as f:
    f.write("id\tname\n")
    for page in api.get_list():
        page_id = page['id']
        page_name = page['name']

        page_names[page_id] = page_name
        f.write(f"{page_id}\t{page_name}\n")

        print(f"{page_id}: {page_name}")
