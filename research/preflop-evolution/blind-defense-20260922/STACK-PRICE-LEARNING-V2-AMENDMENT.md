# Pre-training implementation correction

Version 1 stopped during the retained-native feature check, before board
preparation, fitting, validation or final testing. It treated NumPy's integer
maximum property as a callable, raising TypeError in card_factors.

Version 2 changes only `np.iinfo(np.int64).max()` to
`np.iinfo(np.int64).max` in a separately named data module. The runner imports
that corrected module and writes to a separate v2 study directory. Preserve the
v1 sources, registration, admission and interruption evidence unchanged.

The reference, seeds, board splits, initialization, optimizer, update budget,
validation selection, final-test roles, thresholds and resource caps are
unchanged. Version 1 performed zero training updates and viewed no test labels.
This is a pre-training bug correction, not an extension after seeing learning
results. V2 is capped at one hour including its own storage admission.
