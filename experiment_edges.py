"""Compare candidate bases for the app's relationship lines (rolling correlations).

  python3 pipeline/experiment_edges.py      -> pipeline/out/experiment_edges.md

Candidates = (change horizon h months, rolling window W months, method).
Scored on the expected-relationship list from indicators.py:
  robust pairs : expected pairs that hold over the full sample (|r 12m| >= 0.3 with the expected sign,
                 Pearson and rank both) -> a good basis should show them, with the right sign, most of the time
  null pairs   : all pairs with full-sample |r| < 0.1 at both 1m and 12m -> a good basis should NOT draw lines
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B  # noqa: E402
import indicators as I  # noqa: E402

CANDIDATES = [(1, 36), (3, 36), (3, 60), (6, 60), (12, 120)]
METHODS = ["pearson", "rank"]
SHOW = float(os.environ.get("SHOW", "0.30"))  # the app draws a line when |r| >= SHOW
if os.environ.get("ONLY"):  # e.g. ONLY="3x60,1x36"
    CANDIDATES = [tuple(map(int, c.split("x"))) for c in os.environ["ONLY"].split(",")]
if os.environ.get("METHOD"):
    METHODS = [os.environ["METHOD"]]


def rcorr(a: dict, b: dict, lag: int, lo: int, hi: int, method: str, min_obs: int):
    ms = [m for m in range(lo, hi + 1) if m in a and m + lag in b]
    if len(ms) < min_obs:
        return None
    xs, ys = [a[m] for m in ms], [b[m + lag] for m in ms]
    if method == "rank":
        xs, ys = B._ranks(xs), B._ranks(ys)
    return B.pearson(xs, ys)


def series_of(a, b, lag, h, w, method, start, end):
    out = {}
    for e in range(start, end + 1):
        r = rcorr(a, b, lag, e - w + 1, e, method, int(w * 0.8))
        if r is not None:
            out[e] = r
    return out


def evaluate(spec, levels, pairs, cutoff):
    tf = {row[0]: row[4] for row in spec}
    lo, last = B.mi(B.CORR_FROM), cutoff - 1
    ch = {h: {i: B.changes(levels[i], tf[i], h) for i in levels} for h in {1, 3, 6, 12}}

    robust, nulls = [], []
    for a, b, sign, lag in pairs:
        if a in levels and b in levels:
            r12, _ = B.corr(ch[12][a], ch[12][b], lag, lo)
            rs = B.spearman(ch[12][a], ch[12][b], lag, lo)
            if r12 is not None and rs is not None and r12 * sign >= 0.3 and rs * sign >= 0.3:
                robust.append((a, b, sign, lag))
    known = {frozenset((a, b)) for a, b, *_ in pairs}
    ids = sorted(levels)
    for x in range(len(ids)):
        for y in range(x + 1, len(ids)):
            a, b = ids[x], ids[y]
            if frozenset((a, b)) in known:
                continue
            r1, n = B.corr(ch[1][a], ch[1][b], 0, lo)
            r12, _ = B.corr(ch[12][a], ch[12][b], 0, lo)
            if r1 is not None and r12 is not None and n >= 120 and abs(r1) < 0.1 and abs(r12) < 0.1:
                nulls.append((a, b, 0, 0))

    rows = []
    for h, w in CANDIDATES:
        for method in METHODS:
            start = lo + h + w - 1
            keep = show = cnt = 0
            jit, jn = 0.0, 0
            for a, b, sign, lag in robust:
                s = series_of(ch[h][a], ch[h][b], lag, h, w, method, start, last - lag)
                for e, r in s.items():
                    cnt += 1
                    keep += r * sign > 0
                    show += r * sign >= SHOW
                    if e - 1 in s:
                        jit += abs(r - s[e - 1]); jn += 1
            fp = fcnt = 0
            for a, b, _s, _l in nulls:
                s = series_of(ch[h][a], ch[h][b], 0, h, w, method, start, last)
                fcnt += len(s)
                fp += sum(abs(r) >= SHOW for r in s.values())
                for e, r in s.items():
                    if e - 1 in s:
                        jit += abs(r - s[e - 1]); jn += 1
            # clutter: lines drawn at the latest month across every pair
            drawn = total = 0
            for x in range(len(ids)):
                for y in range(x + 1, len(ids)):
                    r = rcorr(ch[h][ids[x]], ch[h][ids[y]], 0, last - w + 1, last, method, int(w * 0.8))
                    if r is not None:
                        total += 1
                        drawn += abs(r) >= SHOW
            rows.append({
                "basis": f"{h}m 변화 · {w}m 창 · {'순위' if method == 'rank' else '일반'}",
                "obs": w // h, "start": B.ym(start),
                "keep": keep / cnt if cnt else None, "show": show / cnt if cnt else None,
                "fp": fp / fcnt if fcnt else None, "jitter": jit / jn if jn else None,
                "drawn": f"{drawn}/{total}",
            })
    return robust, nulls, rows


def table(rows):
    p = lambda v: "–" if v is None else f"{v:.0%}"  # noqa: E731
    L = ["| 기준 | 독립 관측 수 | 타임머신 시작 | 부호 일치 ↑ | 선 표시 ↑ | 잘못된 선 ↓ | 월간 흔들림 ↓ | 최근 표시 선 |",
         "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['basis']} | {r['obs']} | {r['start']} | {p(r['keep'])} | {p(r['show'])} | {p(r['fp'])} | "
                 f"{r['jitter']:.3f} | {r['drawn']} |")
    return L


def main():
    now = datetime.now(timezone.utc)
    cutoff = B.mi(now.strftime("%Y-%m"))
    raw, errors = B.fetch_all(bool(os.environ.get("ECOS_API_KEY")))
    out = ["# 관계선 계산 기준 시험\n", f"생성: {now:%Y-%m-%d %H:%M} UTC · 표시 기준 |r| ≥ {SHOW}\n",
           "- **부호 일치**: 확실한 관계(전체 기간에 성립)에서 롤링 r의 부호가 맞는 비율",
           f"- **선 표시**: 같은 관계가 앱에 선으로 그려지는 비율 (부호 일치 + |r| ≥ {SHOW})",
           f"- **잘못된 선**: 관계가 없는 쌍(전체 기간 |r| < 0.1)에 선이 그려지는 비율",
           "- **월간 흔들림**: 타임머신을 한 달 옮길 때 r이 평균적으로 바뀌는 크기 (작을수록 부드러움)",
           "- **최근 표시 선**: 가장 최근 시점에 그래프에 그려지는 선 수 / 계산 가능한 쌍 수\n"]
    if errors:
        out += ["수집 실패: " + "; ".join(errors), ""]
    sets = [("US", I.US, I.PAIRS_US)]
    if os.environ.get("ECOS_API_KEY"):
        sets.append(("KR", I.KR + [r for r in I.US if r[0] in I.KR_SHARED], I.PAIRS_KR))
    for code, spec, pairs in sets:
        levels = B.build_levels(spec, raw, cutoff)
        print(f"evaluating {code} ...")
        robust, nulls, rows = evaluate(spec, levels, pairs, cutoff)
        out += [f"## {code}\n", f"확실한 관계 {len(robust)}쌍, 관계 없는 쌍 {len(nulls)}개로 평가\n"] + table(rows) + [""]
    path = os.path.join(B.OUT, os.environ.get("OUTFILE", "experiment_edges.md"))
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")
    print(f"done -> {path}")


if __name__ == "__main__":
    main()
