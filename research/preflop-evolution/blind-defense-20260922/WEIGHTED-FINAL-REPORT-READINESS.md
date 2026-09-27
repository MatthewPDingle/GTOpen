# Final findings report preparation

`tools/research/weighted_final_findings_v1.py` prepares the complete findings
after the fixed evaluation, its independent review, and the full trajectory
diagnostic have finished. It does not inspect intermediate evaluation outcomes
or select policies. Run it manually after checking those completed results:

```text
python tools/research/weighted_final_findings_v1.py
```

It authenticates the registered source inputs and completed result hashes,
requires all 65,536 deals and 2,048 reviewed batches, and includes all eight
payoff contrasts. The rendered report separates cross-seed range consistency,
within-run movement, per-hand coverage and payoff evidence. It reports both
positive and negative interval conclusions and leaves unresolved contrasts
inconclusive. No outcome automatically triggers deployment.

Outputs will include a Markdown findings report, all 169 labeled hand-class
policies and distances, a graph of every gain and interval, and an evidence
manifest. The plot still needs visual inspection once it is generated. The
scientific interpretation and next research decision remain manual work.

Preparation checks reused the prior completed study and synthetic sign changes:
all eight comparisons were retained, all-inconclusive and mixed positive/negative
counts were correct, a missing comparison was rejected, and the current unfinished
study was refused before publication. No current-study result was generated.
The corresponding control artifact binds the report source and reused inputs.
