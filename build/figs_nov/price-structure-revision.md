# Revised price structure — paste-ready

**Bill of materials confirmed at ₱2,735.00.** Prices and margins are unchanged. What changes is that the cost build-up now traces to that figure instead of stopping at an unexplained ₱3,400 component line.

---

## The build-up

| | |
|---|---|
| Bill of materials, one unit — **confirmed** | **₱2,735** |
| + Battery protection, charging, and production allowance | ₱665 |
| **= Components, production unit** | **₱3,400** |
| + Assembly, calibration, functional test, packaging | ₱600 |
| **= Fully loaded unit cost** | **₱4,000** |

Selling price ₱8,000 → **₱4,000 margin on the first production unit, about 50%.**

At volume: ~₱3,000 at 100 units (silicone vacuum-cast enclosures, batch PCB, bulk pricing); ~₱2,500 at 500 units via contract assembly.

### What the ₱665 covers

Your bill of materials states that **battery protection and a compatible charging solution are not included in the current total.** On top of that, a unit built to sell needs what a bench prototype does not: connectors and strain relief, a finished enclosure rather than a raw print, and a spares allowance for units damaged in assembly.

**One number to confirm:** the battery protection and charging portion. A TP4056-class charging module plus a small BMS board should sit comfortably inside ₱300 at Philippine retail, which leaves ₱365 for the rest. If your supplier quotes materially above ₱300, the ₱4,000 figure needs revisiting before the ₱8,000 price does.

---

## Paste-ready replacements for the concept note

### 1. FINANCIAL REQUIREMENT — unit cost sentence

**Find:**

> The fully loaded cost of one production unit, once the design is frozen, is approximately ₱4,000: about ₱3,400 of components plus assembly, calibration and packaging.

**Replace with:**

> The fully loaded cost of one production unit, once the design is frozen, is approximately ₱4,000. The bill of materials for a single unit totals ₱2,735 (Malimban, 2026) and states that battery protection and a charging circuit are not included in that total; adding those, together with the connectors, strain relief, finished enclosure and spares allowance a saleable unit requires beyond a prototype, brings components to approximately ₱3,400. Assembly, calibration, functional test and packaging account for the remaining ₱600.

### 2. PRODUCTION WORKING CAPITAL

**Find:**

> The ₱40,000 production working capital allocation is separate, and buys the first batch of ten saleable units at approximately ₱4,000 each fully loaded: ₱3,400 of components once the design is frozen, plus assembly, calibration and packaging.

**Replace with:**

> The ₱40,000 production working capital allocation is separate, and buys the first batch of ten saleable units at approximately ₱4,000 each fully loaded: ₱3,400 of components once the design is frozen — the ₱2,735 bill of materials plus battery protection, charging and the production allowance — together with assembly, calibration, functional test and packaging.

### 3. Business model canvas, cost structure block

**Find:**

> UNIT COST: ~₱4,000 fully loaded (₱3,400 of components plus assembly); ~₱3,000 at 100 units, ~₱2,500 at 500

**Replace with:**

> UNIT COST: ~₱4,000 fully loaded — ₱2,735 bill of materials, ₱665 battery protection, charging and production allowance, ₱600 assembly and test; ~₱3,000 at 100 units, ~₱2,500 at 500

(Edit `deckfigs/build.py`, the `Cost Structure` block, then rebuild Figure 8.)

---

## What does not change

Nothing downstream. ₱4,000 fully loaded, ₱4,000 device margin per facility, ₱40,000 for ten units, and every revenue figure in `finpack/model.py` stay exactly as they are. This revision makes the ₱4,000 **traceable**, it does not move it.

---

## The alternative, and why I would not take it

You could instead restate components as ~₱3,000 (₱2,735 + ~₱265 for battery protection and charging only), giving a fully loaded cost of ~₱3,600 and a margin of ₱4,400, or **55%**.

It is arguably tighter to the bill of materials. But it would require recomputing `finpack/model.py` and every figure, table and slide that imports it — Y1 and Y2 cash, the payback month, Figure 12, the deck's slide 14 — days before nationals, to make your margin look *better*. A reviewer does not penalise a conservative cost estimate; they penalise one that does not reconcile. Keeping ₱4,000 and showing the bridge solves the real problem.

---

## Still separate: the paper's ₱2,094.47

The 83-page paper reports ₱2,094.47 for the prototype actually tested. That is an earlier, different build. Both figures can be true, but the two documents should say so. One line in the paper revision pack resolves it:

> An earlier parts receipt for the first research prototype totalled ₱2,094.47. The bill of materials reported here, at ₱2,735.00, covers the current build, which adds the printed circuit board, the internal battery and the printed enclosure.
