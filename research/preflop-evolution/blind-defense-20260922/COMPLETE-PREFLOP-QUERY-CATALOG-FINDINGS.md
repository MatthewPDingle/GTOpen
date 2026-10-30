# Complete preflop query catalog: native history checks passed

The existing 6,630-row native holding catalog covers all 1,326 physical holdings
at each of five preflop decisions. It reduces to 845 canonical decision/class
rows. Every physical holding in each class produced identical native observation
keys and features, including the neural-fallback inputs.

The new query builder retains 699 rows on the actual incoming support: 169 BB
classes at three decisions and 96 BTN classes at two decisions. Unsupported BTN
classes are omitted using the context-bound pair-mass matrix. This does not
change the incoming ranges or silently invent a policy for absent classes.

Own-action histories were reconstructed from the registered tree. The native
bank-query exporter, rerun on 128 already retained training deals, independently
agreed on 488 preflop observations and 220 ancestor/action links. Six malformed
catalog/context cases were rejected. Control v3 took approximately 2.30 seconds,
used no GPU and generated no new poker deals.

This closes the query-construction step only. Complete 110-model-bank inference,
conditional terminal/reach decomposition, sampling weights, numerical bounds and
fresh payoff evaluation remain to be qualified. The model's original root
catalog and inference implementation are unchanged; the new catalog supplies
queries rather than replacing model metadata.

## Preserved fixture failures

- Control v1 used saved training queries, which lack own_history. Its comparison
  stopped with KeyError before producing a successful result.
- Control v2 invoked the appropriate bank-query exporter but copied format 3
  from the labelled all-in batch. The exporter requires raw format 2 and refused
  it before inference.
- Control v3 explicitly exports an unlabelled format-2 batch containing the same
  retained deal arrays, IDs and seeds. Hidden all-in labels are excluded. The
  catalog-builder implementation did not change between these controls.

Earlier registrations, sources and partial artifacts remain available. Neither
failed fixture attempt is evidence against poker behavior or a hidden retry of
a statistical test.

Result: complete-preflop-query-catalog-control-v3-result.json.
Registration SHA256: 1ddad1d260ba19fde69a3fa15d90de23e9b7cda69a069111572cd808a5bb5001.
Query catalog SHA256: 903dab1aecf7c73045eca272d27d1d49cf53ee6821337ffe2fdd8103468ba38b.
See REACH-WEIGHTED-EVALUATION-DESIGN.md for the prospective estimator and remaining gates.
