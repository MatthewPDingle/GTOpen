# Matched stack-depth model comparison

**SYNTHETIC SOFTWARE CONTROL — NOT A POKER RESULT.**

Candidate = baseline plus 25 river hand-versus-board inputs. Both learn the existing heads-up all-street tree. BB faces a BTN min-raise, SB has folded, dead money is 0.5bb, and rake is 5% capped at 2bb. The inherited 200bb BTN entry range is fixed across stacks.

Each depth uses 4,096 fresh physical deals and eight crossed profiles. A and B are separate training runs. Each gain replaces one player while holding the indicated opponent fixed. These are bb per entry, not cash-game win rates or equilibrium/exploitability estimates.

All primary intervals use the original simultaneous bounded empirical-Bernstein method across 56 comparisons (family alpha 0.05, one final look). Improvement requires all eight pooled lower bounds above zero and no negative per-depth mean. A failed criterion does not establish equivalence.

## Equal-depth pooled gains

Divide each depth gain by its starting stack, then average the seven depths with equal weight. Values below are percentages of starting stack per entry, not range-frequency percentage points.

| Run | Player replaced | Fixed opponent | Mean % | Primary lower % | Primary upper % |
| --- | --- | --- | ---: | ---: | ---: |
| A | BB | baseline BTN | 6.000000 | 4.075121 | 7.924879 |
| A | BB | candidate BTN | 6.000000 | 4.075121 | 7.924879 |
| A | BTN | baseline BB | 5.000000 | 3.075121 | 6.924879 |
| A | BTN | candidate BB | 5.000000 | 3.075121 | 6.924879 |
| B | BB | baseline BTN | 6.500000 | 4.575121 | 8.424879 |
| B | BB | candidate BTN | 6.500000 | 4.575121 | 8.424879 |
| B | BTN | baseline BB | 5.500000 | 3.575121 | 7.424879 |
| B | BTN | candidate BB | 5.500000 | 3.575121 | 7.424879 |

## All stack-specific comparisons

60bb and 150bb were held out from fitting. Test draws are fresh but training/test boards are not strictly disjoint. The intervals measure payoff uncertainty, not uncertainty in hand frequencies.

Signed paired loss = baseline value minus candidate value; a negative loss is a gain. 95th/99th percentiles are linear empirical quantiles, not tail guarantees. “Mean positive loss” averages max(loss, 0) over every deal.

### 20bb — fitting depth

| Run | Player replaced | Fixed opponent | Mean bb | Primary lower bb | Primary upper bb | Negative deals % |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | BB | baseline BTN | 1.200000 | 0.811819 | 1.588181 | 0.0000 |
| A | BB | candidate BTN | 1.200000 | 0.811819 | 1.588181 | 0.0000 |
| A | BTN | baseline BB | 1.000000 | 0.611819 | 1.388181 | 0.0000 |
| A | BTN | candidate BB | 1.000000 | 0.611819 | 1.388181 | 0.0000 |
| B | BB | baseline BTN | 1.300000 | 0.911819 | 1.688181 | 0.0000 |
| B | BB | candidate BTN | 1.300000 | 0.911819 | 1.688181 | 0.0000 |
| B | BTN | baseline BB | 1.100000 | 0.711819 | 1.488181 | 0.0000 |
| B | BTN | candidate BB | 1.100000 | 0.711819 | 1.488181 | 0.0000 |

| Run | Player | Fixed opponent | Loss p95 bb | Loss p99 bb | Worst loss bb | Mean positive loss bb |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | BB | baseline BTN | -1.196400 | -1.196080 | -1.196000 | 0.000000 |
| A | BB | candidate BTN | -1.196400 | -1.196080 | -1.196000 | 0.000000 |
| A | BTN | baseline BB | -0.996400 | -0.996080 | -0.996000 | 0.000000 |
| A | BTN | candidate BB | -0.996400 | -0.996080 | -0.996000 | 0.000000 |
| B | BB | baseline BTN | -1.296400 | -1.296080 | -1.296000 | 0.000000 |
| B | BB | candidate BTN | -1.296400 | -1.296080 | -1.296000 | 0.000000 |
| B | BTN | baseline BB | -1.096400 | -1.096080 | -1.096000 | 0.000000 |
| B | BTN | candidate BB | -1.096400 | -1.096080 | -1.096000 | 0.000000 |

