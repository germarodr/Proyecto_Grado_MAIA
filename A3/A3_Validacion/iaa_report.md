# A3 inter-annotator agreement report

Metrics lead: ABC (group 14, sampling lead). Computed with `a3_metrics.py` (commit in manifest_metrics.json) from the frozen gold files of both rounds. Guide rev3.1; contract of 28 Oct 2026 and its pending changes.

5940 annotated packages (2970 T_A, 2970 T_B), each annotated once by a member of group 14 and once by a member of group 15. Cohen's kappa takes the G14 and the G15 annotation of each package as the two raters, on the primary label, **before adjudication**; Krippendorff's alpha (nominal) does not assume fixed raters; alpha with MASI distance uses primary + secondary labels. `unclear` counts as an answer.

**The A2 pre-label was visible to both annotators** (A3 asks to confirm or correct it), so part of the agreement can come from confirming it. Kappa is therefore reported next to the correction rate per cell and per annotator: a rate near zero in a cell would point to automatic confirmation rather than review.

## 1. Agreement (primary label)

| scope | packages | observed agreement | Cohen kappa | >= 0.6 | alpha (nominal) | alpha (MASI, primary + secondary) | annotations with a secondary | unclear annotations |
|---|---|---|---|---|---|---|---|---|
| T_A (G14), all rounds | 2970 | 88.0% | 0.865 | yes | 0.865 | 0.861 | 54 | 4 |
| T_A, round1 | 1980 | 88.7% | 0.865 | yes | 0.865 | 0.858 | 38 | 4 |
| T_A, round2 | 990 | 86.8% | 0.812 | yes | 0.812 | 0.811 | 16 | 0 |
| T_B (G15), all rounds | 2970 | 87.0% | 0.854 | yes | 0.854 | 0.850 | 62 | 2 |
| T_B, round1 | 1980 | 89.1% | 0.870 | yes | 0.870 | 0.867 | 34 | 2 |
| T_B, round2 | 990 | 82.7% | 0.759 | yes | 0.759 | 0.754 | 28 | 0 |
| Both sets | 5940 | 87.5% | 0.860 | yes | 0.860 | 0.855 | 116 | 6 |
| Both sets, round1 | 3960 | 88.9% | 0.867 | yes | 0.867 | 0.862 | 72 | 6 |
| Both sets, round2 | 1980 | 84.7% | 0.786 | yes | 0.786 | 0.782 | 44 | 0 |

Secondary labels: 116 of 11880 annotations (1.0%) have one; alpha MASI differs from nominal alpha only through them.

## 2. Agreement per label (one vs rest)

**T_A (G14)**

| label | G14 annotations | G15 annotations | both | positive specific agreement | kappa (one vs rest) |
|---|---|---|---|---|---|
| Background | 372 | 322 | 275 | 79.3% | 0.765 |
| Gap | 300 | 328 | 275 | 87.6% | 0.861 |
| Basis | 320 | 335 | 284 | 86.7% | 0.851 |
| Comparison | 307 | 302 | 267 | 87.7% | 0.863 |
| Application | 357 | 372 | 320 | 87.8% | 0.861 |
| Improvement/Modification | 309 | 290 | 256 | 85.5% | 0.838 |
| Evidence | 356 | 382 | 318 | 86.2% | 0.842 |
| Identification of the Originator | 325 | 324 | 316 | 97.4% | 0.971 |
| Further Reading | 320 | 315 | 304 | 95.7% | 0.952 |
| unclear | 4 | 0 | 0 | 0.0% | 0.000 |

**T_B (G15)**

