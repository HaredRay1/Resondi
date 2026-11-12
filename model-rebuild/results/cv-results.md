# 5-fold patient cross-validation over all ICBHI patients (2026-11-12 05:28)

Every ICBHI patient is tested exactly once, by a model that never saw them. Cycle-level balanced accuracy is pooled over all patients, with a 95% patient-bootstrap CI.

```
mfcc_icbhi seed 11                 pooled bal 0.340 (CI 0.304-0.382)  folds 0.341+/-0.027  acc 0.366  F1 0.312  Crac=0.50 Heal=0.33 Whee=0.31 Whee=0.22
fdc3_sprs seed 11                  pooled bal 0.390 (CI 0.352-0.424)  folds 0.385+/-0.031  acc 0.411  F1 0.356  Crac=0.54 Heal=0.37 Whee=0.37 Whee=0.27  SPRS-test 0.561
fdc3_sprs seed 22                  pooled bal 0.391 (CI 0.352-0.429)  folds 0.391+/-0.026  acc 0.402  F1 0.353  Crac=0.50 Heal=0.37 Whee=0.39 Whee=0.30  SPRS-test 0.545
fdc3_sprs seed 33                  pooled bal 0.395 (CI 0.356-0.434)  folds 0.396+/-0.029  acc 0.430  F1 0.368  Crac=0.54 Heal=0.41 Whee=0.37 Whee=0.25  SPRS-test 0.552
fdc3_sprs ensemble 11+22+33        pooled bal 0.400 (CI 0.359-0.435)  folds 0.399+/-0.028  acc 0.430  F1 0.369  Crac=0.56 Heal=0.40 Whee=0.38 Whee=0.26  SPRS-test 0.563
```
