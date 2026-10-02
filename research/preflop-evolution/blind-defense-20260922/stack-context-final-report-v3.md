# Matched stack-depth model comparison

The registered improvement criterion is not met; at least one stack/actor comparison has a negative mean gain.

Candidate = baseline plus 25 river hand-versus-board inputs. Both learn the existing heads-up all-street tree. BB faces a BTN min-raise, SB has folded, dead money is 0.5bb, and rake is 5% capped at 2bb. The inherited 200bb BTN entry range is fixed across stacks.

Each depth uses 4,096 fresh physical deals and eight crossed profiles. A and B are separate training runs. Each gain replaces one player while holding the indicated opponent fixed. These are bb per entry, not cash-game win rates or equilibrium/exploitability estimates.

All primary intervals use the original simultaneous bounded empirical-Bernstein method across 56 comparisons (family alpha 0.05, one final look). Improvement requires all eight pooled lower bounds above zero and no negative per-depth mean. A failed criterion does not establish equivalence.

## Equal-depth pooled gains

Divide each depth gain by its starting stack, then average the seven depths with equal weight. Values below are percentages of starting stack per entry, not range-frequency percentage points.

| Run | Player replaced | Fixed opponent | Mean % | Primary lower % | Primary upper % |
| --- | --- | --- | ---: | ---: | ---: |
| A | BB | baseline BTN | 0.007290 | -2.195089 | 2.209669 |
| A | BB | candidate BTN | 0.026171 | -2.196748 | 2.249090 |
| A | BTN | baseline BB | 0.097418 | -2.074083 | 2.268919 |
| A | BTN | candidate BB | 0.078635 | -2.098418 | 2.255688 |
| B | BB | baseline BTN | 0.072099 | -2.141619 | 2.285816 |
| B | BB | candidate BTN | 0.041964 | -2.169476 | 2.253404 |
| B | BTN | baseline BB | -0.048417 | -2.241559 | 2.144724 |
| B | BTN | candidate BB | -0.020394 | -2.194759 | 2.153970 |

## All stack-specific comparisons

60bb and 150bb were held out from fitting. Test draws are fresh but training/test boards are not strictly disjoint. The intervals measure payoff uncertainty, not uncertainty in hand frequencies.

Signed paired loss = baseline value minus candidate value; a negative loss is a gain. 95th/99th percentiles are linear empirical quantiles, not tail guarantees. “Mean positive loss” averages max(loss, 0) over every deal.

### 20bb — fitting depth

| Run | Player replaced | Fixed opponent | Mean bb | Primary lower bb | Primary upper bb | Negative deals % |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | BB | baseline BTN | -0.013372 | -0.490562 | 0.463818 | 42.9688 |
| A | BB | candidate BTN | 0.000937 | -0.480637 | 0.482511 | 42.9199 |
| A | BTN | baseline BB | 0.070114 | -0.419682 | 0.559910 | 47.7295 |
| A | BTN | candidate BB | 0.059137 | -0.422899 | 0.541172 | 47.5586 |
| B | BB | baseline BTN | 0.035514 | -0.451303 | 0.522332 | 47.6807 |
| B | BB | candidate BTN | 0.017842 | -0.465513 | 0.501198 | 48.8525 |
| B | BTN | baseline BB | -0.031296 | -0.520395 | 0.457803 | 50.3418 |
| B | BTN | candidate BB | -0.013923 | -0.506637 | 0.478790 | 49.0967 |

| Run | Player | Fixed opponent | Loss p95 bb | Loss p99 bb | Worst loss bb | Mean positive loss bb |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | BB | baseline BTN | 2.069925 | 4.411382 | 15.382538 | 0.367132 |
| A | BB | candidate BTN | 2.116187 | 4.982404 | 14.416127 | 0.376507 |
| A | BTN | baseline BB | 1.584100 | 4.438138 | 13.375178 | 0.303776 |
| A | BTN | candidate BB | 1.713270 | 4.360034 | 13.169681 | 0.292806 |
| B | BB | baseline BTN | 2.137914 | 4.817846 | 12.780805 | 0.396119 |
| B | BB | candidate BTN | 2.003828 | 4.643529 | 13.115997 | 0.394795 |
| B | BTN | baseline BB | 1.957992 | 5.046292 | 18.947877 | 0.365167 |
| B | BTN | candidate BB | 1.743934 | 4.464895 | 18.527848 | 0.351124 |

