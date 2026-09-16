# N13: opponent-equity distribution features

Specified before fitting. The expanded-data experiments did not improve their
fixed original validation cases. This separate experiment keeps the original
26 training/development contexts and tests one missing-information hypothesis:
two opponent ranges can give a hand the same average preflop equity but very
different distributions of matchup strength.

Retain the original 104 shape features and add the compatible-opponent-weighted
second, third and fourth raw moments of cached pairwise equity for each hand.
For each moment append itself and its products with equity, pair, suited, IP
and log(1+SPR): 18 new features, 122 total. These use no flop or outcome inputs.
Keep ridge penalty 0.1 and the existing compatible-mass centering at inference.
There is one candidate, no feature or penalty grid, and no expanded-data fit.

Exclude each whole source family in four folds. Reproduce the original
shape/0.1 control on the same 26 cases. Require at least 5% lower equal-family
mean error and no family more than 5% worse. Do not modify this feature set or
threshold after seeing its result. If eligible, fit all 26 and freeze before
fresh evaluation. Register against all 400 still-unused expanded-validation
queries (50 boards across eight contexts), never the N09 outcomes being
generated earlier. Require at least 15% lower mean error than Balanced in
each evaluation family and no individual case over 10% worse than the
original conditional predictor, retaining the existing prospective gates.

The moments can share the existing GPU equity-averaging loop; they need not
add another matrix traversal or shared arrays. This is only an implementation
hypothesis. A qualified model needs an independent GPU arithmetic oracle,
repeated runtime measurements and changed-policy validation. No deployment or
full-game convergence claim follows from this training screen.

Do not fit or run numerical tests while N04's GPU timing benchmark is active.
Preparing source files is allowed; fitting waits until reference generation
resumes. The original ten-hour deadline remains fixed.
