import requests
import glob
import queue
import os
import time
import random

# Define headers to mimic a browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}

def dump_page(session, page_id):
    for attempt in range(5):
        try:
            resp = session.get(
                f'https://w.atwiki.jp/hmiku/pedit/{page_id}.html',
                headers=HEADERS,
                timeout=10
            )
            text = resp.text
            if resp.status_code == 404:
                os.makedirs('not_founds', exist_ok=True)
                with open(f"not_founds/{page_id}.html", "w", encoding='utf-8') as f:
                    f.write(text)
                print(f"{page_id}: Not found.")
                break
            if resp.status_code != 200:
                print(f"{page_id}: {resp.status_code}")
                time.sleep(5)
                continue
            if any(phrase in text for phrase in [
                "はこのWikiにログインしているメンバーか管理者に編集を許可しています。",
                "編集モード廃止に伴い",
                "は管理者からの編集のみ許可しています",
                "サポートしておりません。"
            ]):
                os.makedirs('no_permissions', exist_ok=True)
                print(f"{page_id}: No permission")
                with open(f"no_permissions/{page_id}.html", "w", encoding='utf-8') as f:
                    f.write(text)
                break
            if "でスパムと判断される内容が存在しています" in text:
                print(f"{page_id}: Spam detected")
                break
            if "<textarea" not in text:
                os.makedirs('no_source_pages', exist_ok=True)
                print(f"{page_id}: 200 but no source")
                with open(f"no_source_pages/{page_id}.html", "w", encoding='utf-8') as f:
                    f.write(text)
                break
            os.makedirs('pages', exist_ok=True)
            with open(f"pages/{page_id}.html", "w", encoding='utf-8') as f:
                f.write(text)
            print(f"{page_id}: Successfully saved.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"{page_id}: Attempt {attempt + 1} failed with error: {e}")
            # Exponential backoff with jitter
            delay = min(60, (2 ** attempt) + random.uniform(0, 1))
            print(f"Sleeping for {delay:.2f} seconds before retrying...")
            time.sleep(delay)
    print(f"{page_id}: Failed after retries")
    return False

def generate_queue():
    q = queue.Queue()
    pendings = set(range(3, 45387))
    pgs = set(int(os.path.splitext(os.path.basename(i))[0]) for i in glob.glob("pages/*.html"))
    nfs = set(int(os.path.splitext(os.path.basename(i))[0]) for i in glob.glob("not_founds/*.html"))
    nps = set(int(os.path.splitext(os.path.basename(i))[0]) for i in glob.glob("no_permissions/*.html"))
    print(f"Total: {len(pendings)}")
    print(f"Pages: {len(pgs)}")
    print(f"Not founds: {len(nfs)}")
    print(f"No permissions: {len(nps)}")
    pendings -= pgs | nfs | nps
    print(f"Pendings: {len(pendings)}")
    for i in sorted(pendings):
        q.put(i)
    return q

def worker_function(q: queue.Queue):
    session = requests.Session()
    while True:
        try:
            page_id = q.get(timeout=10)
        except queue.Empty:
            break
        print(f"Processing page {page_id}")
        success = dump_page(session, page_id)
        if not success:
            print(f"{page_id}: Re-queueing for retry")
            q.put(page_id)
            # Longer sleep after failure
            time.sleep(10)
        else:
            # Random sleep between requests
            delay = random.uniform(5, 10)
            print(f"Sleeping for {delay:.2f} seconds")
            time.sleep(delay)
        q.task_done()

if __name__ == '__main__':
    q = generate_queue()
    worker_function(q)
    q.join()
    print("Done.")
