"""Canonical processed format. Every time-series loader returns LONG df with COLS; monthly data uses MONTHLY_COLS."""
COLS = ["ts", "site", "meter", "kwh", "kw", "flag", "kwh_raw"]
# ts      : tz-aware Europe/Warsaw, interval START
# site    : hala | d17 | basen | ds18 | akropol
# meter   : PPE id / ZAS1 / ZAS2 / meter id. One site = sum of its meters (no 'total' rows -> no double counting)
# kwh     : cleaned energy in interval ; kw : mean power (= kwh * 60/minutes)
# flag    : see FLAGS ; kwh_raw : value as delivered (NaN if absent) -> before/after anomaly plots
FLAGS = ["ok", "interp", "gapfill", "split", "anomaly", "suspect", "missing"]
# ok measured | interp short gap/bad value linear | gapfill long gap: counter spread or weekday profile
# split combined reading divided | anomaly rejected measured value, replaced | suspect kept, questionable | missing NaN
SITES = ["hala", "d17", "basen", "ds18", "akropol"]

MONTHLY_COLS = ["month", "site", "carrier", "meter", "value", "unit", "flag", "value_raw", "note"]
# month   : Timestamp first day of month (naive) ; site: ds01..ds19 | alfa
# carrier : el | heat ; meter: el D|N|total(alfa) ; heat co|cw|ct|total (total only where co/cw not split)
# unit    : kWh (el) | GJ (heat)
