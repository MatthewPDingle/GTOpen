# Full-study operational recovery prepared

The qualified two-thread runtime and closed-port-aware storage inventory are
available to the later admission and continuation stages through
`board_full_resource_wrapper_v1.py`. This wrapper invokes the existing frozen
scientific drivers. It changes only their global inventory dependency for
that process and preserves their own gates and limits.

Default commands only check readiness. Actual admission or training requires
`--run`. Training resume additionally requires `--resume --attempt <name>`
with a distinct attempt name, so each invocation retains its own registration
and failure/completion record. A completed scientific output cannot be
overwritten. The prefix, its independent review, its terminal recovered queue
and the wrapper's qualification must all exist and pass before work begins.

The admission stage records one genuine global inventory and matches it to
the original measured projection. The training stage records its original
driver's initial and final inventories. No compression credit, new sample
selection or larger budget is introduced. The fixed endpoint remains 78
generations per arm; no full run has been admitted by preparing this wrapper.

`board_matched_complete_readback_v2.py` uses the same version 2 sequence reader
qualified on the bounded control. Its independent calculations and numerical
tolerances remain unchanged. Actual full readback still requires both
completed 78-generation arms and the passed prefix reviews.

Readiness checks correctly reported the missing completed prefixes, audits,
storage admission and full training results. No admission, GPU training or
full audit was launched by these preparation checks.
