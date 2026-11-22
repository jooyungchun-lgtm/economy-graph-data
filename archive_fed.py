"""Archive every Federal Reserve Board DDP release package before the service retires.

DDP notice (inside the downloaded files): the preformatted package feature retires 2027-03-31,
the DDP page is removed 2027-07-01. This keeps a dated, checksummed copy of all history.

  python3 pipeline/archive_fed.py            # all releases -> pipeline/archive/fed/<YYYY-MM-DD>/
  python3 pipeline/archive_fed.py H15 H10    # only some

Re-running on the same day skips files that are already present and valid.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import urllib.request
import zipfile
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "archive", "fed")
UA = "Mozilla/5.0 (compatible; EconomyGraph-prototype/0.1)"
RELEASES = ["CHGDEL", "CP", "DSR", "E2", "FOR", "G17", "G19", "G20", "H10", "H15", "H3",
            "H41", "H6", "H8", "PRATES", "SCOOS", "SLOOS", "Z1"]
EXTRA = {"EBP.csv": "https://www.federalreserve.gov/econres/notes/feds-notes/ebp_csv.csv"}


def download(url: str, path: str) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=600) as r, open(path + ".part", "wb") as f:
                while chunk := r.read(1 << 20):
                    f.write(chunk)
            os.replace(path + ".part", path)
            return
        except Exception as e:
            err = e
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"{url}: {err}")


def check_zip(path: str) -> list[str]:
    with zipfile.ZipFile(path) as z:
        bad = z.testzip()
        if bad:
            raise RuntimeError(f"corrupt member {bad}")
        names = z.namelist()
    if not any(n.lower().endswith("_data.xml") for n in names):
        raise RuntimeError("no *_data.xml inside")
    return names


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def main(argv: list[str]) -> int:
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out = os.path.join(ROOT, day)
    os.makedirs(out, exist_ok=True)
    manifest_path = os.path.join(out, "manifest.json")
    manifest = json.load(open(manifest_path)) if os.path.exists(manifest_path) else {"files": {}}
    targets = {f"{r}.zip": f"https://www.federalreserve.gov/datadownload/Output.aspx?rel={r}&filetype=zip"
               for r in (argv or RELEASES)}
    if not argv:
        targets.update(EXTRA)
    failed = []
    for name, url in targets.items():
        path = os.path.join(out, name)
        try:
            if not os.path.exists(path):
                download(url, path)
                time.sleep(2)  # be polite to the server
            members = check_zip(path) if name.endswith(".zip") else []
            manifest["files"][name] = {"url": url, "bytes": os.path.getsize(path),
                                       "sha256": sha256(path), "members": members}
            print(f"  ok   {name:12s} {os.path.getsize(path) / 1e6:8.1f} MB")
        except Exception as e:
            failed.append(name)
            if os.path.exists(path):
                os.replace(path, path + ".bad")  # keep for inspection, never silently reuse
            print(f"  FAIL {name}: {e}")
    manifest.update({"archived_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                     "source": "Federal Reserve Board Data Download Program (public domain)"})
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=1)
    total = sum(v["bytes"] for v in manifest["files"].values())
    print(f"{len(manifest['files'])} files, {total / 1e6:.1f} MB -> {out}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
