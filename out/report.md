# 데이터 수집 시제품 결과

생성: 2026-11-22 12:22 UTC · 기준월: 2026-10까지

## US

### 기대 관계 검증

결과: ✅ 27 · 🟡 3 · ⚪ 4 · ❌ 1

- 기간: 1990-01 ~ 2026-10 · 변화량 기준 상관계수 (금리는 차이, 가격은 로그 변화율)
- `r 1m`: 월간 변화끼리 · `r 12m`: 12개월 변화끼리 (경기 흐름에 가까움, 겹치는 구간이라 표본이 실제보다 적은 효과)
- `최근 관계선`: 앱 관계선 기준(3개월 변화 · 60개월 창 · 순위 상관)의 최신값 · `부호 유지율`: 같은 기준의 롤링 창 중 기대 부호와 같은 비율
- 판정 (`r 12m` 기준): ✅ 부호 일치·|r|≥0.3 · 🟡 부호 일치·약함 · ⚪ 거의 0 (|r|<0.15) · ❌ 반대 부호·|r|≥0.15

- `순위 12m`: 12개월 변화의 순위 상관 (극단값 영향 제거). `r 12m`과 차이가 크면 특정 사건(예: 2020년 코로나)이 결과를 좌우한 것

| A → B | 지연 | 기대 | r 1m | r 12m | 순위 12m | 최근 관계선 | 부호 유지율 | n | 판정 |
|---|---|---|---|---|---|---|---|---|---|
| Fed Funds Rate → 2Y Treasury Yield | 0 | + | +0.43 | +0.82 | +0.80 | +0.42 | 94% | 442 | ✅ |
| Fed Funds Rate → 3M Treasury Bill | 0 | + | +0.76 | +0.98 | +0.97 | +0.91 | 100% | 442 | ✅ |
| 2Y Treasury Yield → 10Y Treasury Yield | 0 | + | +0.80 | +0.82 | +0.80 | +0.87 | 100% | 442 | ✅ |
| 10Y Treasury Yield → 30Y Treasury Yield | 0 | + | +0.94 | +0.94 | +0.94 | +0.93 | 100% | 442 | ✅ |
| Fed Funds Rate → Yield Curve (10Y-2Y) | 0 | − | -0.42 | -0.78 | -0.78 | -0.50 | 99% | 442 | ✅ |
| CPI Inflation (YoY) → Fed Funds Rate | 6 | + | +0.04 | +0.16 | +0.22 | +0.18 | 75% | 435 | 🟡 |
| Core CPI (YoY) → Fed Funds Rate | 6 | + | +0.09 | +0.23 | +0.20 | +0.23 | 73% | 435 | 🟡 |
| Unemployment Rate → Fed Funds Rate | 3 | − | -0.05 | -0.44 | -0.64 | -0.35 | 77% | 438 | ✅ |
| Fed Balance Sheet → 10Y Real Yield (TIPS) | 0 | − | +0.20 | -0.09 | -0.19 | +0.03 | 43% | 274 | ⚪ |
| 10Y Real Yield (TIPS) → 10Y Treasury Yield | 0 | + | +0.78 | +0.80 | +0.76 | +0.93 | 100% | 274 | ✅ |
| 5Y Breakeven Inflation → 10Y Treasury Yield | 0 | + | +0.26 | +0.34 | +0.34 | +0.32 | 100% | 274 | ✅ |
| Industrial Production → Unemployment Rate | 0 | − | -0.75 | -0.74 | -0.52 | -0.22 | 96% | 440 | ✅ |
| Nonfarm Payrolls (change) → Unemployment Rate | 0 | − | -0.96 | -0.94 | -0.75 | -0.37 | 94% | 440 | ✅ |
| Employment-Population Ratio → Unemployment Rate | 0 | − | -0.95 | -0.96 | -0.78 | -0.34 | 97% | 440 | ✅ |
| Unemployment Rate → Wage Growth (YoY) | 6 | − | -0.01 | -0.15 | -0.29 | +0.02 | 37% | 223 | 🟡 |
| Job Openings (JOLTS) → Wage Growth (YoY) | 0 | + | -0.25 | -0.11 | +0.17 | +0.22 | 45% | 223 | ⚪ |
| Unemployment Rate → CPI Inflation (YoY) | 12 | − | +0.17 | +0.23 | +0.10 | +0.07 | 43% | 428 | ❌ |
| M2 Money Supply → CPI Inflation (YoY) | 12 | + | +0.23 | +0.43 | +0.24 | +0.25 | 81% | 428 | ✅ |
| WTI Crude Oil → CPI Inflation (YoY) | 0 | + | +0.45 | +0.71 | +0.75 | +0.67 | 100% | 440 | ✅ |
| PPI Final Demand (YoY) → CPI Inflation (YoY) | 3 | + | +0.17 | +0.85 | +0.69 | +0.36 | 58% | 175 | ✅ |
| WTI Crude Oil → 5Y Breakeven Inflation | 0 | + | +0.43 | +0.67 | +0.64 | +0.67 | 100% | 274 | ✅ |
| Excess Bond Premium → Industrial Production | 6 | − | -0.08 | -0.47 | -0.34 | -0.10 | 81% | 436 | ✅ |
| Yield Curve (10Y-2Y) → Unemployment Rate | 12 | − | +0.03 | +0.15 | +0.16 | -0.31 | 55% | 428 | ⚪ |
| Copper → Industrial Production | 0 | + | +0.12 | +0.37 | +0.22 | +0.18 | 79% | 442 | ✅ |
| Fed Funds Rate → US Dollar Index (Broad) | 0 | + | -0.18 | +0.04 | +0.16 | +0.05 | 56% | 238 | ⚪ |
| US Dollar Index (Broad) → EUR/USD | 0 | − | -0.82 | -0.86 | -0.84 | -0.91 | 100% | 238 | ✅ |
| US Dollar Index (Broad) → USD/JPY | 0 | + | +0.31 | +0.30 | +0.28 | +0.72 | 100% | 238 | ✅ |
| US Dollar Index (Broad) → Gold | 0 | − | -0.42 | -0.52 | -0.53 | -0.49 | 100% | 238 | ✅ |
| US Dollar Index (Broad) → WTI Crude Oil | 0 | − | -0.42 | -0.65 | -0.54 | +0.20 | 91% | 238 | ✅ |
| US Dollar Index (Broad) → Copper | 0 | − | -0.56 | -0.77 | -0.76 | -0.38 | 100% | 238 | ✅ |
| 10Y Real Yield (TIPS) → Gold | 0 | − | -0.46 | -0.44 | -0.42 | -0.57 | 98% | 274 | ✅ |
| 10Y Real Yield (TIPS) → Bitcoin | 0 | − | -0.06 | -0.31 | -0.22 | -0.21 | 81% | 145 | ✅ |
| Gold → Silver | 0 | + | +0.69 | +0.78 | +0.77 | +0.83 | 99% | 442 | ✅ |
| WTI Crude Oil → Brent Crude Oil | 0 | + | +0.94 | +0.98 | +0.98 | +0.98 | 100% | 442 | ✅ |
| Bitcoin → Ethereum | 0 | + | +0.54 | +0.89 | +0.89 | +0.84 | 100% | 123 | ✅ |