| label | G14 annotations | G15 annotations | both | positive specific agreement | kappa (one vs rest) |
|---|---|---|---|---|---|
| Background | 372 | 317 | 270 | 78.4% | 0.756 |
| Gap | 300 | 326 | 269 | 85.9% | 0.843 |
| Basis | 340 | 321 | 278 | 84.1% | 0.821 |
| Comparison | 307 | 302 | 275 | 90.3% | 0.892 |
| Application | 364 | 395 | 327 | 86.2% | 0.841 |
| Improvement/Modification | 273 | 284 | 232 | 83.3% | 0.816 |
| Evidence | 371 | 395 | 329 | 85.9% | 0.838 |
| Identification of the Originator | 324 | 325 | 315 | 97.1% | 0.967 |
| Further Reading | 317 | 305 | 289 | 92.9% | 0.921 |
| unclear | 2 | 0 | 0 | 0.0% | 0.000 |

**Both sets**

| label | G14 annotations | G15 annotations | both | positive specific agreement | kappa (one vs rest) |
|---|---|---|---|---|---|
| Background | 744 | 639 | 545 | 78.8% | 0.760 |
| Gap | 600 | 654 | 544 | 86.8% | 0.852 |
| Basis | 660 | 656 | 562 | 85.4% | 0.836 |
| Comparison | 614 | 604 | 542 | 89.0% | 0.877 |
| Application | 721 | 767 | 647 | 87.0% | 0.851 |
| Improvement/Modification | 582 | 574 | 488 | 84.4% | 0.828 |
| Evidence | 727 | 777 | 647 | 86.0% | 0.840 |
| Identification of the Originator | 649 | 649 | 631 | 97.2% | 0.969 |
| Further Reading | 637 | 620 | 593 | 94.4% | 0.937 |
| unclear | 6 | 0 | 0 | 0.0% | 0.000 |

## 3. Correction rate of the A2 pre-label per test-set cell

| set | round | pre-label cell | packages | annotations corrected | rate | pkgs any | pkgs both | gold != pre-label |
|---|---|---|---|---|---|---|---|---|
| A | round1 | Background | 330 | 82 | 12.4% | 71 | 11 | 47 (14.2%) |
| A | round1 | Gap | 330 | 65 | 9.8% | 57 | 8 | 30 (9.1%) |
| A | round1 | Comparison | 330 | 73 | 11.1% | 64 | 9 | 34 (10.3%) |
| A | round1 | Application | 330 | 27 | 4.1% | 23 | 4 | 12 (3.6%) |
| A | round1 | Evidence | 330 | 24 | 3.6% | 23 | 1 | 8 (2.4%) |
| A | round1 | Identification of the Originator | 330 | 15 | 2.3% | 15 | 0 | 6 (1.8%) |
| A | round2 | Basis | 330 | 58 | 8.8% | 49 | 9 | 23 (7.0%) |
| A | round2 | Improvement/Modification | 330 | 89 | 13.5% | 75 | 14 | 51 (15.5%) |
| A | round2 | Further Reading | 330 | 31 | 4.7% | 27 | 4 | 13 (3.9%) |
| B | round1 | Background | 330 | 82 | 12.4% | 76 | 6 | 46 (13.9%) |
| B | round1 | Gap | 330 | 74 | 11.2% | 64 | 10 | 42 (12.7%) |
| B | round1 | Comparison | 330 | 71 | 10.8% | 56 | 15 | 27 (8.2%) |
| B | round1 | Application | 330 | 27 | 4.1% | 23 | 4 | 11 (3.3%) |
| B | round1 | Evidence | 330 | 13 | 2.0% | 11 | 2 | 5 (1.5%) |
| B | round1 | Identification of the Originator | 330 | 21 | 3.2% | 17 | 4 | 12 (3.6%) |
| B | round2 | Basis | 330 | 78 | 11.8% | 68 | 10 | 45 (13.6%) |
| B | round2 | Improvement/Modification | 330 | 142 | 21.5% | 102 | 40 | 83 (25.2%) |
| B | round2 | Further Reading | 330 | 43 | 6.5% | 41 | 2 | 16 (4.8%) |
| all | | | 5940 | 1015 | 8.5% | 862 | 153 | 511 (8.6%) |

## 4. Per annotator (pseudonyms)

