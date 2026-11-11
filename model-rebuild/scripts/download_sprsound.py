"""Download SPRSound (CC BY 4.0) file by file from GitHub raw, resumable. Skips files already complete.

git clone stalled on this connection (11 Nov), so files are fetched one by one, 8 at a time,
into C:\\Users\\Hared\\Downloads\\sprsound (outside the project: never synced to Drive or git).
Run: python model-rebuild/scripts/download_sprsound.py   (re-run to resume)
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

TREE = os.path.join(r"C:\Users\Hared\Downloads\sprsound", "_tree.json")
DEST = r"C:\Users\Hared\Downloads\sprsound"
BASE = "https://raw.githubusercontent.com/SJTU-YONGFU-RESEARCH-GRP/SPRSound/main/"

if not os.path.exists(TREE):
    req = urllib.request.Request("https://api.github.com/repos/SJTU-YONGFU-RESEARCH-GRP/SPRSound/git/trees/main?recursive=1",
                                 headers={"User-Agent": "resondi-research"})
    json.dump(json.load(urllib.request.urlopen(req, timeout=120))["tree"], open(TREE, "w"))
tree = json.load(open(TREE, encoding="utf-8-sig"))
files = [t for t in tree if t["type"] == "blob" and t["path"].startswith("BioCAS20")
         and t["path"].endswith((".wav", ".json"))]
extra = [t for t in tree if t["type"] == "blob" and t["path"] in ("LICENSE", "README.md")]
files = sorted(files, key=lambda t: (t["path"].split("/")[0], t["path"])) + extra
total = sum(t["size"] for t in files)


def get(t):
    out = os.path.join(DEST, *t["path"].split("/"))
    if os.path.exists(out) and os.path.getsize(out) == t["size"]:
        return t["size"], True
    os.makedirs(os.path.dirname(out), exist_ok=True)
    url = BASE + urllib.parse.quote(t["path"])
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "resondi-research"})
            data = urllib.request.urlopen(req, timeout=60).read()
            if len(data) != t["size"]:
                raise IOError(f"size {len(data)} != {t['size']}")
            tmp = out + ".part"
            open(tmp, "wb").write(data)
            os.replace(tmp, out)
            return t["size"], False
        except Exception as e:  # noqa: BLE001
            time.sleep(2 * (attempt + 1))
            err = e
    print("FAILED", t["path"], err, flush=True)
    return 0, False


done = 0
t0 = time.time()
with ThreadPoolExecutor(8) as ex:
    for i, (n, _) in enumerate(ex.map(get, files), 1):
        done += n
        if i % 250 == 0 or i == len(files):
            el = time.time() - t0
            print(f"{i}/{len(files)} files  {done / 1e6:,.0f}/{total / 1e6:,.0f} MB  {done / 1e6 / max(el, 1):.2f} MB/s", flush=True)
missing = [t["path"] for t in files
           if not (os.path.exists(os.path.join(DEST, *t["path"].split("/"))) and
                   os.path.getsize(os.path.join(DEST, *t["path"].split("/"))) == t["size"])]
print("DONE" if not missing else f"INCOMPLETE: {len(missing)} files missing; re-run to resume", flush=True)