### 목록에 없는 강한 관계 (r 12m 상위 15, 설명 추가 후보)

| A | B | r 12m | n |
|---|---|---|---|
| Nonfarm Payrolls (change) | Employment-Population Ratio | +0.97 | 440 |
| 2Y Treasury Yield | 3M Treasury Bill | +0.89 | 442 |
| Yield Curve (10Y-2Y) | 3M Treasury Bill | -0.81 | 442 |
| Labor Force Participation | Employment-Population Ratio | +0.78 | 440 |
| PPI Final Demand (YoY) | 5Y Breakeven Inflation | +0.75 | 180 |
| Nonfarm Payrolls (change) | Labor Force Participation | +0.75 | 440 |
| 2Y Treasury Yield | Yield Curve (10Y-2Y) | -0.74 | 442 |
| Industrial Production | Job Openings (JOLTS) | +0.72 | 298 |
| 30Y Treasury Yield | 10Y Real Yield (TIPS) | +0.72 | 274 |
| 5Y Breakeven Inflation | Excess Bond Premium | -0.71 | 274 |
| Unemployment Rate | Job Openings (JOLTS) | -0.71 | 297 |
| Industrial Production | Employment-Population Ratio | +0.70 | 440 |
| PPI Final Demand (YoY) | Natural Gas (US) | +0.70 | 180 |
| 5Y Breakeven Inflation | Copper | +0.70 | 274 |
| Industrial Production | Nonfarm Payrolls (change) | +0.70 | 442 |

### 데이터 범위

