"""Indicator registry and expected relationships for the prototype.

transform = how a monthly *change* is computed for correlation:
  bp   : level difference (rates, in percentage points)
  diff : level difference (ratios already in %, indexes like EBP)
  pct  : percent change (prices, quantities)
  flow : the value itself is already a change (e.g. payroll change); 12m change = 12m sum
"""

# ---- raw series to download -------------------------------------------------------------
FED = {
    "H15": ["RIFSPFF_N.M", "RIFLGFCM03_N.M", "RIFLGFCY02_N.M", "RIFLGFCY05_N.M", "RIFLGFCY10_N.M",
            "RIFLGFCY30_N.M", "RIFLGFCY05_XII_N.M", "RIFLGFCY10_XII_N.M"],
    "H10": ["JRXWTFB_N.M", "RXI$US_N.M.EU", "RXI_N.M.JA", "RXI_N.M.KO"],
    "H6": ["M2.M"],
    "G17": ["IP.B50001.S"],
    "H41": ["RESPPA_N.WW"],
}
BLS = ["CUUR0000SA0", "CUUR0000SA0L1E", "WPUFD4", "CES0500000003", "LNS14000000",
       "CES0000000001", "LNS11300000", "LNS12300000", "JTS000000000000000JOL"]
PINK = {"gold": "Gold", "silver": "Silver", "copper": "Copper",
        "wti": "Crude oil, WTI", "brent": "Crude oil, Brent", "natgas": "Natural gas, US"}
KRAKEN = {"btc": "XBTUSD", "eth": "ETHUSD"}
ECOS = {
    "kr_base": ("722Y001", "0101000"),
    "kr_ktb3": ("721Y001", "5020000"),
    "kr_ktb10": ("721Y001", "5050000"),
    "kr_cpi_idx": ("901Y009", "0"),
    "kr_unemp": ("901Y027", "I61BC", "I28B"),  # seasonally adjusted
}

