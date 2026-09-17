# Development expansion after failed transfer screening

The initial 18-feature candidate did not beat its unchanged baseline in
leave-one-policy-family-out development screening. Its planned 120-reference
test was not run. Preserve that candidate and protocol; no failed result is
relabeled as a success.

This separate development acquisition adds two deliberately different synthetic
preflop policies: one linear and one with a polar raising component. These are
data-generation fixtures, not claimed GTO strategies or learned player profiles.
Every legal action remains available. Recompute coherent reaches from their
action probabilities and derive the three connected postflop contexts at 40bb.

Generate 60 labels: two policies, three continuations, ten stratified boards
shared across contexts (two per stratum, paired-development-expansion-v1).
This small panel provides development data; it cannot establish final accuracy.
Retain the established postflop tree, zero rake, CPU and GPU gap <=0.1% pot and
2,000-iteration ceiling. Exclude unsettled individual hands from fitting.

For a bounded exploratory screen, compare compact18 and existing range54
centered features, ridge penalties 0.001/0.01/0.1/1, action weights 0/4/100,
and correction strengths 0.25/0.5/1. Include the unchanged baseline explicitly.
Leave each of four policy families out in turn, including the two completed
historical audits. Select only if mean adjusted action MAE improves >=5%, no
family's adjusted action MAE worsens >5%, and mean leaf MAE in each family and
each estimator worsens <=5%. Otherwise stop and report no candidate.

Freeze any selected replacement separately. It must pass a new, separately
registered prospective test before native integration. Neither the original
candidate nor this screen changes the live app on port 56708.
