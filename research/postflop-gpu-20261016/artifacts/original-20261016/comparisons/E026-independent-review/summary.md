# E026 independent terminal review

CONFIRMED_REJECTED. The registered score rose from9,520.4104ms to10,051.9586ms, a5.5832488% slowdown (gain-5.5832488%). All three paired aggregate comparisons were slower. The>=2% gain gate fails.

| Fixture | Median complete-cycle regression | Pairs over3% slower | Guard |
|---|---:|---:|---|
| Rainbow | +5.9049642% |3/3|Failed|
| Two-tone | +5.4316372% |3/3|Failed|
| River | -7.1626322% |1/3|Passed|

All18 complete non-timing results and138 convergence checks/complete stage trajectories match exactly. The unchanged unit inventory passed84 tests with4 ignored. Fixed order, quality target, stops200/200/60, all samples, fresh build artifacts, embedded candidate CUDA, script/authorization/D050/D051 pins, source maps, binary/log hashes and patch alias are consistent. No exclusions or extensions occurred.

Descriptive component medians show solve+329.5016ms on rainbow and+193.2919ms on two-tone; every paired solve was slower on those fixtures. River solve was1.4749ms lower and init5.0113ms lower. Component medians need not sum to the median complete cycle, and these observations do not establish a device-level cause or justify a scoped rescue.

The active candidate162-file map was captured before restoration: only kernels.cu and mod.rs differed from accepted E020. The pinned cleanup record and independent file recheck confirm all162 accepted source hashes restored. Root's cleanup record also confirms the original live executable unchanged and zero broader/holdout/cumulative executions or extensions.

The first reviewer-only audit retained an inherited V025-unit selector and therefore selected the wrong expected manifest for V026-unit. Its script/logs remain preserved. The additive R2 repair changes only that spelling and passes939 file assertions over115 pinned audit inputs. No native run, measurement, evaluated source or frozen evidence changed.

This closes the fixed compressed primary screen. D051's scoped exact-kernel pass remains valid evidence but is not a performance result. Broader original/F32/GPU/continuation controls, wide-turn and cumulative qualification were not run because this screen failed. E026 is neither accepted nor deployed.
