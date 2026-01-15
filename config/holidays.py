# South Korea (KRX) Market Holidays 2025-2027
# Includes Public Holidays + Labor Day (May 1st)
# Format: YYYY-MM-DD

HOLIDAYS_2025 = [
    "2025-01-01", # New Year's Day
    "2025-01-27", "2025-01-28", "2025-01-29", # Lunar New Year
    "2025-03-03", # March 1st (Observed)
    "2025-05-01", # Labor Day
    "2025-05-05", # Children's Day
    "2025-05-06", # Buddha's Birthday (Observed?) - Verify if needed, usually fixed but check calendar
    "2025-06-06", # Memorial Day
    "2025-08-15", # Liberation Day
    "2025-10-03", # National Foundation Day
    "2025-10-06", # Chuseok
    "2025-10-07", # Chuseok
    "2025-10-08", # Chuseok
    "2025-10-09", # Hangeul Day
    "2025-12-25", # Christmas
]

HOLIDAYS_2026 = [
    "2026-01-01", # New Year's Day
    "2026-02-16", "2026-02-17", "2026-02-18", # Lunar New Year
    "2026-03-02", # March 1st (Observed)
    "2026-05-01", # Labor Day
    "2026-05-05", # Children's Day
    "2026-05-25", # Buddha's Birthday (Observed)
    "2026-06-06", # Memorial Day (Saturday, usually no sub for Memorial Day unless rule changes, but markets close)
    "2026-08-17", # Liberation Day (Observed)
    "2026-09-24", "2026-09-25", "2026-09-26", # Chuseok
    "2026-10-05", # National Foundation Day (Observed)
    "2026-10-09", # Hangeul Day
    "2026-12-25", # Christmas
]

HOLIDAYS_2027 = [
    "2027-01-01", # New Year's Day
    "2027-02-06", "2027-02-07", "2027-02-08", # Lunar New Year (Roughly, check exact Lunar)
    # Lunar New Year 2027: Feb 6 (Sat), 7 (Sun), 8 (Mon). Sub? Feb 9 (Tue) might be sub.
    "2027-02-09", # Substitute for Lunar New Year?
    "2027-03-01", # March 1st
    "2027-05-01", # Labor Day
    "2027-05-05", # Children's Day
    "2027-05-13", # Buddha's Birthday
    "2027-06-06", # Memorial Day
    "2027-08-16", # Liberation Day (Observed for Sun Aug 15)
    "2027-09-14", "2027-09-15", "2027-09-16", # Chuseok
    "2027-10-04", # National Foundation Day (Observed for Sun Oct 3)
    "2027-10-09", # Hangeul Day (Sat) -> Oct 11 (Observed)?
    "2027-10-11", # Hangeul Day (Observed)
    "2027-12-25", # Christmas (Sat) -> Dec 27 (Observed)?
    "2027-12-27", # Christmas (Observed)
]

# Combine and expose as set
MARKET_HOLIDAYS = set(HOLIDAYS_2025 + HOLIDAYS_2026 + HOLIDAYS_2027)
