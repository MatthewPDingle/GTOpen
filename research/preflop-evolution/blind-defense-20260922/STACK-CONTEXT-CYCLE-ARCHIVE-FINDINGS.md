# Complete-cycle evidence can be retained losslessly

The archive control completed successfully in 836.313 seconds. It read the
previously verified native cycle, made new owned copies, compressed those copies,
and authenticated every restored original byte stream. It created no poker
labels, trained no models and left every original research file unchanged.

The 2,955 cycle files contained 5,705,964,390 original bytes. Their XZ bundles use
124,090,308 bytes, a 45.98-fold reduction. Including manifests and control metadata,
the new retained store occupies 125,135,511 allocated bytes. This is a measured
single-cycle storage result, not a promise for every future training cycle.

The control deliberately changed a copied file and confirmed that retirement
was refused without removing any raw file. After restoring the copy, it interrupted
retirement after seven files, then authenticated the durable archives and safely
finished removing only the remaining exact new duplicates. The unchanged legacy
originals were rehashed again at the end. No historical store was cleaned up.

The initial scheduler took 700.656 seconds for compression and readback, after
72.172 seconds of inventory/copy setup. Its four-job wave barriers can leave
workers waiting for the slowest member of a wave. A separately versioned dynamic
scheduler uses the same codec and retirement verifier, but queues independent
jobs continuously. Its separate check must pass before it is used for training;
the initial result alone is not evidence for that scheduler.

The dynamic scheduler subsequently passed its separate check on the eight largest
jobs, totaling 891,401,793 raw bytes. Every compressed bundle was byte-identical
to its retained baseline counterpart. Compression plus readback took 49.734
seconds and 154.359 CPU seconds, averaging 3.10 CPU cores; the whole check took
55.078 seconds. This was not a matched wall-time benchmark of both schedulers.
Its new retained store occupies 16,437,354 allocated bytes. Original files remain
unchanged. The study controller now uses this qualified dynamic scheduler.

The learning comparison must keep archive indexes, model/checkpoint identities
and final played-bank selection. Space savings are an implementation improvement,
not evidence that the poker model is more accurate.
