# N33 stopped at its first accounting check

The run failed before producing any blend scores. Its proposed baseline used
the historical ordinary Balanced comparator from `range_value_pilot.context`.
That comparator averages opponent classes independently; the candidate and
reference weighting use compatible card pairs. Their convex mixture therefore
does not conserve the compatible-pair weighted pot.

Across the 26 inputs the ordinary comparator's weighted total ranges from
0.9894848 to 1.0146916 pots. This does not invalidate earlier comparisons against
ordinary Balanced; it does invalidate N33's claim that both blend endpoints
share compatible-pair accounting.

The frozen protocol and code are retained as failed evidence, without silently
changing the asserted invariant. N34 separately specifies the paired Balanced
endpoint actually used by the experimental GPU interface. No application code,
existing predictor, training labels or previous qualification gate changed.