| Run | BB policy | BTN policy | BB min bb | BB max bb | BTN min bb | BTN max bb |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | baseline | baseline | -0.040000 | 0.040000 | 0.460000 | 0.540000 |
| A | baseline | candidate | -1.044000 | -0.956000 | 1.456000 | 1.544000 |
| A | candidate | baseline | 1.156000 | 1.244000 | -0.744000 | -0.656000 |
| A | candidate | candidate | 0.152000 | 0.248000 | 0.252000 | 0.348000 |
| B | baseline | baseline | -0.040000 | 0.040000 | 0.460000 | 0.540000 |
| B | baseline | candidate | -1.144000 | -1.056000 | 1.556000 | 1.644000 |
| B | candidate | baseline | 1.256000 | 1.344000 | -0.844000 | -0.756000 |
| B | candidate | candidate | 0.152000 | 0.248000 | 0.252000 | 0.348000 |

### 40bb — fitting depth

| Run | Player replaced | Fixed opponent | Mean bb | Primary lower bb | Primary upper bb | Negative deals % |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | BB | baseline BTN | 2.400000 | 1.628429 | 3.171571 | 0.0000 |
| A | BB | candidate BTN | 2.400000 | 1.628429 | 3.171571 | 0.0000 |
| A | BTN | baseline BB | 2.000000 | 1.228429 | 2.771571 | 0.0000 |
| A | BTN | candidate BB | 2.000000 | 1.228429 | 2.771571 | 0.0000 |
| B | BB | baseline BTN | 2.600000 | 1.828429 | 3.371571 | 0.0000 |
| B | BB | candidate BTN | 2.600000 | 1.828429 | 3.371571 | 0.0000 |
| B | BTN | baseline BB | 2.200000 | 1.428429 | 2.971571 | 0.0000 |
| B | BTN | candidate BB | 2.200000 | 1.428429 | 2.971571 | 0.0000 |

| Run | Player | Fixed opponent | Loss p95 bb | Loss p99 bb | Worst loss bb | Mean positive loss bb |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | BB | baseline BTN | -2.392800 | -2.392160 | -2.392000 | 0.000000 |
| A | BB | candidate BTN | -2.392800 | -2.392160 | -2.392000 | 0.000000 |
| A | BTN | baseline BB | -1.992800 | -1.992160 | -1.992000 | 0.000000 |
| A | BTN | candidate BB | -1.992800 | -1.992160 | -1.992000 | 0.000000 |
| B | BB | baseline BTN | -2.592800 | -2.592160 | -2.592000 | 0.000000 |
| B | BB | candidate BTN | -2.592800 | -2.592160 | -2.592000 | 0.000000 |
| B | BTN | baseline BB | -2.192800 | -2.192160 | -2.192000 | 0.000000 |
| B | BTN | candidate BB | -2.192800 | -2.192160 | -2.192000 | 0.000000 |

| Run | BB policy | BTN policy | BB min bb | BB max bb | BTN min bb | BTN max bb |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | baseline | baseline | -0.080000 | 0.080000 | 0.420000 | 0.580000 |
| A | baseline | candidate | -2.088000 | -1.912000 | 2.412000 | 2.588000 |
| A | candidate | baseline | 2.312000 | 2.488000 | -1.988000 | -1.812000 |
| A | candidate | candidate | 0.304000 | 0.496000 | 0.004000 | 0.196000 |
| B | baseline | baseline | -0.080000 | 0.080000 | 0.420000 | 0.580000 |
| B | baseline | candidate | -2.288000 | -2.112000 | 2.612000 | 2.788000 |
| B | candidate | baseline | 2.512000 | 2.688000 | -2.188000 | -2.012000 |
| B | candidate | candidate | 0.304000 | 0.496000 | 0.004000 | 0.196000 |

### 60bb — held out from fitting

| Run | Player replaced | Fixed opponent | Mean bb | Primary lower bb | Primary upper bb | Negative deals % |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | BB | baseline BTN | 3.600000 | 2.445038 | 4.754962 | 0.0000 |
| A | BB | candidate BTN | 3.600000 | 2.445038 | 4.754962 | 0.0000 |
| A | BTN | baseline BB | 3.000000 | 1.845038 | 4.154962 | 0.0000 |
| A | BTN | candidate BB | 3.000000 | 1.845038 | 4.154962 | 0.0000 |
| B | BB | baseline BTN | 3.900000 | 2.745038 | 5.054962 | 0.0000 |
| B | BB | candidate BTN | 3.900000 | 2.745038 | 5.054962 | 0.0000 |
| B | BTN | baseline BB | 3.300000 | 2.145038 | 4.454962 | 0.0000 |
| B | BTN | candidate BB | 3.300000 | 2.145038 | 4.454962 | 0.0000 |

