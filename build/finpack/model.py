"""Month-by-month cash contribution model for Resondi's commercial operation.

Single source of truth for every recovery figure in the concept note, the
business model canvas and Figure 12. Assumptions match the note's wording:
  - device margin of P4,000 is received in the month a facility is acquired
  - the P900 monthly contribution begins the month AFTER acquisition
    ("P4,000 on acquisition and P900 per month thereafter")
  - Year 1: ten facilities, one a month, months 1-10
  - Year 2: fifteen new facilities across months 13-24 (25 in total)
  - school licences contribute P25,800 a year, paid annually in advance;
    Year 1 schools sign in months 2, 4, 6; Year 2 renewals fall on their
    anniversaries (14, 16, 18) and four new schools sign in 15, 17, 19, 21
Commercial month 1 = month 15 of the implementation plan.
"""
DEV, SUB, LIC = 4_000, 900, 25_800
OFFSET = 14                      # commercial month m = funding month m + 14

new_fac = {m: 1 for m in range(1, 11)}
for m in range(13, 25):
    new_fac[m] = 1
for m in (13, 17, 21):
    new_fac[m] += 1
# Year 3: 25 more facilities, reaching the 50-facility obtainable market
for m in range(25, 37):
    new_fac[m] = new_fac.get(m, 0) + 2
new_fac[25] += 1
schools = {2: 1, 4: 1, 6: 1, 14: 1, 15: 1, 16: 1, 17: 1, 18: 1, 19: 1, 21: 1}
# Year 3: 7 renewals on their anniversaries + 8 new, reaching 15 institutions
for m in (26, 27, 28, 29, 30, 31, 33):
    schools[m] = schools.get(m, 0) + 1
for m in (25, 26, 28, 30, 32, 33, 34, 35):
    schools[m] = schools.get(m, 0) + 1

assert sum(v for m, v in new_fac.items() if m <= 12) == 10
assert sum(v for m, v in new_fac.items() if m <= 24) == 25
assert sum(new_fac.values()) == 50
assert sum(v for m, v in schools.items() if m <= 12) == 3
assert sum(v for m, v in schools.items() if 12 < m <= 24) == 7
assert sum(v for m, v in schools.items() if m > 24) == 15

def run(months=24):
    rows, cum, acquired = [], 0, 0
    for m in range(1, months + 1):
        billing = acquired                      # acquired before this month
        n = new_fac.get(m, 0)
        dev, sub, lic = n * DEV, billing * SUB, schools.get(m, 0) * LIC
        cash = dev + sub + lic
        cum += cash
        acquired += n
        rows.append(dict(m=m, new=n, base=acquired, dev=dev, sub=sub, lic=lic,
                         cash=cash, cum=cum))
    return rows

def crossing(rows, target):
    for r in rows:
        if r["cum"] >= target:
            return r["m"]
    return None

ROWS = run(36)
Y1 = ROWS[11]["cum"]
Y2 = ROWS[23]["cum"] - Y1
Y3 = ROWS[35]["cum"] - ROWS[23]["cum"]
CUM24 = ROWS[23]["cum"]
CUM36 = ROWS[35]["cum"]
X500 = crossing(ROWS, 500_000)
X300 = crossing(ROWS, 300_000)

# Investor repayment: 40% of NET earnings until P500,000 is returned.
# Net = contribution less operating overhead. Overhead is not yet costed, so the
# repayment month is reported across a band of assumptions rather than as one figure.
INVESTOR_SHARE = 0.40
SEED = 500_000

def investor_month(overhead):
    """Commercial month in which the investor's 40% share has returned the seed."""
    paid = 0.0
    for r in ROWS:
        paid += r["cash"] * (1 - overhead) * INVESTOR_SHARE
        if paid >= SEED:
            return r["m"]
    return None

if __name__ == "__main__":
    for r in ROWS:
        print(f"m{r['m']:>2}  new={r['new']}  base={r['base']:>2}  dev={r['dev']:>6,}  "
              f"sub={r['sub']:>6,}  lic={r['lic']:>6,}  cash={r['cash']:>7,}  cum={r['cum']:>8,}")
    print()
    print(f"Year 1 cash          : {Y1:,}")
    print(f"Year 2 cash          : {Y2:,}")
    print(f"Cumulative, month 24 : {CUM24:,}")
    print(f"Year 3 cash          : {Y3:,}")
    print(f"Cumulative, month 36 : {CUM36:,}")
    print(f"P500,000 crossed     : commercial month {X500}  (funding month {X500 + OFFSET})")
    print(f"P300,000 crossed     : commercial month {X300}  (funding month {X300 + OFFSET})")
    print()
    print("Investor repayment (40% of net until P500,000 returns):")
    for oh in (0.00, 0.15, 0.25, 0.35):
        m = investor_month(oh)
        if m:
            print(f"  overhead {oh:>4.0%}: commercial month {m:>2}  (funding month {m + OFFSET})")
        else:
            print(f"  overhead {oh:>4.0%}: not repaid within 36 commercial months")