# ---- indicators -------------------------------------------------------------------------
# (id, display name, unit, source label, transform, recipe)
# recipe: ("raw", key) | ("yoy", key) | ("spread", a, b) | ("mdiff", key)
US = [
    ("fed_funds", "Fed Funds Rate", "%", "Federal Reserve Board H.15", "bp", ("raw", "RIFSPFF_N.M")),
    ("usd_broad", "US Dollar Index (Broad)", "index", "Federal Reserve Board H.10", "pct", ("raw", "JRXWTFB_N.M")),
    ("ust10y", "10Y Treasury Yield", "%", "Federal Reserve Board H.15", "bp", ("raw", "RIFLGFCY10_N.M")),
    ("ust2y", "2Y Treasury Yield", "%", "Federal Reserve Board H.15", "bp", ("raw", "RIFLGFCY02_N.M")),
    ("curve_10y2y", "Yield Curve (10Y-2Y)", "pp", "Calculated", "bp", ("spread", "RIFLGFCY10_N.M", "RIFLGFCY02_N.M")),
    ("cpi_yoy", "CPI Inflation (YoY)", "%", "BLS", "diff", ("yoy", "CUUR0000SA0")),
    ("unemployment", "Unemployment Rate", "%", "BLS", "diff", ("raw", "LNS14000000")),
    ("gold", "Gold", "USD/oz", "World Bank Pink Sheet", "pct", ("raw", "gold")),
    ("btc", "Bitcoin", "USD", "Kraken", "pct", ("raw", "btc")),
    ("eth", "Ethereum", "USD", "Kraken", "pct", ("raw", "eth")),
    ("ip", "Industrial Production", "index", "Federal Reserve Board G.17", "pct", ("raw", "IP.B50001.S")),
    ("core_cpi_yoy", "Core CPI (YoY)", "%", "BLS", "diff", ("yoy", "CUUR0000SA0L1E")),
    ("ppi_yoy", "PPI Final Demand (YoY)", "%", "BLS", "diff", ("yoy", "WPUFD4")),
    ("wage_yoy", "Wage Growth (YoY)", "%", "BLS", "diff", ("yoy", "CES0500000003")),
    ("breakeven_5y", "5Y Breakeven Inflation", "pp", "Calculated (H.15)", "bp", ("spread", "RIFLGFCY05_N.M", "RIFLGFCY05_XII_N.M")),
    ("payrolls_chg", "Nonfarm Payrolls (change)", "thousand", "BLS", "flow", ("mdiff", "CES0000000001")),
    ("lfpr", "Labor Force Participation", "%", "BLS", "diff", ("raw", "LNS11300000")),
    ("epop", "Employment-Population Ratio", "%", "BLS", "diff", ("raw", "LNS12300000")),
    ("job_openings", "Job Openings (JOLTS)", "thousand", "BLS", "pct", ("raw", "JTS000000000000000JOL")),
    ("tbill3m", "3M Treasury Bill", "%", "Federal Reserve Board H.15", "bp", ("raw", "RIFLGFCM03_N.M")),
    ("ust30y", "30Y Treasury Yield", "%", "Federal Reserve Board H.15", "bp", ("raw", "RIFLGFCY30_N.M")),
    ("real10y", "10Y Real Yield (TIPS)", "%", "Federal Reserve Board H.15", "bp", ("raw", "RIFLGFCY10_XII_N.M")),
    ("ebp", "Excess Bond Premium", "pp", "Federal Reserve Board", "diff", ("raw", "ebp")),
    ("m2", "M2 Money Supply", "USD bn", "Federal Reserve Board H.6", "pct", ("raw", "M2.M")),
    ("fed_assets", "Fed Balance Sheet", "USD mn", "Federal Reserve Board H.4.1", "pct", ("raw", "RESPPA_N.WW")),
    ("wti", "WTI Crude Oil", "USD/bbl", "World Bank Pink Sheet", "pct", ("raw", "wti")),
    ("brent", "Brent Crude Oil", "USD/bbl", "World Bank Pink Sheet", "pct", ("raw", "brent")),
    ("natgas", "Natural Gas (US)", "USD/mmbtu", "World Bank Pink Sheet", "pct", ("raw", "natgas")),
    ("copper", "Copper", "USD/mt", "World Bank Pink Sheet", "pct", ("raw", "copper")),
    ("silver", "Silver", "USD/oz", "World Bank Pink Sheet", "pct", ("raw", "silver")),
    ("eurusd", "EUR/USD", "USD per EUR", "Federal Reserve Board H.10", "pct", ("raw", "RXI$US_N.M.EU")),
    ("usdjpy", "USD/JPY", "JPY per USD", "Federal Reserve Board H.10", "pct", ("raw", "RXI_N.M.JA")),
]

KR = [
    ("kr_base", "BOK Base Rate", "%", "Bank of Korea ECOS", "bp", ("raw", "kr_base")),
    ("usdkrw", "USD/KRW", "KRW per USD", "Federal Reserve Board H.10", "pct", ("raw", "RXI_N.M.KO")),
    ("kr_ktb10", "KTB 10Y Yield", "%", "Bank of Korea ECOS", "bp", ("raw", "kr_ktb10")),
    ("kr_ktb3", "KTB 3Y Yield", "%", "Bank of Korea ECOS", "bp", ("raw", "kr_ktb3")),
    ("kr_curve", "Yield Curve (10Y-3Y)", "pp", "Calculated", "bp", ("spread", "kr_ktb10", "kr_ktb3")),
    ("kr_cpi_yoy", "CPI Inflation (YoY)", "%", "Bank of Korea ECOS", "diff", ("yoy", "kr_cpi_idx")),
    ("kr_unemp", "Unemployment Rate", "%", "Bank of Korea ECOS", "diff", ("raw", "kr_unemp")),
    ("kr_us_gap", "KR-US Policy Rate Gap", "pp", "Calculated", "bp", ("spread", "kr_base", "RIFSPFF_N.M")),
]
# global nodes shown on the Korea graph as well
KR_SHARED = ["gold", "btc", "eth", "wti", "usd_broad", "ust10y", "fed_funds"]