| Run | Player | Fixed opponent | Loss p95 bb | Loss p99 bb | Worst loss bb | Mean positive loss bb |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | BB | baseline BTN | -3.589200 | -3.588240 | -3.588000 | 0.000000 |
| A | BB | candidate BTN | -3.589200 | -3.588240 | -3.588000 | 0.000000 |
| A | BTN | baseline BB | -2.989200 | -2.988240 | -2.988000 | 0.000000 |
| A | BTN | candidate BB | -2.989200 | -2.988240 | -2.988000 | 0.000000 |
| B | BB | baseline BTN | -3.889200 | -3.888240 | -3.888000 | 0.000000 |
| B | BB | candidate BTN | -3.889200 | -3.888240 | -3.888000 | 0.000000 |
| B | BTN | baseline BB | -3.289200 | -3.288240 | -3.288000 | 0.000000 |
| B | BTN | candidate BB | -3.289200 | -3.288240 | -3.288000 | 0.000000 |

| Run | BB policy | BTN policy | BB min bb | BB max bb | BTN min bb | BTN max bb |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | baseline | baseline | -0.120000 | 0.120000 | 0.380000 | 0.620000 |
| A | baseline | candidate | -3.132000 | -2.868000 | 3.368000 | 3.632000 |
| A | candidate | baseline | 3.468000 | 3.732000 | -3.232000 | -2.968000 |
| A | candidate | candidate | 0.456000 | 0.744000 | -0.244000 | 0.044000 |
| B | baseline | baseline | -0.120000 | 0.120000 | 0.380000 | 0.620000 |
| B | baseline | candidate | -3.432000 | -3.168000 | 3.668000 | 3.932000 |
| B | candidate | baseline | 3.768000 | 4.032000 | -3.532000 | -3.268000 |
| B | candidate | candidate | 0.456000 | 0.744000 | -0.244000 | 0.044000 |

### 100bb — fitting depth

| Run | Player replaced | Fixed opponent | Mean bb | Primary lower bb | Primary upper bb | Negative deals % |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | BB | baseline BTN | 6.000000 | 4.078258 | 7.921742 | 0.0000 |
| A | BB | candidate BTN | 6.000000 | 4.078258 | 7.921742 | 0.0000 |
| A | BTN | baseline BB | 5.000000 | 3.078258 | 6.921742 | 0.0000 |
| A | BTN | candidate BB | 5.000000 | 3.078258 | 6.921742 | 0.0000 |
| B | BB | baseline BTN | 6.500000 | 4.578258 | 8.421742 | 0.0000 |
| B | BB | candidate BTN | 6.500000 | 4.578258 | 8.421742 | 0.0000 |
| B | BTN | baseline BB | 5.500000 | 3.578258 | 7.421742 | 0.0000 |
| B | BTN | candidate BB | 5.500000 | 3.578258 | 7.421742 | 0.0000 |

| Run | Player | Fixed opponent | Loss p95 bb | Loss p99 bb | Worst loss bb | Mean positive loss bb |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | BB | baseline BTN | -5.982000 | -5.980400 | -5.980000 | 0.000000 |
| A | BB | candidate BTN | -5.982000 | -5.980400 | -5.980000 | 0.000000 |
| A | BTN | baseline BB | -4.982000 | -4.980400 | -4.980000 | 0.000000 |
| A | BTN | candidate BB | -4.982000 | -4.980400 | -4.980000 | 0.000000 |
| B | BB | baseline BTN | -6.482000 | -6.480400 | -6.480000 | 0.000000 |
| B | BB | candidate BTN | -6.482000 | -6.480400 | -6.480000 | 0.000000 |
| B | BTN | baseline BB | -5.482000 | -5.480400 | -5.480000 | 0.000000 |
| B | BTN | candidate BB | -5.482000 | -5.480400 | -5.480000 | 0.000000 |

| Run | BB policy | BTN policy | BB min bb | BB max bb | BTN min bb | BTN max bb |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | baseline | baseline | -0.200000 | 0.200000 | 0.300000 | 0.700000 |
| A | baseline | candidate | -5.220000 | -4.780000 | 5.280000 | 5.720000 |
| A | candidate | baseline | 5.780000 | 6.220000 | -5.720000 | -5.280000 |
| A | candidate | candidate | 0.760000 | 1.240000 | -0.740000 | -0.260000 |
| B | baseline | baseline | -0.200000 | 0.200000 | 0.300000 | 0.700000 |
| B | baseline | candidate | -5.720000 | -5.280000 | 5.780000 | 6.220000 |
| B | candidate | baseline | 6.280000 | 6.720000 | -6.220000 | -5.780000 |
| B | candidate | candidate | 0.760000 | 1.240000 | -0.740000 | -0.260000 |

