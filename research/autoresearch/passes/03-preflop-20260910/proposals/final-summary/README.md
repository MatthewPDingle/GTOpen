# Frozen evidence summary generator

`generate.py` reads existing JSON evidence only. It does not run a solver, build code, inspect native saves, hash native data, read the app, or alter the research queue. Default output is stdout; `--output` creates a new file exclusively and refuses to overwrite an existing artifact.

```powershell
python generate.py
python generate.py --output final-summary-new.json
python -m unittest -v test_generate.py
```

Generate to a new path after optional qualifications finish. The published report is `../../final-summary.json`; `--output` refuses to overwrite it. No README or run manifest is modified by the generator.

Required inputs are `final-performance.json`, `extended-convergence-comparisons.json`, `extended-convergence-protocol.json`, three final suite JSONs, the accepted source manifest, and deployment evidence. The generator requires all four exact primary GPU comparisons and both completed, exact extended target comparisons, matching checkpoint sequences/final vectors, finite timings, consistent reductions, and the frozen candidate source/cadence/target. Test counts remain separate because suites overlap. Accepted source/deployment facts are recorded evidence, not freshly checked live state.

Optional `fresh-eight-comparisons.json` is pending until all three pairs exist; no timing headline is emitted early. Complete fresh qualification must have pairs1/2/3 exact, native0→20, checkpoint cadence10, and the recorded0.005bb target misses. It is explicitly fixed work, not convergence time.

Optional API input defaults to `api-first-strategy-eight-a.json` in the pass root. Use `--api-summary <completed-summary.json>` to read the completed isolated API result directly. It requires the exact-native and fixed-pair markers plus finite original/candidate checkpoint and strategy-response times. It preserves the evidence's polling/fixed-pair interpretation and claims no general API speedup. An explicitly requested missing file is an error.

Optional budget qualifications are `api-auto-modeled-b.json` and `api-modeled23000-a.json`. If either is published, both must be present and fully completed/exact. The generator checks their specific23924MB/B32/HU-on and23000MB/B31/HU-off outcomes, original resolved budget, candidate literal-reference agreement, allocation bounds, per-case completion/guards, and polling intervals. It reads each copied raw case JSON sequentially to derive native0→2 and check role plus metadata preservation except iteration. It does not read the native files referenced inside those JSONs. The earlier23GB harness timeout remains a separate failed experiment; successful short API checks are not convergence results or an explanation of the failure.

For pass evidence, an adjacent `.json.gz` takes precedence over `.json`. The actual compressed path is recorded in `evidence_sources` and raw-case checks. This allows publication of the losslessly compressed large qualification metadata; no conversion or hashing is performed by the generator. The existing proposal summary snapshot predates these optional additions and is intentionally not regenerated automatically.

Validation: all seven pre-compression tests passed against the complete uncompressed raw evidence, including actual recorded native0→2 checks. Eight current unittest cases pass with small synthetic raw-case fixtures for repeated tests, preserving direct invalid-role/metadata/iteration/budget/outcome guards and adding gzip exact-value loading. Primary/extended refusal tests, incomplete fresh qualification, synthetic API rejection and existing-output preservation remain covered. No pass-root summary was created. These are generator tests, not solver tests, and must not be added to solver validation counts.
