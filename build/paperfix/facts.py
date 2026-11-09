"""Verified values for the paper revision pack (CLAUDE.md Part A5 and A7).

Every number the pack prints comes from here, and the statistics are recomputed
and checked against the figures the handoff states.
"""
from math import comb, sqrt

SIGNAL = (45, 32)                                     # dB: Resondi, conventional
NOISE = {"Quiet room": 24, "Hospital ward": 35, "Community area": 42}   # dB
CLARITY = (68, 25, 7)                                 # % good / acceptable / poor
RESPONSE = {                                          # Table 5: mean s, SD s
    "Smart-stethoscope connection": (4.55, 0.83),
    "Sound recording": (15.00, 0.00),
    "Recording-quality assessment": (144.68, 28.94),
    "Signal preprocessing": (20.91, 4.18),
    "Classification output": (3.97, 0.87),
}
AGREE = (6, 15)
CHANCE = 0.25

UTAUT = [  # construct, items, mean, SD, alpha (None where one item)
    ("Performance expectancy", 3, 4.09, 0.59, 0.51),
    ("Effort expectancy", 3, 4.09, 0.60, 0.76),
    ("Facilitating conditions", 5, 3.84, 0.61, 0.59),
    ("Social influence", 1, 3.63, 1.21, None),
]
UTAUT_OVERALL = 3.95
N_RESP = 27


def wilson(k, n, z=1.959964):
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centre - half, centre + half


def binom_upper(k, n, p):
    """One-sided exact binomial P(X >= k)."""
    return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def needed_for_significance(n, p, alpha=0.05):
    return next(k for k in range(n + 1) if binom_upper(k, n, p) < alpha)


LO, HI = wilson(*AGREE)
P_CHANCE = binom_upper(AGREE[0], AGREE[1], CHANCE)
K_NEEDED = needed_for_significance(AGREE[1], CHANCE)
TOTAL_TIME = sum(m for m, _ in RESPONSE.values())
QA_SHARE = RESPONSE["Recording-quality assessment"][0] / TOTAL_TIME
AMP_RATIO = 10 ** ((SIGNAL[0] - SIGNAL[1]) / 20)

# The handoff's stated values; fail loudly if the arithmetic disagrees.
assert (round(LO * 100, 1), round(HI * 100, 1)) == (19.8, 64.3), (LO, HI)
assert round(P_CHANCE, 3) == 0.148, P_CHANCE
assert K_NEEDED == 8, K_NEEDED
assert round(AMP_RATIO, 1) == 4.5, AMP_RATIO
assert sum(CLARITY) == 100
