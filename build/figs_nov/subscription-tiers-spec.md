# Resondi subscription tiers — implementation spec

**Status: proposed, not validated.** These prices are a design, not something a buyer has agreed to. See "Before you commit to these" at the end.

`ESSENTIAL` is the existing ₱1,500 offering, unchanged. Nothing in the financial model is re-cut: ₱1,500 × facilities remains the floor, and the two tiers above it only add. Schools keep the separate ₱30,000 annual teaching licence — it is a different product and is not part of this ladder.

---

## The three tiers

| | Essential | Clinical | Network |
|---|---|---|---|
| Price per facility per month | **₱1,500** | **₱2,900** | **₱4,500** |
| Minimum facilities | 1 | 1 | 3 |
| Cloud allowance | ₱350 | ₱450 | ₱600 |
| Service and replacement reserve | ₱250 | ₱250 | ₱250 |
| Review operations | — | — | ₱350 |
| **Contribution** | **₱900** | **₱2,200** | **₱3,300** |
| Available | now | after the funded build | after the funded build |

Contribution per facility per year: ₱10,800 / ₱26,400 / ₱39,600.

---

## Feature flags

Suggested flag names for the app. Everything in `core` is on for all tiers.

```js
const TIERS = {
  essential: {
    price: 1500, minFacilities: 1, devices: 1, users: 2,
    supportSla: 'next_business_day',
    features: [...CORE],
  },
  clinical: {
    price: 2900, minFacilities: 1, devices: 3, users: 8,
    supportSla: 'same_business_day',
    features: [...CORE,
      'rehab_module',            // practitioner-released exercises
      'rbac_audit',              // role-based access + audit log
      'facility_report_monthly', // PDF for the health officer
    ],
  },
  network: {
    price: 4500, minFacilities: 3, devices: 5, users: Infinity,
    supportSla: 'same_day_named_contact',
    features: [...CORE,
      'rehab_module', 'rbac_audit',
      'facility_report_monthly',
      'cross_facility_routing',  // send a capture to a remote clinician
      'cluster_dashboard',       // MHO view across facilities
      'data_export',             // DOH / LGU reporting
      'quarterly_clinical_review',
      'annual_refresher_training',
    ],
  },
};

const CORE = [
  'guided_capture',        // seven lung sites, five heart points
  'quality_check',         // runs before analysis
  'ai_classification',     // four lung sound patterns
  'site_tagged_storage',
  'offline_capture',       // store-and-forward on MicroSD
  'practitioner_review',   // confirm / modify / reject
  'longitudinal_compare',  // same-site comparison across visits; in CORE by decision (2 Nov), ships with the funded build
  'cloud_backup',
  'model_updates',
  'device_replacement_reserve',
];
```

### Gating notes

- **Gate at the facility, not the user.** A facility's tier governs every account under it; `devices` and `users` are per facility.
- **`network` is a cluster-level subscription.** Enforce `minFacilities: 3` at the account, and bill per facility within it. `cluster_dashboard` and `cross_facility_routing` need a cluster entity above the facility in the data model — that is the only schema change the ladder requires.
- **Never gate anything safety-related.** `quality_check` and `practitioner_review` stay in `CORE` on every tier. A cheaper plan must not mean a less-reviewed result.
- **Downgrade behaviour:** data captured under a higher tier stays readable. If a facility drops to `essential`, hide the rehabilitation module and monthly reports, do not delete the history. The longitudinal view stays: it is in `CORE`.
- **Longitudinal comparison is never gated.** It is the headline of the pitch and the projections model every facility on Essential, so it sits in `CORE` (user decision, 2 Nov).

---

## Where the funded app features sit

Not arbitrary — each is a line already funded in Table 15's ₱38,000 mobile-application budget. `longitudinal_compare` is funded there too but sits in Essential, deliberately:

| Feature | Funded line |
|---|---|
| `rbac_audit` | Role-based access control and audit logging — ₱8,000 |
| Practitioner dashboard behind `cross_facility_routing` | Practitioner dashboard and review workflow — ₱9,000 |
| `offline_capture` hardening | Offline capture and synchronisation — ₱7,000 |
| `longitudinal_compare` (Essential, in `CORE`) | Longitudinal comparison views — ₱7,000 |

So the pricing ladder and the funding ask describe the same build. That is a useful thing to be able to say to a judge: *the tiers above Essential are exactly what the ₱38,000 pays for.*

---

## What this does to the projections

The current model assumes every facility pays ₱1,500. If any facility takes a higher tier, contribution rises; it cannot fall. Two ways to handle it:

1. **Leave the projections alone.** Keep modelling every facility at Essential and describe the ladder as upside. Conservative, defensible, nothing to recompute.
2. **Model a mix.** For example 70% Essential / 25% Clinical / 5% Network gives a blended ₱1,440 contribution per facility per month against ₱900 today — a 60% increase. If you do this, `finpack/model.py` is the only place to change it, and every figure and table that imports it updates together.

**Recommendation: option 1 for the PSC submission.** You have ten facilities in commercial Year 1; a tier mix assumption at that scale is guesswork, and a judge can see that. Present the ladder as how pricing scales once the product does.

---

## Bundles

A facility buying a device and a subscription in the same procurement is making one decision, not two, and an LGU budget line is easier to defend as a single annual figure than as a capital purchase plus a recurring charge.