### 150bb — held out from fitting

| Run | Player replaced | Fixed opponent | Mean bb | Primary lower bb | Primary upper bb | Negative deals % |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | BB | baseline BTN | 9.000000 | 6.119782 | 11.880218 | 0.0000 |
| A | BB | candidate BTN | 9.000000 | 6.119782 | 11.880218 | 0.0000 |
| A | BTN | baseline BB | 7.500000 | 4.619782 | 10.380218 | 0.0000 |
| A | BTN | candidate BB | 7.500000 | 4.619782 | 10.380218 | 0.0000 |
| B | BB | baseline BTN | 9.750000 | 6.869782 | 12.630218 | 0.0000 |
| B | BB | candidate BTN | 9.750000 | 6.869782 | 12.630218 | 0.0000 |
| B | BTN | baseline BB | 8.250000 | 5.369782 | 11.130218 | 0.0000 |
| B | BTN | candidate BB | 8.250000 | 5.369782 | 11.130218 | 0.0000 |

| Run | Player | Fixed opponent | Loss p95 bb | Loss p99 bb | Worst loss bb | Mean positive loss bb |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | BB | baseline BTN | -8.973000 | -8.970600 | -8.970000 | 0.000000 |
| A | BB | candidate BTN | -8.973000 | -8.970600 | -8.970000 | 0.000000 |
| A | BTN | baseline BB | -7.473000 | -7.470600 | -7.470000 | 0.000000 |
| A | BTN | candidate BB | -7.473000 | -7.470600 | -7.470000 | 0.000000 |
| B | BB | baseline BTN | -9.723000 | -9.720600 | -9.720000 | 0.000000 |
| B | BB | candidate BTN | -9.723000 | -9.720600 | -9.720000 | 0.000000 |
| B | BTN | baseline BB | -8.223000 | -8.220600 | -8.220000 | 0.000000 |
| B | BTN | candidate BB | -8.223000 | -8.220600 | -8.220000 | 0.000000 |

| Run | BB policy | BTN policy | BB min bb | BB max bb | BTN min bb | BTN max bb |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | baseline | baseline | -0.300000 | 0.300000 | 0.200000 | 0.800000 |
| A | baseline | candidate | -7.830000 | -7.170000 | 7.670000 | 8.330000 |
| A | candidate | baseline | 8.670000 | 9.330000 | -8.830000 | -8.170000 |
| A | candidate | candidate | 1.140000 | 1.860000 | -1.360000 | -0.640000 |
| B | baseline | baseline | -0.300000 | 0.300000 | 0.200000 | 0.800000 |
| B | baseline | candidate | -8.580000 | -7.920000 | 8.420000 | 9.080000 |
| B | candidate | baseline | 9.420000 | 10.080000 | -9.580000 | -8.920000 |
| B | candidate | candidate | 1.140000 | 1.860000 | -1.360000 | -0.640000 |

### 200bb — fitting depth

| Run | Player replaced | Fixed opponent | Mean bb | Primary lower bb | Primary upper bb | Negative deals % |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | BB | baseline BTN | 12.000000 | 8.161306 | 15.838694 | 0.0000 |
| A | BB | candidate BTN | 12.000000 | 8.161306 | 15.838694 | 0.0000 |
| A | BTN | baseline BB | 10.000000 | 6.161306 | 13.838694 | 0.0000 |
| A | BTN | candidate BB | 10.000000 | 6.161306 | 13.838694 | 0.0000 |
| B | BB | baseline BTN | 13.000000 | 9.161306 | 16.838694 | 0.0000 |
| B | BB | candidate BTN | 13.000000 | 9.161306 | 16.838694 | 0.0000 |
| B | BTN | baseline BB | 11.000000 | 7.161306 | 14.838694 | 0.0000 |
| B | BTN | candidate BB | 11.000000 | 7.161306 | 14.838694 | 0.0000 |

| Run | Player | Fixed opponent | Loss p95 bb | Loss p99 bb | Worst loss bb | Mean positive loss bb |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | BB | baseline BTN | -11.964000 | -11.960800 | -11.960000 | 0.000000 |
| A | BB | candidate BTN | -11.964000 | -11.960800 | -11.960000 | 0.000000 |
| A | BTN | baseline BB | -9.964000 | -9.960800 | -9.960000 | 0.000000 |
| A | BTN | candidate BB | -9.964000 | -9.960800 | -9.960000 | 0.000000 |
| B | BB | baseline BTN | -12.964000 | -12.960800 | -12.960000 | 0.000000 |
| B | BB | candidate BTN | -12.964000 | -12.960800 | -12.960000 | 0.000000 |
| B | BTN | baseline BB | -10.964000 | -10.960800 | -10.960000 | 0.000000 |
| B | BTN | candidate BB | -10.964000 | -10.960800 | -10.960000 | 0.000000 |