| Run | BB policy | BTN policy | BB min bb | BB max bb | BTN min bb | BTN max bb |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | baseline | baseline | -19.198074 | 18.274490 | -19.762680 | 17.764088 |
| A | baseline | candidate | -19.684017 | 18.025513 | -19.524272 | 18.210511 |
| A | candidate | baseline | -19.277261 | 17.685811 | -19.143933 | 17.839192 |
| A | candidate | candidate | -19.678995 | 18.004792 | -19.450635 | 18.204672 |
| B | baseline | baseline | -19.579995 | 18.211548 | -19.682647 | 18.099600 |
| B | baseline | candidate | -19.429894 | 18.179219 | -19.648404 | 17.980519 |
| B | candidate | baseline | -19.596962 | 17.830881 | -19.258836 | 18.110792 |
| B | candidate | candidate | -19.328629 | 17.598075 | -19.031161 | 17.881656 |

### 40bb — fitting depth

| Run | Player replaced | Fixed opponent | Mean bb | Primary lower bb | Primary upper bb | Negative deals % |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | BB | baseline BTN | -0.024540 | -0.980641 | 0.931561 | 49.5850 |
| A | BB | candidate BTN | -0.048870 | -1.033564 | 0.935823 | 50.5615 |
| A | BTN | baseline BB | -0.017766 | -0.939916 | 0.904384 | 46.9482 |
| A | BTN | candidate BB | 0.003282 | -0.934316 | 0.940879 | 45.3369 |
| B | BB | baseline BTN | -0.018987 | -0.970235 | 0.932260 | 49.6094 |
| B | BB | candidate BTN | -0.030675 | -0.991392 | 0.930043 | 50.4150 |
| B | BTN | baseline BB | -0.001988 | -0.931535 | 0.927558 | 50.1953 |
| B | BTN | candidate BB | 0.007241 | -0.905476 | 0.919958 | 50.1709 |

| Run | Player | Fixed opponent | Loss p95 bb | Loss p99 bb | Worst loss bb | Mean positive loss bb |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | BB | baseline BTN | 3.384318 | 9.780378 | 39.440710 | 0.691006 |
| A | BB | candidate BTN | 3.840557 | 11.237276 | 34.554835 | 0.791935 |
| A | BTN | baseline BB | 2.382834 | 8.425966 | 23.523017 | 0.438254 |
| A | BTN | candidate BB | 2.751890 | 8.036491 | 32.126164 | 0.512083 |
| B | BB | baseline BTN | 3.193948 | 10.486905 | 29.684838 | 0.639300 |
| B | BB | candidate BTN | 3.151252 | 10.672168 | 27.790028 | 0.653557 |
| B | BTN | baseline BB | 2.242866 | 7.550445 | 28.849278 | 0.463832 |
| B | BTN | candidate BB | 2.068999 | 7.013264 | 25.290152 | 0.413991 |

| Run | BB policy | BTN policy | BB min bb | BB max bb | BTN min bb | BTN max bb |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | baseline | baseline | -36.862141 | 38.116072 | -39.596692 | 35.380264 |
| A | baseline | candidate | -39.289234 | 38.248474 | -39.746547 | 37.814360 |
| A | candidate | baseline | -37.385753 | 37.492514 | -38.971553 | 35.975801 |
| A | candidate | candidate | -39.268184 | 37.602940 | -39.080604 | 37.784920 |
| B | baseline | baseline | -37.755803 | 38.313105 | -39.810351 | 36.317944 |
| B | baseline | candidate | -38.628112 | 36.890359 | -38.366738 | 37.193280 |
| B | candidate | baseline | -37.657132 | 38.142069 | -39.637608 | 36.251475 |
| B | candidate | candidate | -39.072298 | 36.712057 | -38.173846 | 37.606494 |

### 60bb — held out from fitting

| Run | Player replaced | Fixed opponent | Mean bb | Primary lower bb | Primary upper bb | Negative deals % |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | BB | baseline BTN | 0.053761 | -1.237252 | 1.344774 | 42.5537 |
| A | BB | candidate BTN | 0.054197 | -1.255290 | 1.363683 | 43.5303 |
| A | BTN | baseline BB | 0.017162 | -1.241710 | 1.276034 | 45.6787 |
| A | BTN | candidate BB | 0.006350 | -1.271670 | 1.284371 | 45.7764 |
| B | BB | baseline BTN | 0.028714 | -1.270445 | 1.327873 | 51.1230 |
| B | BB | candidate BTN | 0.010797 | -1.288108 | 1.309702 | 51.0010 |
| B | BTN | baseline BB | -0.042720 | -1.300651 | 1.215211 | 51.4160 |
| B | BTN | candidate BB | -0.027733 | -1.290110 | 1.234643 | 51.4160 |

