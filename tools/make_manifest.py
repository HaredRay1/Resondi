"""Write MANIFEST.txt: every file in the Resondi folder, one path per line, so a reader (or Claude chat) can see what
exists without opening the folder. A folder holding more than LIMIT files of its own (audio clips, render frames)
gets one line with the count. Skips .git, __pycache__ and node_modules.

    python tools/make_manifest.py
"""
import collections
import datetime
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {".git", "__pycache__", "node_modules"}
LIMIT = 100


def files_under(d):
    n, kinds = 0, collections.Counter()
    for _, dirs, fs in os.walk(d):
        dirs[:] = [x for x in dirs if x not in SKIP]
        n += len(fs)
        kinds.update(os.path.splitext(f)[1].lower() or "(none)" for f in fs)
    return n, kinds


lines = []


def walk(d, rel):
    """List d's files, then its folders. A folder holding more than LIMIT files of its own (clips, frames) has them
    as one line."""
    entries = sorted((x for x in os.listdir(d) if x not in SKIP), key=str.lower)
    files = [x for x in entries if os.path.isfile(os.path.join(d, x))]
    dirs = [x for x in entries if os.path.isdir(os.path.join(d, x))]
    if len(files) > LIMIT:
        kinds = collections.Counter(os.path.splitext(f)[1].lower() or "(none)" for f in files)
        top = ", ".join(f"{k} {v}" for k, v in kinds.most_common(3))
        lines.append(f"{rel}/* ({len(files)} files: {top})")
    else:
        lines.extend((rel + "/" + f).lstrip("/") for f in files)
    for name in dirs:
        p, r = os.path.join(d, name), (rel + "/" + name).lstrip("/")
        if files_under(p)[0] == 0:
            lines.append(f"{r}/ (empty)")
        else:
            walk(p, r)


walk(ROOT, "")
head = (f"Every file in the Resondi folder on {datetime.date.today():%d %B %Y}, written by tools/make_manifest.py. "
        f"A folder with more than {LIMIT} files of its own is one line (folder/*). Not listed: .git, __pycache__, "
        f"node_modules.\n")
with open(os.path.join(ROOT, "MANIFEST.txt"), "w", encoding="utf-8", newline="\n") as f:
    f.write(head + "\n" + "\n".join(lines) + "\n")
print("wrote MANIFEST.txt:", len(lines), "lines")
