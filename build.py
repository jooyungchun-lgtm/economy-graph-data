"""Economy Graph data pipeline prototype.

  python3 pipeline/build.py            # fetch (cached 20h), compute, write pipeline/out/
  ECOS_API_KEY=... python3 pipeline/build.py   # also builds Korea

Outputs (what the app would download):
  out/<country>/series.json  monthly levels per indicator (full history from 1970)
  out/<country>/edges.json   rolling 36-month correlation of monthly changes for every pair,
                             one value per month (drives the time machine)
  out/report.md              validation of expected relationships + data coverage
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import indicators as I  # noqa: E402
import sources as S  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
HISTORY_FROM = "1970-01"
CORR_FROM = "1990-01"      # correlation sample start
# Relationship-line basis, chosen by experiment_edges.py (2026-11-22):
# 3-month changes, 60-month window, rank correlation, line drawn when |r| >= 0.4.
EDGE_H = 3                 # change horizon (months)
WINDOW = 60                # rolling window (months)
MIN_OBS = 48               # minimum overlapping observations in a window (80%)
EDGE_METHOD = "rank"       # rank (Spearman) resists one-off shocks such as 2020
SHOW_TIERS = [0.4, 0.55, 0.7]  # app: hide below 0.4, three line thicknesses
STRONG, WEAK = 0.30, 0.15  # |r| thresholds for the verdict


# ---------------------------------------------------------------- month helpers
def mi(ym: str) -> int:
    return int(ym[:4]) * 12 + int(ym[5:7]) - 1


def ym(i: int) -> str:
    return f"{i // 12:04d}-{i % 12 + 1:02d}"


# ---------------------------------------------------------------- fetch
def fetch_all(with_kr: bool) -> tuple[dict, list[str]]:
    raw, errors = {}, []
    now_year = datetime.now(timezone.utc).year
    jobs = [(f"Fed {r}", lambda r=r, s=s: S.fed_release(r, s)) for r, s in I.FED.items()]
    jobs += [
        ("Fed EBP", S.fed_ebp),
        ("BLS", lambda: S.bls(I.BLS, 1969, now_year)),
        ("World Bank Pink Sheet", lambda: S.pink_sheet(I.PINK)),
        ("Kraken", lambda: S.kraken(I.KRAKEN)),
    ]
    if with_kr:
        jobs.append(("ECOS", lambda: S.ecos(I.ECOS, "196001", f"{now_year}12")))
    for name, fn in jobs:
        try:
            got = fn()
            raw.update(got)
            print(f"  ok   {name}: {len(got)} series")
        except Exception as e:  # keep going; report what failed
            errors.append(f"{name}: {e}")
            print(f"  FAIL {name}: {e}")
    return raw, errors


# ---------------------------------------------------------------- levels + changes
def build_levels(spec, raw, cutoff: int) -> dict[str, dict[int, float]]:
    """Monthly level per indicator, keyed by month index; drops the current (incomplete) month."""
    out = {}
    for iid, _n, _u, _s, _t, recipe in spec:
        kind, *keys = recipe
        if any(k not in raw for k in keys):
            continue
        src = [{mi(k): v for k, v in raw[key].items()} for key in keys]
        a = src[0]
        if kind == "raw":
            s = dict(a)
        elif kind == "yoy":
            s = {m: (v / a[m - 12] - 1) * 100 for m, v in a.items() if m - 12 in a and a[m - 12]}
        elif kind == "spread":
            s = {m: v - src[1][m] for m, v in a.items() if m in src[1]}
        elif kind == "mdiff":
            s = {m: v - a[m - 1] for m, v in a.items() if m - 1 in a}
        else:
            raise ValueError(kind)
        s = {m: round(v, 4) for m, v in s.items() if mi(HISTORY_FROM) <= m < cutoff}
        if s:
            out[iid] = s
    return out


def changes(level: dict[int, float], transform: str, h: int) -> dict[int, float]:
    out = {}
    for m, v in level.items():
        if transform == "flow":
            win = [level.get(m - k) for k in range(h)]
            if all(x is not None for x in win):
                out[m] = sum(win)
        elif m - h in level:
            p = level[m - h]
            if transform == "pct":
                if p > 0 and v > 0:
                    out[m] = math.log(v / p)
            else:
                out[m] = v - p
    return out


# ---------------------------------------------------------------- statistics
def pearson(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx == 0 or syy == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(sxx * syy)


def _ranks(v: list[float]) -> list[float]:
    order = sorted(range(len(v)), key=v.__getitem__)
    r = [0.0] * len(v)
    i = 0
    while i < len(order):  # average ranks for ties
        j = i
        while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2
        i = j + 1
    return r


def spearman(a: dict, b: dict, lag: int, lo: int):
    """Rank correlation: robust to outliers such as the 2020 COVID months."""
    ms = [m for m in sorted(a) if m >= lo and m + lag in b]
    return pearson(_ranks([a[m] for m in ms]), _ranks([b[m + lag] for m in ms]))


def corr(a: dict, b: dict, lag: int = 0, lo: int | None = None, hi: int | None = None):
    """r between a[m] and b[m+lag], for months m in [lo, hi]."""
    cand = range(lo, hi + 1) if lo is not None and hi is not None else sorted(a)
    ms = [m for m in cand if m in a and m + lag in b and (lo is None or m >= lo) and (hi is None or m <= hi)]
    return pearson([a[m] for m in ms], [b[m + lag] for m in ms]), len(ms)


def rolling(a: dict, b: dict, lag: int, start: int, end: int):
    """Rolling WINDOW-month correlation of a[m] vs b[m+lag], one value per window end month."""
    vals = []
    for e in range(start, end + 1):
        ms = [m for m in range(e - WINDOW + 1, e + 1) if m in a and m + lag in b]
        if len(ms) < MIN_OBS:
            vals.append(None)
            continue
        xs, ys = [a[m] for m in ms], [b[m + lag] for m in ms]
        if EDGE_METHOD == "rank":
            xs, ys = _ranks(xs), _ranks(ys)
        r = pearson(xs, ys)
        vals.append(round(r, 2) if r is not None else None)
    return vals


# ---------------------------------------------------------------- country build
def build_country(code: str, spec: list, levels: dict, pairs: list, cutoff: int) -> list[str]:
    tf = {row[0]: row[4] for row in spec}
    ch1 = {i: changes(levels[i], tf[i], 1) for i in levels}
    ch12 = {i: changes(levels[i], tf[i], 12) for i in levels}
    chE = {i: changes(levels[i], tf[i], EDGE_H) for i in levels}  # relationship-line basis
    lo, last = mi(CORR_FROM), cutoff - 1
    os.makedirs(os.path.join(OUT, code), exist_ok=True)

    # series.json
    series = []
    for iid, name, unit, src, t, _ in spec:
        if iid in levels:
            ms = sorted(levels[iid])
            series.append({"id": iid, "name": name, "unit": unit, "source": src, "transform": t,
                           "start": ym(ms[0]), "values": [levels[iid].get(m) for m in range(ms[0], ms[-1] + 1)]})
    with open(os.path.join(OUT, code, "series.json"), "w") as f:
        json.dump({"country": code, "series": series}, f, separators=(",", ":"))

    # edges.json: rolling correlation for every pair (time machine)
    ids = [s["id"] for s in series]
    start = lo + WINDOW - 1
    edges = []
    for x in range(len(ids)):
        for y in range(x + 1, len(ids)):
            v = rolling(chE[ids[x]], chE[ids[y]], 0, start, last)
            if any(r is not None for r in v):
                first = next(k for k, r in enumerate(v) if r is not None)
                edges.append({"a": ids[x], "b": ids[y], "start": ym(start + first), "r": v[first:]})
    with open(os.path.join(OUT, code, "edges.json"), "w") as f:
        json.dump({"country": code, "window": WINDOW, "change_months": EDGE_H, "method": EDGE_METHOD,
                   "show_tiers": SHOW_TIERS, "edges": edges}, f, separators=(",", ":"))

    # report section
    name_of = {row[0]: row[1] for row in spec}
    L = [f"## {code.upper()}\n", "### 기대 관계 검증\n",
         f"- 기간: {CORR_FROM} ~ {ym(last)} · 변화량 기준 상관계수 (금리는 차이, 가격은 로그 변화율)",
         "- `r 1m`: 월간 변화끼리 · `r 12m`: 12개월 변화끼리 (경기 흐름에 가까움, 겹치는 구간이라 표본이 실제보다 적은 효과)",
         f"- `최근 관계선`: 앱 관계선 기준({EDGE_H}개월 변화 · {WINDOW}개월 창 · {'순위' if EDGE_METHOD == 'rank' else '일반'} 상관)의 최신값 · "
         f"`부호 유지율`: 같은 기준의 롤링 창 중 기대 부호와 같은 비율",
         f"- 판정 (`r 12m` 기준): ✅ 부호 일치·|r|≥{STRONG} · 🟡 부호 일치·약함 · ⚪ 거의 0 (|r|<{WEAK}) · ❌ 반대 부호·|r|≥{WEAK}\n",
         "- `순위 12m`: 12개월 변화의 순위 상관 (극단값 영향 제거). `r 12m`과 차이가 크면 특정 사건(예: 2020년 코로나)이 결과를 좌우한 것\n",
         "| A → B | 지연 | 기대 | r 1m | r 12m | 순위 12m | 최근 관계선 | 부호 유지율 | n | 판정 |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    tally = {"✅": 0, "🟡": 0, "⚪": 0, "❌": 0, "–": 0}
    for a, b, sign, lag in pairs:
        if a not in levels or b not in levels:
            L.append(f"| {name_of.get(a, a)} → {name_of.get(b, b)} | {lag} | {'+' if sign > 0 else '−'} | – | – | – | – | – | 0 | – 데이터 없음 |")
            tally["–"] += 1
            continue
        r1, _ = corr(ch1[a], ch1[b], lag, lo)
        r12, n12 = corr(ch12[a], ch12[b], lag, lo)
        rs12 = spearman(ch12[a], ch12[b], lag, lo)
        roll_all = rolling(chE[a], chE[b], lag, lo + WINDOW - 1, last - lag)
        r36 = roll_all[-1] if roll_all else None
        roll = [r for r in roll_all if r is not None]
        keep = sum(1 for r in roll if r * sign > 0) / len(roll) if roll else None
        if r12 is None:
            v = "–"
        elif abs(r12) < WEAK:
            v = "⚪"
        elif r12 * sign > 0:
            v = "✅" if abs(r12) >= STRONG else "🟡"
        else:
            v = "❌"
        tally[v] += 1
        f = lambda r: "–" if r is None else f"{r:+.2f}"  # noqa: E731
        L.append(f"| {name_of[a]} → {name_of[b]} | {lag} | {'+' if sign > 0 else '−'} | {f(r1)} | {f(r12)} | {f(rs12)} | {f(r36)} | "
                 f"{'–' if keep is None else f'{keep:.0%}'} | {n12} | {v} |")
    L.insert(2, "결과: " + " · ".join(f"{k} {n}" for k, n in tally.items() if n) + "\n")

    # strongest relationships not in the expected list (candidates for explanations)
    known = {frozenset((a, b)) for a, b, *_ in pairs}
    found = []
    for x in range(len(ids)):
        for y in range(x + 1, len(ids)):
            if frozenset((ids[x], ids[y])) in known:
                continue
            r, n = corr(ch12[ids[x]], ch12[ids[y]], 0, lo)
            if r is not None and n >= 60:
                found.append((abs(r), r, ids[x], ids[y], n))
    found.sort(reverse=True)
    L += ["\n### 목록에 없는 강한 관계 (r 12m 상위 15, 설명 추가 후보)\n", "| A | B | r 12m | n |", "|---|---|---|---|"]
    L += [f"| {name_of[a]} | {name_of[b]} | {r:+.2f} | {n} |" for _, r, a, b, n in found[:15]]

    L += ["\n### 데이터 범위\n", "| 지표 | 출처 | 시작 | 끝 | 개월 수 |", "|---|---|---|---|---|"]
    for s in series:
        ms = sorted(levels[s["id"]])
        L.append(f"| {s['name']} | {s['source']} | {ym(ms[0])} | {ym(ms[-1])} | {len(ms)} |")
    missing = [row[1] for row in spec if row[0] not in levels]
    if missing:
        L.append(f"\n누락 지표: {', '.join(missing)}")
    sizes = {fn: os.path.getsize(os.path.join(OUT, code, fn)) for fn in ("series.json", "edges.json")}
    L.append(f"\n파일 크기: " + ", ".join(f"{k} {v / 1024:.0f}KB" for k, v in sizes.items()))
    return L


def write_manifest(now, cutoff: int, errors: list[str]) -> None:
    """out/manifest.json: the app downloads this small file first and fetches only files whose hash changed."""
    import hashlib
    files = {}
    for code in sorted(os.listdir(OUT)):
        d = os.path.join(OUT, code)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            p = os.path.join(d, fn)
            with open(p, "rb") as f:
                files[f"{code}/{fn}"] = {"sha256": hashlib.sha256(f.read()).hexdigest(), "bytes": os.path.getsize(p)}
    manifest = {"schema": 1, "generated_utc": now.isoformat(timespec="seconds"), "through": ym(cutoff - 1),
                "complete": not errors, "files": files}
    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1)


def main():
    now = datetime.now(timezone.utc)
    cutoff = mi(now.strftime("%Y-%m"))  # exclude the current, incomplete month
    with_kr = bool(os.environ.get("ECOS_API_KEY"))
    print("fetching ...")
    raw, errors = fetch_all(with_kr)
    if not with_kr and os.environ.get("REQUIRE_KR"):
        # in CI a missing key must fail the run, otherwise stale Korea files would be republished as current
        errors.append("ECOS: ECOS_API_KEY secret is not set")
        print("  FAIL ECOS: ECOS_API_KEY secret is not set")

    report = [f"# 데이터 수집 시제품 결과\n", f"생성: {now:%Y-%m-%d %H:%M} UTC · 기준월: {ym(cutoff - 1)}까지\n"]
    if errors:
        report += ["**수집 실패**\n"] + [f"- {e}" for e in errors] + [""]

    us_levels = build_levels(I.US, raw, cutoff)
    print("building US ...")
    report += build_country("us", I.US, us_levels, I.PAIRS_US, cutoff)

    kr_spec = I.KR + [row for row in I.US if row[0] in I.KR_SHARED]
    kr_levels = build_levels(kr_spec, raw, cutoff)
    report.append("")
    if with_kr:
        print("building KR ...")
        report += build_country("kr", kr_spec, kr_levels, I.PAIRS_KR, cutoff)
    else:
        report += ["## KR\n", "ECOS_API_KEY가 없어 한국은행 데이터(기준금리·국고채·CPI·실업률)는 건너뜀. "
                   "USD/KRW(연준 H.10)만 수집됨."]

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "report.md"), "w") as f:
        f.write("\n".join(report) + "\n")
    write_manifest(now, cutoff, errors)
    print(f"done -> {os.path.join(OUT, 'report.md')}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
