# ICBHI + SPRSound fusion round: test results (2026-11-12 00:25)

Primary, pre-specified before any test read: **fdc3 seed 33** (results/prespec-icbhi-sprs-round.md).
Scored from the saved models, without retraining. Other rows are for comparison only.

## ICBHI test: 31 patients, 1051 cycles/events

PRIMARY fdc3 seed 33, cycle level
=================================
items: 1051
accuracy: 0.472   (always guessing the commonest class scores 0.528)
balanced accuracy: 0.394   macro F1: 0.383

class                    support  precision  recall  specif.     F1
Crackles                     268      0.403   0.567    0.713  0.471
Healthy                      555      0.667   0.519    0.710  0.584
Wheezing                     120      0.234   0.242    0.898  0.238
Wheezing with Crackles       108      0.229   0.250    0.903  0.239

confusion matrix (rows = true, columns = predicted)
                            Crackles     Healthy    Wheezing  Wheezing w
Crackles                         152          83          14          19
Healthy                          175         288          44          48
Wheezing                          26          41          29          24
Wheezing with Crackles            24          20          37          27

## SPRS test: 230 patients, 3643 cycles/events

PRIMARY fdc3 seed 33, cycle level
=================================
items: 3643
accuracy: 0.662   (always guessing the commonest class scores 0.773)
balanced accuracy: 0.572   macro F1: 0.454

class                    support  precision  recall  specif.     F1
Crackles                     556      0.320   0.531    0.797  0.399
Healthy                     2816      0.913   0.699    0.774  0.792
Wheezing                     226      0.429   0.549    0.952  0.482
Wheezing with Crackles        45      0.083   0.511    0.929  0.143

confusion matrix (rows = true, columns = predicted)
                            Crackles     Healthy    Wheezing  Wheezing w
Crackles                         295         170          25          66
Healthy                          586        1968         135         127
Wheezing                          29          12         124          61
Wheezing with Crackles            12           5           5          23

## All versions

```
icbhi  fdc3 (PRIMARY)           seed 33  balanced 0.394  F1 0.383  Crac=0.57 Heal=0.52 Whee=0.24 Whee=0.25
icbhi  late3                    seed 22  balanced 0.357  F1 0.345  Crac=0.62 Heal=0.51 Whee=0.17 Whee=0.12
icbhi  fdc2_nochroma            seed 11  balanced 0.365  F1 0.349  Crac=0.55 Heal=0.46 Whee=0.25 Whee=0.20
icbhi  single_spec              seed 33  balanced 0.346  F1 0.324  Crac=0.46 Heal=0.40 Whee=0.17 Whee=0.36
icbhi  single_mfcc              seed 22  balanced 0.367  F1 0.324  Crac=0.74 Heal=0.30 Whee=0.27 Whee=0.17
icbhi  single_chroma            seed 33  balanced 0.389  F1 0.308  Crac=0.81 Heal=0.21 Whee=0.07 Whee=0.45
sprs   fdc3 (PRIMARY)           seed 33  balanced 0.572  F1 0.454  Crac=0.53 Heal=0.70 Whee=0.55 Whee=0.51
sprs   late3                    seed 22  balanced 0.528  F1 0.425  Crac=0.48 Heal=0.70 Whee=0.44 Whee=0.49
sprs   fdc2_nochroma            seed 11  balanced 0.534  F1 0.412  Crac=0.45 Heal=0.69 Whee=0.46 Whee=0.53
sprs   single_spec              seed 33  balanced 0.510  F1 0.391  Crac=0.47 Heal=0.66 Whee=0.42 Whee=0.49
sprs   single_mfcc              seed 22  balanced 0.513  F1 0.395  Crac=0.40 Heal=0.67 Whee=0.46 Whee=0.53
sprs   single_chroma            seed 33  balanced 0.459  F1 0.223  Crac=0.51 Heal=0.14 Whee=0.36 Whee=0.82
```