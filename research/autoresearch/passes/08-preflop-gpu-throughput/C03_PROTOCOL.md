# C03: reuse quadrature products when a warp has no tie mass

Control is retained C01. The multiway terminal evaluates Q products at different
tie-splitting points, then adds Q weighted terms in fixed order. If every live
opponent has exactly zero equal-strength mass, those Q products are identical.
Test a warp-uniform branch that computes the ordered opponent product once and
still performs every original weighted addition in its original order. No sample
is skipped and no accumulation is collapsed. Lanes with any tie mass use the
unchanged product arithmetic. Preload less/equal values so the fast path can be
chosen without changing their computation. This may lose due to registers and
branch overhead; that is what the timing screen must determine.

Use an isolated research kernel and the same native/C01/adversarial comparisons
as C02. Any changed checkpoint/arena bits rejects it. If exact tests pass, run
one large paired six-sweep/two-warmup benchmark from the frozen native save.
Require at least 1% complete-runtime improvement to extend to three large/small
pairs. Final retention still requires >=3% large paired median gain, <=3% small
regression and all required regression suites. No parameter sweep after failure.

Build/test cap 240 seconds; each benchmark 180 seconds. One workload at a time,
run07 live-app guard and immutable inputs. CPU performance excluded; port 56708
unchanged. This targets fixed-work throughput, not convergence per iteration.
