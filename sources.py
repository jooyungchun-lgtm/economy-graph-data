"""Data source fetchers. Standard library only (runs on GitHub Actions without installs).

Every fetcher returns {series_key: {"YYYY-MM": float}} with one value per month.
Raw downloads are cached in pipeline/.cache for CACHE_HOURS to avoid hammering sources.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
import time
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".cache")
CACHE_HOURS = 20
UA = "Mozilla/5.0 (compatible; EconomyGraph-prototype/0.1)"

Monthly = dict[str, float]


# ---------------------------------------------------------------- http + cache
SECRET_ENV = ("ECOS_API_KEY", "BLS_API_KEY")


def redact(text: str) -> str:
    """Never let API keys reach logs, reports or exceptions (ECOS puts the key in the URL path)."""
    for name in SECRET_ENV:
        v = os.environ.get(name)
        if v:
            text = text.replace(v, "***")
    return text


def _get(url: str, cache_name: str, data: bytes | None = None, headers: dict | None = None) -> bytes:
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, cache_name)
    if os.path.exists(path) and time.time() - os.path.getmtime(path) < CACHE_HOURS * 3600:
        with open(path, "rb") as f:
            return f.read()
    h = {"User-Agent": UA}
    h.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=h)
    last = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                body = r.read()
            break
        except Exception as e:  # network hiccup: retry with backoff
            last = e
            time.sleep(3 * (attempt + 1))
    else:
        raise RuntimeError(redact(f"download failed: {url}: {last}"))
    with open(path + ".tmp", "wb") as f:
        f.write(body)
    os.replace(path + ".tmp", path)
    return body


def _num(s) -> float | None:
    try:
        v = float(s)
    except (TypeError, ValueError):
        return None
    return v if v == v else None  # drop NaN


def _month_last(points: list[tuple[str, float]]) -> Monthly:
    """Daily/weekly points (YYYY-MM-DD, v), sorted -> last value of each month."""
    out: Monthly = {}
    for d, v in sorted(points):
        out[d[:7]] = v
    return out


# ---------------------------------------------------------------- Federal Reserve Board (DDP)
# NOTE: the DDP package download is scheduled for retirement on 2027-03-31
# (page removal 2027-07-01). Replace with release-page CSVs before then.
FED_ARCHIVE = os.path.join(HERE, "archive", "fed")  # filled by archive_fed.py


def _fed_archived(filename: str) -> bytes:
    """Newest archived copy of a Fed file (archive/fed/<YYYY-MM-DD>/<filename>)."""
    days = sorted(os.listdir(FED_ARCHIVE), reverse=True) if os.path.isdir(FED_ARCHIVE) else []
    for d in days:
        p = os.path.join(FED_ARCHIVE, d, filename)
        if os.path.isfile(p):
            print(f"  note Fed {filename}: live download failed, using archive {d}")
            with open(p, "rb") as f:
                return f.read()
    raise RuntimeError(f"no archived copy of {filename}")


def _fed_get(url: str, cache_name: str, archive_name: str) -> bytes:
    try:
        return _get(url, cache_name)
    except Exception:
        return _fed_archived(archive_name)


def fed_release(release: str, series: list[str]) -> dict[str, Monthly]:
    raw = _fed_get(f"https://www.federalreserve.gov/datadownload/Output.aspx?rel={release}&filetype=zip",
                   f"fed_{release}.zip", f"{release}.zip")
    zf = zipfile.ZipFile(io.BytesIO(raw))
    name = next(n for n in zf.namelist() if n.lower().endswith("_data.xml"))
    want = set(series)
    out: dict[str, Monthly] = {}
    for _, el in ET.iterparse(zf.open(name), events=("end",)):
        if not el.tag.endswith("}Series"):
            continue
        sn = el.get("SERIES_NAME")
        if sn in want:
            pts = []
            for o in el:
                if o.tag.endswith("}Obs"):
                    v = _num(o.get("OBS_VALUE"))
                    if v is not None:
                        pts.append((o.get("TIME_PERIOD"), v))
            out[sn] = _month_last(pts)
        el.clear()
    missing = want - out.keys()
    if missing:
        raise RuntimeError(f"Fed {release}: series not found {sorted(missing)}")
    return out


def fed_ebp() -> dict[str, Monthly]:
    """Excess Bond Premium (Gilchrist-Zakrajsek), Federal Reserve Board."""
    raw = _fed_get("https://www.federalreserve.gov/econres/notes/feds-notes/ebp_csv.csv", "fed_ebp.csv", "EBP.csv")
    out: Monthly = {}
    for row in csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))):
        v = _num(row.get("ebp"))
        if v is not None:
            out[row["date"][:7]] = v
    return {"ebp": out}


# ---------------------------------------------------------------- BLS (API v1, no key)
def bls(series: list[str], start_year: int, end_year: int) -> dict[str, Monthly]:
    """v1 limits: 25 series and 10 years per request, 25 requests/day per IP.
    With BLS_API_KEY set, v2 is used (20 years per request, 500/day)."""
    key = os.environ.get("BLS_API_KEY")
    span = 20 if key else 10
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/" if key else \
          "https://api.bls.gov/publicAPI/v1/timeseries/data/"
    out: dict[str, Monthly] = {s: {} for s in series}
    for i in range(0, len(series), 25):
        chunk = series[i:i + 25]
        y = start_year
        while y <= end_year:
            y2 = min(y + span - 1, end_year)
            body = {"seriesid": chunk, "startyear": str(y), "endyear": str(y2)}
            if key:
                body["registrationkey"] = key
            digest = hashlib.sha1(",".join(chunk).encode()).hexdigest()[:10]  # stable across runs
            tag = f"bls_{digest}_{y}_{y2}.json"
            raw = _get(url, tag, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
            js = json.loads(raw)
            if js.get("status") != "REQUEST_SUCCEEDED":
                os.remove(os.path.join(CACHE, tag))  # do not cache failures
                raise RuntimeError(f"BLS: {js.get('status')} {js.get('message')}")
            for s in js["Results"]["series"]:
                for d in s["data"]:
                    if re.fullmatch(r"M(0[1-9]|1[0-2])", d["period"]):
                        v = _num(d["value"])
                        if v is not None:
                            out[s["seriesID"]][f"{d['year']}-{d['period'][1:]}"] = v
            y = y2 + 1
    return out


# ---------------------------------------------------------------- World Bank Pink Sheet (monthly xlsx)
PINK_PAGE = "https://www.worldbank.org/en/research/commodity-markets"


def _xlsx_rows(raw: bytes, sheet_name: str) -> list[dict[str, str]]:
    z = zipfile.ZipFile(io.BytesIO(raw))
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
          "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", ns):
            shared.append("".join(t.text or "" for t in si.iter(f"{{{ns['m']}}}t")))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rid = next(s.get(f"{{{ns['r']}}}id") for s in wb.iter(f"{{{ns['m']}}}sheet") if s.get("name") == sheet_name)
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    target = next(r.get("Target") for r in rels if r.get("Id") == rid)
    path = target.lstrip("/") if target.startswith("/") else "xl/" + target
    rows = []
    for row in ET.fromstring(z.read(path)).iter(f"{{{ns['m']}}}row"):
        cells = {}
        for c in row.findall("m:c", ns):
            col = re.match(r"[A-Z]+", c.get("r")).group()
            v = c.find("m:v", ns)
            if v is None:
                is_ = c.find("m:is", ns)
                txt = "".join(t.text or "" for t in is_.iter(f"{{{ns['m']}}}t")) if is_ is not None else None
            else:
                txt = shared[int(v.text)] if c.get("t") == "s" else v.text
            if txt is not None:
                cells[col] = txt
        rows.append(cells)
    return rows


def pink_sheet(columns: dict[str, str]) -> dict[str, Monthly]:
    """columns: {our_key: exact Pink Sheet header text}."""
    page = _get(PINK_PAGE, "wb_commodity_page.html").decode("utf-8", "replace")
    m = re.search(r'https?://[^"\']*CMO-Historical-Data-Monthly\.xlsx', page)
    if not m:
        raise RuntimeError("Pink Sheet link not found on World Bank page")
    rows = _xlsx_rows(_get(m.group(), "wb_pink_monthly.xlsx"), "Monthly Prices")
    header = next(r for r in rows if any(v.strip() == "Gold" for v in r.values()))
    col_of = {v.strip(): k for k, v in header.items()}
    out: dict[str, Monthly] = {}
    for key, title in columns.items():
        if title not in col_of:
            raise RuntimeError(f"Pink Sheet column missing: {title}")
        col, series = col_of[title], {}
        for r in rows:
            mm = re.fullmatch(r"(\d{4})M(\d{2})", (r.get("A") or "").strip())
            if mm:
                v = _num(r.get(col))
                if v is not None:
                    series[f"{mm.group(1)}-{mm.group(2)}"] = v
        out[key] = series
    return out


# ---------------------------------------------------------------- Crypto (Kraken public OHLC, weekly bars)
def kraken(pairs: dict[str, str]) -> dict[str, Monthly]:
    """Weekly bars (max 720 = ~13.8 years). Each bar is assigned to the month in which it closes."""
    out = {}
    for key, pair in pairs.items():
        js = json.loads(_get(f"https://api.kraken.com/0/public/OHLC?pair={pair}&interval=10080",
                             f"kraken_{pair}.json"))
        if js.get("error"):
            raise RuntimeError(f"Kraken {pair}: {js['error']}")
        bars = next(v for k, v in js["result"].items() if k != "last")
        pts = []
        for b in bars:
            close_t = int(b[0]) + 7 * 86400 - 1
            d = datetime.fromtimestamp(close_t, timezone.utc).strftime("%Y-%m-%d")
            pts.append((d, float(b[4])))
        out[key] = _month_last(pts)
    return out


# ---------------------------------------------------------------- Bank of Korea ECOS
def ecos(items: dict[str, tuple[str, ...]], start: str, end: str) -> dict[str, Monthly]:
    """items: {our_key: (stat_code, item1[, item2])}; start/end 'YYYYMM'.
    Needs ECOS_API_KEY (free from ecos.bok.or.kr). Returns {} when the key is absent."""
    key = os.environ.get("ECOS_API_KEY")
    if not key:
        return {}
    out = {}
    for name, (stat, *its) in items.items():
        path = "/".join([stat, "M", start, end, *its])
        url = f"https://ecos.bok.or.kr/api/StatisticSearch/{key}/json/kr/1/100000/{path}"
        js = json.loads(_get(url, f"ecos_{stat}_{'_'.join(its)}_{start}_{end}.json"))
        rows = js.get("StatisticSearch", {}).get("row")
        if not rows:
            os.remove(os.path.join(CACHE, f"ecos_{stat}_{'_'.join(its)}_{start}_{end}.json"))
            raise RuntimeError(f"ECOS {name}: {js.get('RESULT')}")
        out[name] = {f"{r['TIME'][:4]}-{r['TIME'][4:6]}": v for r in rows
                     if (v := _num(r["DATA_VALUE"])) is not None}
    return out