| 지표 | 출처 | 시작 | 끝 | 개월 수 |
|---|---|---|---|---|
| Fed Funds Rate | Federal Reserve Board H.15 | 1970-01 | 2026-10 | 682 |
| US Dollar Index (Broad) | Federal Reserve Board H.10 | 2006-01 | 2026-10 | 250 |
| 10Y Treasury Yield | Federal Reserve Board H.15 | 1970-01 | 2026-10 | 682 |
| 2Y Treasury Yield | Federal Reserve Board H.15 | 1976-06 | 2026-10 | 605 |
| Yield Curve (10Y-2Y) | Calculated | 1976-06 | 2026-10 | 605 |
| CPI Inflation (YoY) | BLS | 1970-01 | 2026-09 | 680 |
| Unemployment Rate | BLS | 1970-01 | 2026-10 | 681 |
| Gold | World Bank Pink Sheet | 1970-01 | 2026-10 | 682 |
| Bitcoin | Kraken | 2013-10 | 2026-10 | 157 |
| Ethereum | Kraken | 2015-08 | 2026-10 | 135 |
| Industrial Production | Federal Reserve Board G.17 | 1970-01 | 2026-10 | 682 |
| Core CPI (YoY) | BLS | 1970-01 | 2026-09 | 680 |
| PPI Final Demand (YoY) | BLS | 2010-11 | 2026-10 | 192 |
| Wage Growth (YoY) | BLS | 2007-03 | 2026-10 | 236 |
| 5Y Breakeven Inflation | Calculated (H.15) | 2003-01 | 2026-10 | 286 |
| Nonfarm Payrolls (change) | BLS | 1970-01 | 2026-10 | 682 |
| Labor Force Participation | BLS | 1970-01 | 2026-10 | 681 |
| Employment-Population Ratio | BLS | 1970-01 | 2026-10 | 681 |
| Job Openings (JOLTS) | BLS | 2000-12 | 2026-09 | 310 |
| 3M Treasury Bill | Federal Reserve Board H.15 | 1981-09 | 2026-10 | 542 |
| 30Y Treasury Yield | Federal Reserve Board H.15 | 1977-02 | 2026-10 | 597 |
| 10Y Real Yield (TIPS) | Federal Reserve Board H.15 | 2003-01 | 2026-10 | 286 |
| Excess Bond Premium | Federal Reserve Board | 1973-01 | 2026-10 | 646 |
| M2 Money Supply | Federal Reserve Board H.6 | 1970-01 | 2026-09 | 681 |
| Fed Balance Sheet | Federal Reserve Board H.4.1 | 2002-12 | 2026-10 | 287 |
| WTI Crude Oil | World Bank Pink Sheet | 1982-01 | 2026-10 | 538 |
| Brent Crude Oil | World Bank Pink Sheet | 1970-01 | 2026-10 | 682 |
| Natural Gas (US) | World Bank Pink Sheet | 1970-01 | 2026-10 | 682 |
| Copper | World Bank Pink Sheet | 1970-01 | 2026-10 | 682 |
| Silver | World Bank Pink Sheet | 1970-01 | 2026-10 | 682 |
| EUR/USD | Federal Reserve Board H.10 | 1999-01 | 2026-10 | 334 |
| USD/JPY | Federal Reserve Board H.10 | 1971-01 | 2026-10 | 670 |

파일 크기: series.json 103KB, edges.json 748KB, theory.json 58KB

## KR

### 기대 관계 검증

결과: ✅ 8 · 🟡 1 · ⚪ 4 · ❌ 1

- 기간: 1990-01 ~ 2026-10 · 변화량 기준 상관계수 (금리는 차이, 가격은 로그 변화율)
- `r 1m`: 월간 변화끼리 · `r 12m`: 12개월 변화끼리 (경기 흐름에 가까움, 겹치는 구간이라 표본이 실제보다 적은 효과)
- `최근 관계선`: 앱 관계선 기준(3개월 변화 · 60개월 창 · 순위 상관)의 최신값 · `부호 유지율`: 같은 기준의 롤링 창 중 기대 부호와 같은 비율
- 판정 (`r 12m` 기준): ✅ 부호 일치·|r|≥0.3 · 🟡 부호 일치·약함 · ⚪ 거의 0 (|r|<0.15) · ❌ 반대 부호·|r|≥0.15

- `순위 12m`: 12개월 변화의 순위 상관 (극단값 영향 제거). `r 12m`과 차이가 크면 특정 사건(예: 2020년 코로나)이 결과를 좌우한 것

