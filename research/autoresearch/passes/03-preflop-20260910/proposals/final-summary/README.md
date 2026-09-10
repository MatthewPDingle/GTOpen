# Frozen evidence summary generator

`generate.py` reads existing JSON evidence only. It does not run a solver, build code, inspect native saves, hash native data, read the app, or alter the research queue. Default output is stdout; `--output` creates a new file exclusively and refuses to overwrite an existing artifact.

```powershell
python generate.py
python generate.py --output final-summary-new.json
python -m unittest -v test_generate.py
```

The saved `final-summary.json` is a proposal snapshot, not a live report. Regenerate to a new path after optional qualifications finish. Parent may publish a new file under the pass root using `--output ../../final-summary.json` if that path does not already exist. No README or run manifest is modified.

Required inputs are `final-performance.json`, `extended-convergence-comparisons.json`, `extended-convergence-protocol.json`, three final suite JSONs, the accepted source manifest, and deployment evidence. The generator requires all four exact primary GPU comparisons and both completed, exact extended target comparisons, matching checkpoint sequences/final vectors, finite timings, consistent reductions, and the frozen candidate source/cadence/target. Test counts remain separate because suites overlap. Accepted source/deployment facts are recorded evidence, not freshly checked live state.

Optional `fresh-eight-comparisons.json` is pending until all three pairs exist; no timing headline is emitted early. Complete fresh qualification must have pairs1/2/3 exact, native0→20, checkpoint cadence10, and the recorded0.005bb target misses. It is explicitly fixed work, not convergence time.

Optional API input defaults to `api-first-strategy-eight-a.json` in the pass root. Use `--api-summary <completed-summary.json>` to read the completed isolated API result directly. It requires the exact-native and fixed-pair markers plus finite original/candidate checkpoint and strategy-response times. It preserves the evidence's polling/fixed-pair interpretation and claims no general API speedup. An explicitly requested missing file is an error.

Validation: six Python unittest cases passed, including the current frozen headline derivation, sixteen primary/extended refusal scenarios, incomplete fresh qualification, synthetic API rejection, and existing-output preservation. The proposal summary was generated successfully from the existing evidence. These are generator tests, not solver tests, and must not be added to solver validation counts.