# ---- textbook relationships ------------------------------------------------------------
# (A, B, expected sign, lag): B is measured `lag` months after A. These are the theory baseline the
# app always draws; the data only says how strongly each one holds in a given era (rolling window).
# Concept names and explanations live in the app repository (shared/catalog.json, key "A|B").
PAIRS_US = [
    # monetary policy and the yield curve
    ("fed_funds", "ust2y", +1, 0),          # expectations hypothesis
    ("fed_funds", "tbill3m", +1, 0),        # money-market arbitrage
    ("ust2y", "ust10y", +1, 0),             # term structure
    ("ust10y", "ust30y", +1, 0),            # term structure
    ("fed_funds", "curve_10y2y", -1, 0),    # tightening flattens the curve
    ("cpi_yoy", "fed_funds", +1, 6),        # Taylor rule (inflation gap)
    ("core_cpi_yoy", "fed_funds", +1, 6),   # Taylor rule (core)
    ("unemployment", "fed_funds", -1, 3),   # Taylor rule (output gap)
    ("fed_assets", "real10y", -1, 0),       # QE lowers term premia
    # Fisher equation
    ("real10y", "ust10y", +1, 0),
    ("breakeven_5y", "ust10y", +1, 0),
    # labour market
    ("ip", "unemployment", -1, 0),          # Okun's law
    ("payrolls_chg", "unemployment", -1, 0),
    ("epop", "unemployment", -1, 0),
    ("unemployment", "wage_yoy", -1, 6),    # wage Phillips curve
    ("job_openings", "wage_yoy", +1, 0),    # labour-market tightness
    ("unemployment", "cpi_yoy", -1, 12),    # Phillips curve
    # inflation
    ("m2", "cpi_yoy", +1, 12),              # quantity theory of money
    ("wti", "cpi_yoy", +1, 0),              # cost-push (energy)
    ("ppi_yoy", "cpi_yoy", +1, 3),          # producer-to-consumer pass-through
    ("wti", "breakeven_5y", +1, 0),         # energy and inflation expectations
    # credit and the cycle
    ("ebp", "ip", -1, 6),                   # financial accelerator
    ("curve_10y2y", "unemployment", -1, 12),  # yield-curve recession signal
    ("copper", "ip", +1, 0),                # industrial demand
    # dollar, commodities and assets
    ("fed_funds", "usd_broad", +1, 0),      # interest-rate parity
    ("usd_broad", "eurusd", -1, 0),         # definition
    ("usd_broad", "usdjpy", +1, 0),         # definition
    ("usd_broad", "gold", -1, 0),           # dollar pricing of commodities
    ("usd_broad", "wti", -1, 0),
    ("usd_broad", "copper", -1, 0),
    ("real10y", "gold", -1, 0),             # opportunity cost of holding gold
    ("real10y", "btc", -1, 0),              # discount rate and risk assets
    ("gold", "silver", +1, 0),              # precious-metal substitutes
    ("wti", "brent", +1, 0),                # same commodity
    ("btc", "eth", +1, 0),                  # same asset class
]
PAIRS_KR = [
    ("kr_base", "kr_ktb3", +1, 0),          # expectations hypothesis
    ("kr_ktb3", "kr_ktb10", +1, 0),         # term structure
    ("kr_base", "kr_curve", -1, 0),         # tightening flattens the curve
    ("kr_cpi_yoy", "kr_base", +1, 6),       # Taylor rule (inflation gap)
    ("kr_unemp", "kr_base", -1, 3),         # Taylor rule (output gap)
    ("kr_unemp", "kr_cpi_yoy", -1, 12),     # Phillips curve
    ("kr_curve", "kr_unemp", -1, 12),       # yield-curve recession signal
    ("fed_funds", "kr_base", +1, 3),        # policy spillover
    ("ust10y", "kr_ktb10", +1, 0),          # global bond-market integration
    ("kr_us_gap", "usdkrw", -1, 0),         # interest-rate parity
    ("usd_broad", "usdkrw", +1, 0),         # global dollar cycle
    ("usdkrw", "kr_cpi_yoy", +1, 6),        # import-price pass-through
    ("wti", "kr_cpi_yoy", +1, 3),           # cost-push (imported energy)
    ("btc", "eth", +1, 0),
]
