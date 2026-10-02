# Complete native output bounds and runner integration

The research runner now accounts for native files written directly to disk,
as well as stdout and stderr. Separate export-only Rust variants check the
serialized aggregate size before opening or writing any output. The board
ceiling is 2 GB; bridge, trace and river ceilings are 64 MB. A 256-byte failure
reserve is included. A requested ceiling can only tighten the fixed ceiling.

This prepares a larger resource profile. It is not evidence of accurate poker
ranges, convergence, a training speedup, or production readiness.

## What was checked

- Two isolated offline builds preserve each original exporter's feature graph.
  Board, bridge and trace use the original default serde_json graph; river uses
  the original continuation-transfer-research / float_roundtrip graph. Original
  sources and executables remain unchanged.
- Thirty-nine actual child invocations passed. Seven retained poker fixtures
  produced identical original bytes at the inclusive and one-byte-extra limits.
  At one byte below the required aggregate, they wrote no payload and retained
  only the fixed error. Direct files use create_new. Large error/panic messages,
  invalid limits, collisions and the river's existing input limits were checked.
- The independent retained audit rehashed the output, source, feature and
  ownership evidence. All 39 child PID/creation identities are distinct; up to
  six native children overlapped. Padded admitted river inputs preserve the
  entire original JSON result after removing only the echoed padding.
- Native execution v2 controls check complete direct-output receipts and refuse
  missing files, partial/nonzero exits, overages, timeout/cancellation and changed
  sources, budgets, hashes, paths or schemas. It is an acceptance/polling bound,
  not a filesystem quota by itself.
- Board worker controls and river call-path controls qualify the v2 wiring.
  Pipeline controls admit one valid result and refuse 118 invalid results;
  three synthetic full-domain draws preserve RNG/scientific state. Native
  verification in those pipeline controls is mocked; they are not a full cycle.
- Source parity reviews preserve target calculations, sampling, action and
  retention RNGs, fitting and scientific selection logic. Prospective contracts
  explicitly tighten board limits to 256..2,000,000,000 bytes and require exact
  v2 envelopes rather than admitting older or malformed results.

The original uncompiled declaration-placement defect and the first river
control's incorrect final verification-count assertion are retained. The latter
changed only a separate control, not implementation or scientific inputs. No
started scientific attempt was retried.

## Evidence and limits

The compact evidence directory records exact original/copy identities and pins
excluded large payloads in their retained stores. Raw native controls remain in
S:\GTOpen-research\native-bounded-export-controls-v1 and builds in
S:\GTOpen-research\native-bounded-export-build-v1. No old files were compressed,
linked, moved or deleted.

The helper serializes in memory before checking the byte gate, so this does not
bound peak RAM or CPU work. Nonriver input reads retain their previous bounds;
no new input-size ceiling was added. Python-generated policies, events and
other derived outputs still need their own admission reserve. Bridge walk is
outside the seven retained parity fixtures and unused by the qualified runner.
Disk-full, partial-write and abrupt-kill injection were not
tested. Named allocated file sizes do not include all filesystem metadata.
Collision identities were checked live but their before/after records were not
persisted. The general native receipt's observed_argv is the owned Popen vector,
not an OS command-line attestation; four small Python wiring controls separately
checked OS command lines. The helper compiler has no process-creation receipt.
Finite retained-fixture parity is not a guarantee for every future context.
Future configurations must pin the new repository paths and bounded executable
identities; historical receipts keep their original paths and identities.

The next admission needs a fresh inventory under the global 800 GB budget,
explicit six-child and derived-output/metadata reserves, then one genuine full
cycle at 20/40/100/200/400bb with both CUDA fits and checkpoint restoration.
Only afterward can sufficiently sampled independent stability/payoff research
be registered. K2/F4 resource checks cannot establish poker accuracy.

Full preflop accuracy, stack-specific openings, five-bets, additional positions,
multiway/Wizard validation and deployment remain outstanding. Production on
56708 is unchanged. No GitHub push or deployment is part of this publication.