| Run | BB policy | BTN policy | BB min bb | BB max bb | BTN min bb | BTN max bb |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | baseline | baseline | -0.400000 | 0.400000 | 0.100000 | 0.900000 |
| A | baseline | candidate | -10.440000 | -9.560000 | 10.060000 | 10.940000 |
| A | candidate | baseline | 11.560000 | 12.440000 | -11.940000 | -11.060000 |
| A | candidate | candidate | 1.520000 | 2.480000 | -1.980000 | -1.020000 |
| B | baseline | baseline | -0.400000 | 0.400000 | 0.100000 | 0.900000 |
| B | baseline | candidate | -11.440000 | -10.560000 | 11.060000 | 11.940000 |
| B | candidate | baseline | 12.560000 | 13.440000 | -12.940000 | -12.060000 |
| B | candidate | candidate | 1.520000 | 2.480000 | -1.980000 | -1.020000 |

### 400bb — fitting depth

| Run | Player replaced | Fixed opponent | Mean bb | Primary lower bb | Primary upper bb | Negative deals % |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | BB | baseline BTN | 24.000000 | 16.327403 | 31.672597 | 0.0000 |
| A | BB | candidate BTN | 24.000000 | 16.327403 | 31.672597 | 0.0000 |
| A | BTN | baseline BB | 20.000000 | 12.327403 | 27.672597 | 0.0000 |
| A | BTN | candidate BB | 20.000000 | 12.327403 | 27.672597 | 0.0000 |
| B | BB | baseline BTN | 26.000000 | 18.327403 | 33.672597 | 0.0000 |
| B | BB | candidate BTN | 26.000000 | 18.327403 | 33.672597 | 0.0000 |
| B | BTN | baseline BB | 22.000000 | 14.327403 | 29.672597 | 0.0000 |
| B | BTN | candidate BB | 22.000000 | 14.327403 | 29.672597 | 0.0000 |

| Run | Player | Fixed opponent | Loss p95 bb | Loss p99 bb | Worst loss bb | Mean positive loss bb |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | BB | baseline BTN | -23.928000 | -23.921600 | -23.920000 | 0.000000 |
| A | BB | candidate BTN | -23.928000 | -23.921600 | -23.920000 | 0.000000 |
| A | BTN | baseline BB | -19.928000 | -19.921600 | -19.920000 | 0.000000 |
| A | BTN | candidate BB | -19.928000 | -19.921600 | -19.920000 | 0.000000 |
| B | BB | baseline BTN | -25.928000 | -25.921600 | -25.920000 | 0.000000 |
| B | BB | candidate BTN | -25.928000 | -25.921600 | -25.920000 | 0.000000 |
| B | BTN | baseline BB | -21.928000 | -21.921600 | -21.920000 | 0.000000 |
| B | BTN | candidate BB | -21.928000 | -21.921600 | -21.920000 | 0.000000 |

| Run | BB policy | BTN policy | BB min bb | BB max bb | BTN min bb | BTN max bb |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | baseline | baseline | -0.800000 | 0.800000 | -0.300000 | 1.300000 |
| A | baseline | candidate | -20.880000 | -19.120000 | 19.620000 | 21.380000 |
| A | candidate | baseline | 23.120000 | 24.880000 | -24.380000 | -22.620000 |
| A | candidate | candidate | 3.040000 | 4.960000 | -4.460000 | -2.540000 |
| B | baseline | baseline | -0.800000 | 0.800000 | -0.300000 | 1.300000 |
| B | baseline | candidate | -22.880000 | -21.120000 | 21.620000 | 23.380000 |
| B | candidate | baseline | 25.120000 | 26.880000 | -26.380000 | -24.620000 |
| B | candidate | candidate | 3.040000 | 4.960000 | -4.460000 | -2.540000 |

## Verification scope

The independent reader checks 256 reconstructed training chance cycles, 896 evaluation archives, 28 complete preflop catalog CPU-reference replays and 14 first/last test-batch replays. It shares the native payoff oracle and does not replay every postflop policy row.

All four frozen banks use played generations 0–63, weights 1–64 and exclude unplayed generation 64. Test results do not select a checkpoint. The preserved JSON contains the original full precision statistics, including exploratory normal intervals, which do not replace the primary gate.

This comparison does not qualify complete preflop accuracy, flexible multiway play, GTO Wizard agreement or production readiness. Range behavior and supported hand changes still require plain-English analysis.
