# Averaging opponent actions at the BB root: bounded diagnostic

The replicated root-retention runs have unstable hand assignments. Before another
training run, measure the opponent-action noise that can be removed while keeping
the same learned policy and the same physical cards. This is not an accuracy test
and does not authorize replacing either stored model or the production solver.

Use both completed and independently audited root-retention training stores.
Select batch 00 at updates 1, 26, 52 and 78 in each store, without inspecting
their payoffs for selection. Each has 64 saved physical deals, a complete saved
current-policy query table and the exact preflop-all-in labels. The 512 deals
are existing training fixtures, not an independent or class-balanced holdout.

For each of these eight fixed policy/card batches:

1. Run the existing full-expectation profile evaluator on the baseline and four
   forced BB initial actions. It enumerates action paths at the supplied board,
   using the original saved probabilities at every later node. Verify independent
   forward cashflow accounting, conservation and baseline/root mixture identity.
2. Repeat the existing external-sampling native traversal with 16 action RNG seeds
   `358501 + 1000 * fixture_index + replicate`, in fixed fixture order (first run,
   then replication; chronological updates). Alter only the RNG seed and batch ID
   in new transport files; preserve the original physical deals, labels and policy
   rows. Every run uses native verify mode.
3. Recover call and raise payoffs from root advantage plus root value. Compare
   their conditional variation over action seeds with the full-expectation result
   on exactly the same cards/policy. Also report call-minus-raise paired noise.
   Report all fixtures and descriptive pooled metrics; no favorable selection.

The full-expectation value is a deterministic action-tree calculation on a
sampled board, not an exact preflop hand value. Private-card and board sampling
noise, policy approximation error and changing training opponents remain.
The existing exact initial-jam target remains separate; this experiment concerns
non-all-in call/raise estimates. No training, GPU inference, new physical deals,
range prescription or deployment occurs.

Before execution, verify the audited source chain, freeze input hashes and this
plan, verify fresh production-idle status, and measure combined allocated research
storage. Admit at most 2 GB new allocation, 4 GB logical files and a 2 GB reserve
under the global 800 GB ceiling. Create a separate NTFS-compressed output folder.
Stop on the first numerical/resource error; keep all artifacts. Use a 30-minute
wall-clock cap, 40 GB free disk on T:, 20 GB available host RAM, two host math
threads, below-normal process priority, and the shared exclusive research lock.
Do not run concurrently with a production solve. Inspect storage after every
fixture and during seed repetitions. No quality-based extension or early stop.

A separate standard-library reader must verify original/current transport
identities, all output hashes, root values from raw records, complete replication
counts, deterministic/full-expectation values and sample variance calculations.
It must not claim independent verification of the native tree rules or learned
policy inference. Only after this diagnostic and readback may we consider a
separately registered training change.
