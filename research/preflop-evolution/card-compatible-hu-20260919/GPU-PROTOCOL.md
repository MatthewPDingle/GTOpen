# GPU parity gate for the small reference game

Use the same three frozen matrices and exactly 1,000 alternating CFR+
iterations. Each GPU block owns one game, keeps both strategies in shared
memory, and retains the joint chance weights in every action value. Float32
arithmetic. The CPU/LP reference remains unchanged.

Pass gates: all probabilities finite and in [0,1]; compatible-game two-sided
best-response gap <=0.001bb; value within that gap of the independently certified
linear-program value. Report strategy differences from the same-iteration
double-precision reference, but do not use a zero-reach hand's arbitrary
policy as a value/accuracy criterion. Zero-range hands must remain finite.

Run only while production is idle. No server integration. Record compile and
execution times separately, input/source/binary hashes, and all policies.
This tiny three-block workload is a correctness prototype, not evidence of
speed or memory cost in the full multiway preflop tree. Do not claim a production
speedup from its timing.