| annotator | annotations | changed the pre-label | partners changed it (same packages) | only the partner changed it | agrees with partner | agrees with gold | unclear |
|---|---|---|---|---|---|---|---|
| G14-a | 1485 | 10.8% | 9.4% | 86 | 86.4% | 92.9% | 0 |
| G14-b | 1485 | 3.5% | 8.9% | 118 | 89.3% | 93.5% | 0 |
| G14-c | 1485 | 7.8% | 9.2% | 99 | 87.8% | 94.0% | 0 |
| G14-d | 1485 | 7.9% | 10.8% | 112 | 86.6% | 91.8% | 6 |
| G15-a | 1485 | 10.9% | 7.2% | 55 | 88.4% | 94.6% | 0 |
| G15-b | 1485 | 1.2% | 7.7% | 113 | 91.2% | 94.4% | 0 |
| G15-c | 1485 | 12.8% | 7.1% | 59 | 85.8% | 92.9% | 0 |
| G15-d | 1485 | 13.3% | 8.1% | 67 | 84.7% | 93.8% | 0 |

## 5. Agreement by self-declared confidence

| confidence | annotations | share | changed the pre-label | agrees with partner | agrees with gold |
|---|---|---|---|---|---|
| Alta | 10759 | 90.6% | 5.6% | 90.0% | 95.0% |
| Media | 1096 | 9.2% | 36.2% | 64.0% | 79.5% |
| Baja | 25 | 0.2% | 44.0% | 44.0% | 62.5% |

## 6. Adjudication (vote first; contract Section 9)

| round | adjudicated | labels differ | an unclear | both votes cast | votes equal | kappa (votes) | decided by votes | by discussion | final = pre-label | final = one annotator | final unclear |
|---|---|---|---|---|---|---|---|---|---|---|---|
| round1 | 439 | 433 | 6 | 439 | 349 (79.5%) | 0.753 | 349 | 90 | 220 | 415 | 2 |
| round2 | 302 | 302 | 0 | 302 | 254 (84.1%) | 0.803 | 254 | 48 | 131 | 284 | 3 |

## 7. A2 pre-label vs gold

| A2 pre-label | packages | gold = pre-label | unanimous (3/3): packages | kept | 2 of 3: packages | kept |
|---|---|---|---|---|---|---|
| Background | 660 | 85.9% | 424 | 90.8% | 236 | 77.1% |
| Gap | 660 | 89.1% | 285 | 88.8% | 375 | 89.3% |
| Basis | 660 | 89.7% | 428 | 95.1% | 232 | 79.7% |
| Comparison | 660 | 90.8% | 471 | 94.3% | 189 | 82.0% |
| Application | 660 | 96.5% | 494 | 98.8% | 166 | 89.8% |
| Improvement/Modification | 660 | 79.7% | 348 | 92.8% | 312 | 65.1% |
| Evidence | 660 | 98.0% | 385 | 98.7% | 275 | 97.1% |
| Identification of the Originator | 660 | 97.3% | 538 | 97.8% | 122 | 95.1% |
| Further Reading | 660 | 95.6% | 508 | 97.6% | 152 | 88.8% |
| all | 5940 | 91.4% | 3881 | 95.4% | 2059 | 83.9% |


| pre-label \ gold | Background | Gap | Basis | Comparison | Application | IM | Evidence | Originator | FR | unclear |
|---|---|---|---|---|---|---|---|---|---|---|
| Background | 567 | 29 | 1 | 8 | 12 | . | 35 | 6 | 1 | 1 |
| Gap | 22 | 588 | . | 7 | . | . | 42 | . | . | 1 |
| Basis | 10 | . | 592 | 1 | 31 | 20 | 3 | 2 | . | 1 |
| Comparison | 21 | 12 | 4 | 599 | 17 | 3 | 4 | . | . | . |
| Application | 13 | . | . | 1 | 637 | 7 | 1 | . | 1 | . |
| Improvement/Modification | 25 | 1 | 53 | 3 | 50 | 526 | . | . | . | 2 |
| Evidence | 3 | 1 | 2 | 1 | 6 | . | 647 | . | . | . |
| Identification of the Originator | 4 | . | 3 | . | 7 | 2 | 2 | 642 | . | . |
| Further Reading | 1 | . | . | 1 | 5 | . | 22 | . | 631 | . |

