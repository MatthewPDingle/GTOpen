# Probe-weight sensitivity

Registered after the initial 80 references, before this sensitivity experiment.
The first-pass AA continuation values greatly exceed the fast estimate, while
AA is given only a 0.001 range weight. Test whether this result depends on such
a small counterfactual presence. The original precision pass must finish first.

Raise the OOP minimum weight for the same eight probes to 0.01, leaving all
other weights, IP ranges, boards, menus, rake and stacks unchanged. Only AA,
KQo, 55 and 76s change. Record the total added combination mass and require it
to stay below 0.5% of the original prepared OOP mass. Preserve every original
reference. Run all 40 paired flops with both menus, not a favorable subset.

Require both global gaps at most 0.05% pot and each probe's OOP best-response
gain at most 0.05bb; stop at 5000 iterations and review any failure. Estimate
the change in gross postflop values using the same stratified, paired board
bootstrap. The fast-model prices are not recalculated in this diagnostic.
This tests sensitivity to a specified small range change, not robustness to
arbitrary ranges or the full-game correctness of either model.

The range-level fast model allocates the starting pot, whereas postflop hand
values can include future bets. A large AA value is therefore possible, but
its size still needs these numerical and range-weight checks. The experiment
does not by itself resolve AA's preflop 4-bet-versus-jam choice.

Run serially after the precision pass, checking production is idle before each
offline job. Preserve port 56708 and all reserved Wizard cases.
