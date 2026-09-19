# Additional lossless host compression feasibility

The measured SSD can provide capacity, but the current every-player whole-record spill would read and write 80 TB each over 2,000 iterations with 20 GB cold state. At the bounded physical test's measured speed, I/O alone projects to about 30 hours, before solver work. This is a projection, not a sustained drive benchmark, and does not authorize that write volume.

While connected storage equivalence runs, examine completed immutable strategy snapshots for further exact in-RAM savings. Start with all six 60-iteration SSD parity states. Then repeat on the connected gate's completed 20-iteration full-support SSD states after its writer has exited. Do not inspect files while they are being replaced.

For each of four F32 arrays, measure: raw byte count; exact positive-zero-word masking (one 32-bit presence mask per 32 words, retain every nonzero bit pattern verbatim, use raw fallback if packing would expand); and standard-library zlib level 1 compression/decompression time and size. The Python masking analysis is a size forecast, not a native runtime benchmark. Preserve negative zero and every nonzero bit pattern. For zlib require full byte equality on decompression. Record source SHA256, snapshot iteration and lengths. No rounding, precision reduction, hand pruning or changes to the game are allowed.

Early snapshots may compress much better than mature learning state. These measurements can justify implementing and testing a lossless codec but cannot establish the full 164-board peak-memory bound, mature compression ratio, or solver speed. Integrating any extra representation requires exact round-trip and connected-game validation plus a raw fallback and explicit capacity guard.