**One rule governs every discount: nothing comes out of the ₱600 per facility per month that pays cloud operation and the device replacement reserve.**

That rule has a consequence worth understanding before you change any number here. On Essential the contribution is *exactly* the ₱900 the projections assume, so there is no headroom — an Essential discount must come out of device margin, and the subscription is charged in full. On Clinical and Network the contribution is ₱2,200 and ₱3,300, so part of the discount can come out of the subscription and still clear ₱900 comfortably.

| Bundle | Tier | Contents | Separately | Bundle | Discount comes from | Contribution retained |
|---|---|---|---|---|---|---|
| **Starter** | Essential | 1 device, 12 months prepaid | ₱26,000 | **₱24,500** | ₱1,500 off the device | ₱900/mo; device margin ₱2,500 (38%) |
| **Clinic** | Clinical | 3 devices, 12 months prepaid | ₱58,800 | **₱52,000** | ₱3,000 devices + ₱3,800 subscription | ₱1,883/mo |
| **Cluster** | Network | 3 facilities × 1 device, 12 months prepaid | ₱186,000 | **₱168,000** | ₱4,500 devices + ₱13,500 subscription | ₱2,925/facility/mo |
| **Teaching** | Schools | Institutional licence + 2 devices | ₱46,000 | **₱42,000** | ₱4,000 off the devices | Licence intact at ₱30,000 |

### Implementation notes

- **Bundles are prepaid, and prepayment is the thing being discounted.** Enforce the full 12 months up front; a bundle that can be cancelled in month 3 is just a discount.
- **Store the device discount and the subscription discount separately.** The ₱900 floor check is on the subscription component alone, and you cannot run that check if the two are merged into one bundle price in the database.
- **Cluster needs the cluster entity** above facility in the data model — the same schema change `network` already requires. It is the only one.
- **Teaching does not join the tier ladder.** The school licence is a different product with different access (cohort accounts, no patient records); do not let a school account be assigned a facility tier.

---

## Onboarding offers

| Offer | Who | What it costs the model |
|---|---|---|
| **First month free** | Any new facility on Essential, month to month | **Nothing.** `model.py` already starts the monthly contribution in the month *after* acquisition (`billing = acquired`, counted before the current month). The acquisition month was never billed in the projections, so the free month is already in the ₱175,900 Year 1 figure. The ₱4,000 device margin is still received on acquisition. |
| **Clinical free for 60 days** | Any new deployment, before it chooses a tier | ₱100/month of extra cloud allowance for two months — **₱200 per facility, once.** |

**Offers do not stack.** A facility takes either the free first month on a month-to-month subscription or a prepaid bundle, never both. Enforce this at the account, not in the UI copy.

```js
const BUNDLES = {
  starter:  { tier: 'essential', devices: 1, months: 12, price: 24500,
              deviceDiscount: 1500, subscriptionDiscount: 0 },
  clinic:   { tier: 'clinical',  devices: 3, months: 12, price: 52000,
              deviceDiscount: 3000, subscriptionDiscount: 3800 },
  cluster:  { tier: 'network',   devices: 3, months: 12, price: 168000,
              facilities: 3, deviceDiscount: 4500, subscriptionDiscount: 13500 },
  teaching: { tier: 'education', devices: 2, months: 12, price: 42000,
              deviceDiscount: 4000, subscriptionDiscount: 0 },
};

const OFFERS = {
  firstMonthFree: { tiers: ['essential'], months: 1, newAccountsOnly: true },
  clinicalTrial:  { tier: 'clinical', days: 60, newDeploymentsOnly: true,
                    onExpiry: 'prompt_tier_choice' },   // never auto-charge
};

// The one invariant worth asserting in code.
const FLOOR = 900;
function contributionAfterDiscount(tier, bundle) {
  const months = bundle?.months ?? 1;
  const gross  = TIERS[tier].price * months - (bundle?.subscriptionDiscount ?? 0);
  const cost   = (CLOUD[tier] + RESERVE + (REVIEW_OPS[tier] ?? 0)) * months;
  return (gross - cost) / months;          // must be >= FLOOR
}
```

`onExpiry: 'prompt_tier_choice'` matters: a trial that silently rolls into a paid tier is the single fastest way to lose a rural health unit's trust, and you will not get it back.

---

## What none of this changes

The projections still model every facility at Essential and at the full ₱1,500. That is deliberate, and it is the conservative choice: the ladder and the bundles can only raise contribution above ₱900, never below it, because the floor check above refuses any configuration that would. Nothing in `finpack/model.py` needs to change, and no figure that imports it needs regenerating.

---

## Before you commit to these

These numbers are invented to a sensible shape. Nobody has said they would pay ₱2,900, and that is the same gap as the rest of the commercial section — there is no willingness-to-pay evidence anywhere in the concept note.

The ladder is cheap to test. When you ask the five to ten budget-holders the pricing questions, add one:

> At ₱1,500 a month you get capture, AI, review and comparison against the patient's last visit. For ₱2,900 you also get the rehabilitation module, role-based access and a monthly report. Which would your facility choose, and why?

Ten answers would turn this from a proposal into a priced product with evidence behind it — and the answers tell you whether the gap between tiers is too wide, too narrow, or in the wrong place.