| A → B | 지연 | 기대 | r 1m | r 12m | 순위 12m | 최근 관계선 | 부호 유지율 | n | 판정 |
|---|---|---|---|---|---|---|---|---|---|
| BOK Base Rate → KTB 3Y Yield | 0 | + | +0.27 | +0.53 | +0.55 | +0.42 | 100% | 318 | ✅ |
| KTB 3Y Yield → KTB 10Y Yield | 0 | + | +0.90 | +0.90 | +0.90 | +0.97 | 100% | 301 | ✅ |
| BOK Base Rate → Yield Curve (10Y-3Y) | 0 | − | -0.31 | -0.71 | -0.62 | -0.55 | 100% | 301 | ✅ |
| CPI Inflation (YoY) → BOK Base Rate | 6 | + | +0.01 | +0.14 | +0.18 | +0.50 | 59% | 318 | ⚪ |
| Unemployment Rate → BOK Base Rate | 3 | − | +0.06 | -0.36 | -0.41 | -0.17 | 72% | 314 | ✅ |
| Unemployment Rate → CPI Inflation (YoY) | 12 | − | -0.04 | -0.10 | -0.04 | -0.03 | 50% | 305 | ⚪ |
| Yield Curve (10Y-3Y) → Unemployment Rate | 12 | − | -0.10 | -0.10 | +0.02 | -0.13 | 73% | 289 | ⚪ |
| Fed Funds Rate → BOK Base Rate | 3 | + | +0.26 | +0.65 | +0.54 | +0.50 | 86% | 318 | ✅ |
| 10Y Treasury Yield → KTB 10Y Yield | 0 | + | +0.58 | +0.63 | +0.61 | +0.67 | 100% | 301 | ✅ |
| KR-US Policy Rate Gap → USD/KRW | 0 | − | +0.09 | +0.29 | +0.18 | -0.03 | 43% | 318 | ❌ |
| US Dollar Index (Broad) → USD/KRW | 0 | + | +0.73 | +0.67 | +0.65 | +0.73 | 100% | 238 | ✅ |
| USD/KRW → CPI Inflation (YoY) | 6 | + | -0.08 | -0.06 | -0.11 | +0.00 | 15% | 436 | ⚪ |
| WTI Crude Oil → CPI Inflation (YoY) | 3 | + | +0.06 | +0.30 | +0.32 | +0.30 | 80% | 439 | 🟡 |
| Bitcoin → Ethereum | 0 | + | +0.54 | +0.89 | +0.89 | +0.84 | 100% | 123 | ✅ |

### 목록에 없는 강한 관계 (r 12m 상위 15, 설명 추가 후보)

| A | B | r 12m | n |
|---|---|---|---|
| KR-US Policy Rate Gap | Fed Funds Rate | -0.82 | 318 |
| US Dollar Index (Broad) | WTI Crude Oil | -0.65 | 238 |
| USD/KRW | Bitcoin | -0.63 | 145 |
| USD/KRW | Ethereum | -0.63 | 123 |
| US Dollar Index (Broad) | Bitcoin | -0.62 | 145 |
| US Dollar Index (Broad) | Ethereum | -0.54 | 123 |
| KTB 3Y Yield | CPI Inflation (YoY) | +0.54 | 366 |
| Fed Funds Rate | 10Y Treasury Yield | +0.52 | 442 |
| US Dollar Index (Broad) | Gold | -0.52 | 238 |
| BOK Base Rate | WTI Crude Oil | +0.46 | 318 |
| Yield Curve (10Y-3Y) | Fed Funds Rate | -0.45 | 301 |
| USD/KRW | WTI Crude Oil | -0.44 | 442 |
| Yield Curve (10Y-3Y) | Bitcoin | +0.43 | 145 |
| KR-US Policy Rate Gap | 10Y Treasury Yield | -0.43 | 318 |
| 10Y Treasury Yield | WTI Crude Oil | +0.41 | 442 |

### 데이터 범위

| 지표 | 출처 | 시작 | 끝 | 개월 수 |
|---|---|---|---|---|
| BOK Base Rate | Bank of Korea ECOS | 1999-05 | 2026-10 | 330 |
| USD/KRW | Federal Reserve Board H.10 | 1981-04 | 2026-10 | 547 |
| KTB 10Y Yield | Bank of Korea ECOS | 2000-10 | 2026-10 | 313 |
| KTB 3Y Yield | Bank of Korea ECOS | 1995-05 | 2026-10 | 378 |
| Yield Curve (10Y-3Y) | Calculated | 2000-10 | 2026-10 | 313 |
| CPI Inflation (YoY) | Bank of Korea ECOS | 1970-01 | 2026-10 | 682 |
| Unemployment Rate | Bank of Korea ECOS | 1999-06 | 2026-10 | 329 |
| KR-US Policy Rate Gap | Calculated | 1999-05 | 2026-10 | 330 |
| Fed Funds Rate | Federal Reserve Board H.15 | 1970-01 | 2026-10 | 682 |
| US Dollar Index (Broad) | Federal Reserve Board H.10 | 2006-01 | 2026-10 | 250 |
| 10Y Treasury Yield | Federal Reserve Board H.15 | 1970-01 | 2026-10 | 682 |
| Gold | World Bank Pink Sheet | 1970-01 | 2026-10 | 682 |
| Bitcoin | Kraken | 2013-10 | 2026-10 | 157 |
| Ethereum | Kraken | 2015-08 | 2026-10 | 135 |
| WTI Crude Oil | World Bank Pink Sheet | 1982-01 | 2026-10 | 538 |

파일 크기: series.json 39KB, edges.json 136KB, theory.json 21KB