| Run | Player | Fixed opponent | Loss p95 bb | Loss p99 bb | Worst loss bb | Mean positive loss bb |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | BB | baseline BTN | 2.848883 | 6.965488 | 19.121463 | 0.540666 |
| A | BB | candidate BTN | 3.483083 | 8.533844 | 18.622265 | 0.636740 |
| A | BTN | baseline BB | 2.173891 | 5.845080 | 16.287759 | 0.430206 |
| A | BTN | candidate BB | 2.677737 | 6.215863 | 20.580246 | 0.508649 |
| B | BB | baseline BTN | 2.957435 | 7.188820 | 14.489383 | 0.593387 |
| B | BB | candidate BTN | 2.929735 | 7.806909 | 17.288331 | 0.597181 |
| B | BTN | baseline BB | 2.060693 | 4.866605 | 19.196247 | 0.438152 |
| B | BTN | candidate BB | 1.896404 | 4.672120 | 20.553995 | 0.401444 |

| Run | BB policy | BTN policy | BB min bb | BB max bb | BTN min bb | BTN max bb |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | baseline | baseline | -47.966493 | 51.074678 | -52.490122 | 46.711946 |
| A | baseline | candidate | -44.995505 | 52.142359 | -53.571242 | 43.982958 |
| A | candidate | baseline | -45.779777 | 49.224751 | -50.657937 | 44.604568 |
| A | candidate | candidate | -38.716037 | 50.727646 | -52.199377 | 37.919184 |
| B | baseline | baseline | -48.549753 | 48.274063 | -49.585338 | 47.220481 |
| B | baseline | candidate | -48.660857 | 48.614074 | -49.964934 | 47.275047 |
| B | candidate | baseline | -49.536230 | 49.531819 | -50.827051 | 48.066794 |
| B | candidate | candidate | -51.968188 | 49.998086 | -51.326944 | 50.498315 |

### 100bb — fitting depth

| Run | Player replaced | Fixed opponent | Mean bb | Primary lower bb | Primary upper bb | Negative deals % |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | BB | baseline BTN | -0.089075 | -2.311730 | 2.133581 | 50.1221 |
| A | BB | candidate BTN | -0.003496 | -2.239254 | 2.232261 | 51.0986 |
| A | BTN | baseline BB | 0.115258 | -2.067131 | 2.297648 | 46.0205 |
| A | BTN | candidate BB | 0.029893 | -2.149754 | 2.209540 | 46.3135 |
| B | BB | baseline BTN | 0.121231 | -2.148809 | 2.391272 | 50.5371 |
| B | BB | candidate BTN | 0.052110 | -2.180132 | 2.284353 | 50.8545 |
| B | BTN | baseline BB | -0.097055 | -2.318481 | 2.124371 | 52.7100 |
| B | BTN | candidate BB | -0.023340 | -2.179378 | 2.132697 | 51.0498 |

| Run | Player | Fixed opponent | Loss p95 bb | Loss p99 bb | Worst loss bb | Mean positive loss bb |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | BB | baseline BTN | 4.460906 | 14.986817 | 75.462845 | 0.938361 |
| A | BB | candidate BTN | 4.887398 | 15.805412 | 42.250921 | 0.956654 |
| A | BTN | baseline BB | 2.455801 | 11.128049 | 62.137178 | 0.559087 |
| A | BTN | candidate BB | 3.048130 | 11.746322 | 66.047075 | 0.647735 |
| B | BB | baseline BTN | 4.434696 | 15.103140 | 50.957512 | 0.886976 |
| B | BB | candidate BTN | 4.539355 | 15.193970 | 50.438789 | 0.897599 |
| B | BTN | baseline BB | 2.937224 | 15.224241 | 80.659412 | 0.712826 |
| B | BTN | candidate BB | 2.195006 | 10.861576 | 46.881382 | 0.541050 |

| Run | BB policy | BTN policy | BB min bb | BB max bb | BTN min bb | BTN max bb |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | baseline | baseline | -80.574222 | 78.581711 | -79.884281 | 79.096786 |
| A | baseline | candidate | -83.295086 | 84.185009 | -85.655334 | 81.848828 |
| A | candidate | baseline | -89.691713 | 87.729449 | -89.125338 | 88.281847 |
| A | candidate | candidate | -93.636465 | 83.984107 | -85.418383 | 92.197172 |
| B | baseline | baseline | -93.866257 | 83.812405 | -85.310380 | 92.475010 |
| B | baseline | candidate | -96.277405 | 60.749325 | -61.951919 | 94.826690 |
| B | candidate | baseline | -88.227670 | 83.540488 | -85.028598 | 86.888830 |
| B | candidate | candidate | -91.564376 | 74.294040 | -75.506035 | 90.182751 |

