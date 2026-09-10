# Forced-policy GPU memory accounting proposal

The constructor currently materializes `forced`, uploads it as `d_forced`, but
does not reserve its bytes in `need`. The CDF batch planner and optional equity
cache can therefore consume that same budget. Legacy games are affected too.
The measured six-seat source has a 1,247.57 MB single arena; forced-policy
payload is bounded by that arena but is not necessarily small.

Apply `forced-policy-budget.patch` to the isolated lab when ready, and append
`tests.rs` to its gpu.rs. No active source was edited and no build/GPU test was
run to prepare this proposal. `proposal.json` pins the source used for the diff.

The constructor reserves the already materialized vector's actual payload
before selecting CDF batches or the optional equity cache. It rejects a budget
exceeded by base plus forced storage even for the legacy model. The one-float
placeholder is also counted when the vector is empty. Overflow fails closed.

The public estimate obtains the same element count through the canonical
`forced_sigma` routing, streaming one node at a time. Peak extra temporary policy
storage is one node's actions × 169 floats, rather than another concatenated
forced table. This can cost CPU time on large modeled trees and can populate the
existing bounded contextual cache; measure estimator/init separately. Do not
duplicate the intricate profile/adaptive/hero/point-lock precedence in a new
allocation-free predicate merely for speed. A later shared routing abstraction
could avoid transient allocations safely if profiling shows this matters.

The proposal keeps kernel code, policies, precision and game rules unchanged.
For fair performance comparisons, put this common accounting fix on both the old
kernel control and compact candidate. Record forced bytes, batch width and cache
choices. A smaller legal batch can change floating-point addition order, so use
the existing numerical arena/EV/gap and time-to-accuracy gates where appropriate.

Proposed host-only checks cover profile versus frozen storage, hero exemption,
point-lock precedence/no double counting, adaptive nodes, exact byte limits,
overflow, smaller batches, direct-normalization fallback and no-particle fallback.
After these compile/pass, also verify actual CUDA `d_forced.len()*4` equals the
reserved count in one small modeled fixture, check refusal at a constructed
budget boundary, and run existing numerical tests for both cache paths.
