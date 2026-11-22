# A1 — estadísticas de similitud coseno

Puntajes de SciBERT sin ajuste fino (comprimidos por anisotropía): sirven para ordenar, no como medida calibrada de relevancia.


## piloto_v1

Filas: 524.713 (partes: 6); con menos de 3 chunks: 0 (0.00%).

| Medida | n | media | desv | min | p5 | p25 | mediana | p75 | p95 | max |
|---|---|---|---|---|---|---|---|---|---|---|
| Coseno Top-1 | 524.713 | 0.9195 | 0.0258 | 0.4302 | 0.8769 | 0.9087 | 0.9235 | 0.9357 | 0.9504 | 0.9998 |
| Coseno Top-2 | 524.713 | 0.9103 | 0.0272 | 0.4041 | 0.8647 | 0.8996 | 0.9150 | 0.9273 | 0.9417 | 0.9740 |
| Coseno Top-3 | 524.713 | 0.9043 | 0.0282 | 0.3919 | 0.8566 | 0.8936 | 0.9094 | 0.9218 | 0.9362 | 0.9680 |
| Brecha Top-1 − Top-2 | 524.713 | 0.0092 | 0.0094 | 0.0000 | 0.0005 | 0.0028 | 0.0065 | 0.0126 | 0.0268 | 0.3199 |
| Brecha Top-1 − Top-3 | 524.713 | 0.0152 | 0.0117 | 0.0000 | 0.0027 | 0.0072 | 0.0125 | 0.0199 | 0.0367 | 0.3384 |

Secciones más frecuentes del chunk Top-1 (encabezado propio, minúsculas):

| Sección | n | % |
|---|---|---|
| introduction | 151.963 | 29.0% |
| related work | 117.587 | 22.4% |
| related works | 10.020 | 1.9% |
| conclusion | 9.111 | 1.7% |
| experiments | 6.334 | 1.2% |
| (sin sección) | 3.704 | 0.7% |
| cifar-10 and analysis | 3.023 | 0.6% |
| experiment: multi-layer neural networks | 2.435 | 0.5% |
| imagenet localization | 2.364 | 0.5% |
| conclusions | 2.324 | 0.4% |
| blind review | 2.303 | 0.4% |
| results | 1.948 | 0.4% |
| discussion | 1.775 | 0.3% |
| method | 1.747 | 0.3% |
| prior work | 1.462 | 0.3% |

## piloto_norw

Filas: 524.713 (partes: 6); con menos de 3 chunks: 0 (0.00%).

| Medida | n | media | desv | min | p5 | p25 | mediana | p75 | p95 | max |
|---|---|---|---|---|---|---|---|---|---|---|
| Coseno Top-1 | 524.713 | 0.9148 | 0.0273 | 0.4285 | 0.8690 | 0.9039 | 0.9192 | 0.9318 | 0.9472 | 0.9998 |
| Coseno Top-2 | 524.713 | 0.9047 | 0.0288 | 0.4041 | 0.8556 | 0.8938 | 0.9099 | 0.9227 | 0.9376 | 0.9740 |
| Coseno Top-3 | 524.713 | 0.8987 | 0.0297 | 0.3776 | 0.8475 | 0.8876 | 0.9042 | 0.9172 | 0.9322 | 0.9680 |
| Brecha Top-1 − Top-2 | 524.713 | 0.0101 | 0.0106 | 0.0000 | 0.0005 | 0.0029 | 0.0069 | 0.0137 | 0.0303 | 0.3199 |
| Brecha Top-1 − Top-3 | 524.713 | 0.0162 | 0.0127 | 0.0000 | 0.0028 | 0.0075 | 0.0130 | 0.0212 | 0.0400 | 0.3384 |

Secciones más frecuentes del chunk Top-1 (encabezado propio, minúsculas):

| Sección | n | % |
|---|---|---|
| introduction | 245.680 | 46.8% |
| conclusion | 15.726 | 3.0% |
| experiments | 8.033 | 1.5% |
| conclusions | 4.465 | 0.9% |
| imagenet localization | 4.117 | 0.8% |
| (sin sección) | 4.112 | 0.8% |
| object detection baselines | 3.875 | 0.7% |
| results | 2.809 | 0.5% |
| method | 2.749 | 0.5% |
| discussion | 2.705 | 0.5% |
| experiment: multi-layer neural networks | 2.470 | 0.5% |
| blind review | 2.303 | 0.4% |
| implementation details | 1.946 | 0.4% |
| object detection improvements | 1.792 | 0.3% |
| datasets | 1.556 | 0.3% |

## extension_norw

Filas: 196.622 (partes: 2); con menos de 3 chunks: 0 (0.00%).

| Medida | n | media | desv | min | p5 | p25 | mediana | p75 | p95 | max |
|---|---|---|---|---|---|---|---|---|---|---|
| Coseno Top-1 | 196.622 | 0.9128 | 0.0280 | 0.3431 | 0.8668 | 0.9018 | 0.9173 | 0.9299 | 0.9456 | 0.9982 |
| Coseno Top-2 | 196.622 | 0.9035 | 0.0292 | 0.3412 | 0.8548 | 0.8924 | 0.9086 | 0.9214 | 0.9367 | 0.9841 |
| Coseno Top-3 | 196.622 | 0.8977 | 0.0299 | 0.3402 | 0.8473 | 0.8865 | 0.9032 | 0.9162 | 0.9315 | 0.9617 |
| Brecha Top-1 − Top-2 | 196.622 | 0.0093 | 0.0097 | 0.0000 | 0.0005 | 0.0027 | 0.0065 | 0.0127 | 0.0276 | 0.2428 |
| Brecha Top-1 − Top-3 | 196.622 | 0.0151 | 0.0117 | 0.0000 | 0.0026 | 0.0071 | 0.0123 | 0.0198 | 0.0369 | 0.2456 |

Secciones más frecuentes del chunk Top-1 (encabezado propio, minúsculas):

| Sección | n | % |
|---|---|---|
| introduction | 79.033 | 40.2% |
| conclusion | 5.650 | 2.9% |
| experiments | 3.902 | 2.0% |
| experiment: multi-layer neural networks | 2.686 | 1.4% |
| conclusions | 2.418 | 1.2% |
| (sin sección) | 2.165 | 1.1% |
| discussion | 1.597 | 0.8% |
| results | 1.259 | 0.6% |
| object detection baselines | 1.160 | 0.6% |
| imagenet localization | 839 | 0.4% |
| object detection improvements | 664 | 0.3% |
| experiment: logistic regression | 614 | 0.3% |
| experiment: bias-correction term | 605 | 0.3% |
| background | 572 | 0.3% |
| conclusion and future work | 540 | 0.3% |