### 150bb — held out from fitting

| Run | Player replaced | Fixed opponent | Mean bb | Primary lower bb | Primary upper bb | Negative deals % |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | BB | baseline BTN | 0.110318 | -2.981496 | 3.202131 | 41.4551 |
| A | BB | candidate BTN | 0.144405 | -2.956929 | 3.245738 | 40.0146 |
| A | BTN | baseline BB | 0.129231 | -2.899759 | 3.158221 | 43.5547 |
| A | BTN | candidate BB | 0.102632 | -2.930529 | 3.135794 | 45.4102 |
| B | BB | baseline BTN | 0.130140 | -2.950866 | 3.211145 | 49.2432 |
| B | BB | candidate BTN | 0.128397 | -2.961579 | 3.218373 | 49.9512 |
| B | BTN | baseline BB | -0.102015 | -3.194684 | 2.990654 | 52.2949 |
| B | BTN | candidate BB | -0.103888 | -3.207915 | 3.000139 | 52.2705 |

| Run | Player | Fixed opponent | Loss p95 bb | Loss p99 bb | Worst loss bb | Mean positive loss bb |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | BB | baseline BTN | 4.076772 | 10.859351 | 40.174025 | 0.773044 |
| A | BB | candidate BTN | 4.014483 | 11.321735 | 48.912399 | 0.796493 |
| A | BTN | baseline BB | 2.429137 | 7.670706 | 18.427391 | 0.499709 |
| A | BTN | candidate BB | 2.589782 | 8.200403 | 20.564116 | 0.521120 |
| B | BB | baseline BTN | 3.594614 | 9.239079 | 37.682919 | 0.736760 |
| B | BB | candidate BTN | 3.443171 | 9.579824 | 53.317583 | 0.742191 |
| B | BTN | baseline BB | 3.287906 | 10.684885 | 72.796827 | 0.727195 |
| B | BTN | candidate BB | 3.189880 | 10.586340 | 78.459599 | 0.685324 |

| Run | BB policy | BTN policy | BB min bb | BB max bb | BTN min bb | BTN max bb |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | baseline | baseline | -93.181406 | 96.705651 | -97.793527 | 91.724835 |
| A | baseline | candidate | -91.233743 | 95.066293 | -96.172805 | 89.759975 |
| A | candidate | baseline | -91.221891 | 83.320540 | -84.702493 | 89.859002 |
| A | candidate | candidate | -92.561858 | 87.218739 | -88.591814 | 91.066668 |
| B | baseline | baseline | -106.390075 | 79.879903 | -81.292642 | 104.949912 |
| B | baseline | candidate | -119.355189 | 85.937151 | -86.843163 | 117.892266 |
| B | candidate | baseline | -101.287956 | 81.719910 | -83.167252 | 99.978082 |
| B | candidate | candidate | -118.329715 | 100.065429 | -101.423662 | 116.949993 |

### 200bb — fitting depth

| Run | Player replaced | Fixed opponent | Mean bb | Primary lower bb | Primary upper bb | Negative deals % |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | BB | baseline BTN | 0.207342 | -4.092972 | 4.507656 | 46.4355 |
| A | BB | candidate BTN | 0.245148 | -4.070184 | 4.560479 | 46.4600 |
| A | BTN | baseline BB | 0.107197 | -4.081789 | 4.296184 | 45.6299 |
| A | BTN | candidate BB | 0.077436 | -4.118100 | 4.272972 | 45.1172 |
| B | BB | baseline BTN | 0.210039 | -4.102613 | 4.522691 | 52.8076 |
| B | BB | candidate BTN | 0.208901 | -4.137502 | 4.555304 | 54.4922 |
| B | BTN | baseline BB | 0.053257 | -4.289511 | 4.396024 | 52.6855 |
| B | BTN | candidate BB | 0.047980 | -4.190987 | 4.286947 | 52.3193 |

| Run | Player | Fixed opponent | Loss p95 bb | Loss p99 bb | Worst loss bb | Mean positive loss bb |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | BB | baseline BTN | 6.943422 | 22.144477 | 80.594389 | 1.461421 |
| A | BB | candidate BTN | 7.359959 | 19.549479 | 99.367157 | 1.495493 |
| A | BTN | baseline BB | 3.564550 | 13.539176 | 55.103649 | 0.742396 |
| A | BTN | candidate BB | 3.835681 | 14.901210 | 84.326204 | 0.792464 |
| B | BB | baseline BTN | 6.372914 | 19.873393 | 84.988971 | 1.411696 |
| B | BB | candidate BTN | 6.307665 | 20.378172 | 89.259364 | 1.459109 |
| B | BTN | baseline BB | 5.593768 | 19.663729 | 107.067803 | 1.230362 |
| B | BTN | candidate BB | 4.204871 | 15.070342 | 92.064892 | 0.980462 |