IM = Improvement/Modification, Originator = Identification of the Originator, FR = Further Reading

## 8. Gold counts (valid = in the test set)

| label | T_A (G14) | T_B (G15) | total |
|---|---|---|---|
| Background | 336 | 330 | 666 |
| Gap | 321 | 310 | 631 |
| Basis | 333 | 322 | 655 |
| Comparison | 308 | 313 | 621 |
| Application | 365 | 400 | 765 |
| Improvement/Modification | 290 | 268 | 558 |
| Evidence | 370 | 386 | 756 |
| Identification of the Originator | 326 | 324 | 650 |
| Further Reading | 318 | 315 | 633 |
| **valid (in_eval)** | 2967 | 2968 | 5935 |
| unclear (out) | 3 | 2 | 5 |

## Note on the per-annotator correction rates

Two annotators changed the A2 pre-label clearly less often than their partners on the same packages: G15-b (1.2% vs 7.7%) and G14-b (3.5% vs 8.9%). Every package was annotated by one member of each group, and any disagreement went to adjudication, so the corrections these two did not make were raised by their partners in 113 and 118 packages and decided there. The design cannot detect packages where both annotators kept a wrong pre-label. Sensitivity: without the packages of these two annotators, Cohen kappa is 0.845 on T_A (1760 packages) and 0.840 on T_B (1595 packages), against 0.865 and 0.854 overall.

## Top-up release, round1 (frozen release_round1.md)

Quota 300 valid gold per cell; release = ceil(1.1 x deficit), reserve first, then buffer.

| set | category | valid | deficit | release | from reserve | from buffer | short |
|---|---|---|---|---|---|---|---|
| A | Background | 320 | 0 | 0 | 0 | 0 | 0 |
| A | Comparison | 307 | 0 | 0 | 0 | 0 | 0 |
| A | Gap | 321 | 0 | 0 | 0 | 0 | 0 |
| A | Evidence | 357 | 0 | 0 | 0 | 0 | 0 |
| A | Application | 337 | 0 | 0 | 0 | 0 | 0 |
| A | Identification of the Originator | 325 | 0 | 0 | 0 | 0 | 0 |
| B | Background | 310 | 0 | 0 | 0 | 0 | 0 |
| B | Comparison | 309 | 0 | 0 | 0 | 0 | 0 |
| B | Gap | 309 | 0 | 0 | 0 | 0 | 0 |
| B | Evidence | 374 | 0 | 0 | 0 | 0 | 0 |
| B | Application | 342 | 0 | 0 | 0 | 0 | 0 |
| B | Identification of the Originator | 323 | 0 | 0 | 0 | 0 | 0 |

Released: 0 packages; cells short even with the buffer: none

## Top-up release, round2 (frozen release_round2.md)

Decision 8 Nov 2026 (groups 14 and 15): round 2 closed without wave 4; cells below 300 keep what they have, documented as lower quotas: A/Improvement/Modification 290, B/Improvement/Modification 268.

## What contract 6.4 would have released (not applied)

Quota 300 valid gold per cell; release = ceil(1.1 x deficit), reserve first, then buffer.

| set | category | valid | deficit | release | from reserve | from buffer | short |
|---|---|---|---|---|---|---|---|
| A | Basis | 333 | 0 | 0 | 0 | 0 | 0 |
| A | Improvement/Modification | 290 | 10 | 11 | 11 | 0 | 0 |
| A | Further Reading | 318 | 0 | 0 | 0 | 0 | 0 |
| B | Basis | 322 | 0 | 0 | 0 | 0 | 0 |
| B | Improvement/Modification | 268 | 32 | 36 | 30 | 6 | 0 |
| B | Further Reading | 315 | 0 | 0 | 0 | 0 | 0 |

Released: 47 packages; cells short even with the buffer: none