| Run | BB policy | BTN policy | BB min bb | BB max bb | BTN min bb | BTN max bb |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | baseline | baseline | -168.737524 | 164.776610 | -166.097894 | 167.300308 |
| A | baseline | candidate | -153.068665 | 142.600694 | -143.942749 | 151.632764 |
| A | candidate | baseline | -158.213303 | 168.722799 | -170.058997 | 156.761051 |
| A | candidate | candidate | -142.883686 | 148.904153 | -150.278861 | 141.428082 |
| B | baseline | baseline | -165.714990 | 117.504822 | -118.527765 | 164.311538 |
| B | baseline | candidate | -181.842855 | 142.960501 | -144.327319 | 180.417459 |
| B | candidate | baseline | -156.167145 | 164.619482 | -165.868570 | 154.832455 |
| B | candidate | candidate | -175.561865 | 134.860304 | -136.091335 | 174.221713 |

### 400bb — fitting depth

| Run | Player replaced | Fixed opponent | Mean bb | Primary lower bb | Primary upper bb | Negative deals % |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | BB | baseline BTN | 0.006000 | -8.212962 | 8.224962 | 50.1465 |
| A | BB | candidate BTN | -0.019935 | -8.209430 | 8.169560 | 51.0254 |
| A | BTN | baseline BB | 0.368619 | -7.838673 | 8.575911 | 48.9258 |
| A | BTN | candidate BB | 0.395763 | -7.826807 | 8.618332 | 47.9980 |
| B | BB | baseline BTN | 0.054877 | -8.097855 | 8.207610 | 47.1680 |
| B | BB | candidate BTN | 0.084283 | -8.040681 | 8.209248 | 48.1445 |
| B | BTN | baseline BB | 0.128673 | -7.997274 | 8.254620 | 51.3916 |
| B | BTN | candidate BB | 0.094338 | -8.011088 | 8.199765 | 51.0986 |

| Run | Player | Fixed opponent | Loss p95 bb | Loss p99 bb | Worst loss bb | Mean positive loss bb |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | BB | baseline BTN | 8.296960 | 23.178568 | 103.995444 | 1.826009 |
| A | BB | candidate BTN | 8.030781 | 22.676979 | 101.200794 | 1.760809 |
| A | BTN | baseline BB | 4.276384 | 17.379538 | 132.452323 | 1.013931 |
| A | BTN | candidate BB | 4.466802 | 19.786600 | 121.909187 | 1.085553 |
| B | BB | baseline BTN | 4.687634 | 16.817001 | 123.836960 | 1.138747 |
| B | BB | candidate BTN | 4.501843 | 17.857527 | 96.718673 | 1.117034 |
| B | BTN | baseline BB | 3.594032 | 14.134132 | 125.878080 | 0.829746 |
| B | BTN | candidate BB | 3.294449 | 14.142965 | 169.044549 | 0.763646 |

| Run | BB policy | BTN policy | BB min bb | BB max bb | BTN min bb | BTN max bb |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | baseline | baseline | -207.142167 | 198.569943 | -199.836192 | 206.081556 |
| A | baseline | candidate | -241.049016 | 142.379828 | -143.632898 | 239.551172 |
| A | candidate | baseline | -247.636499 | 212.005279 | -213.274357 | 246.202396 |
| A | candidate | candidate | -252.591806 | 141.858625 | -143.019775 | 251.109035 |
| B | baseline | baseline | -252.546086 | 240.330483 | -241.787384 | 251.112018 |
| B | baseline | candidate | -241.695869 | 258.372836 | -259.719745 | 240.196791 |
| B | candidate | baseline | -155.275162 | 257.288371 | -258.778699 | 154.352395 |
| B | candidate | candidate | -146.234110 | 256.417210 | -257.913391 | 145.479810 |

## Verification scope

The independent reader checks 256 reconstructed training chance cycles, 896 evaluation archives, 28 complete preflop catalog CPU-reference replays and 14 first/last test-batch replays. It shares the native payoff oracle and does not replay every postflop policy row.

All four frozen banks use played generations 0–63, weights 1–64 and exclude unplayed generation 64. Test results do not select a checkpoint. The preserved JSON contains the original full precision statistics, including exploratory normal intervals, which do not replace the primary gate.

This comparison does not qualify complete preflop accuracy, flexible multiway play, GTO Wizard agreement or production readiness. Range behavior and supported hand changes still require plain-English analysis.
