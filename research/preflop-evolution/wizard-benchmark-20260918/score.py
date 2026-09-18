"""Validate UI captures and score explicitly matched, hand-level candidates.

No browser access, live-server calls, model fitting or solver invocation.
Run with no argument to validate captures; pass a candidate JSON to score.
"""
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent


def finite(value):
    x = float(value)
    if not math.isfinite(x):
        raise ValueError("Nonfinite value")
    return x


def canonical_hand(combo):
    cards = combo.split("_")[-1]
    if len(cards) != 4:
        raise ValueError("Invalid combo identity")
    a, sa, b, sb = cards
    return a + b + ("" if a == b else "s" if sa == sb else "o")


def references(capture):
    result = {}
    for case in capture["cases"]:
        if case["id"] in result:
            raise ValueError("Duplicate case")
        hands = {}
        for probe in case["probes"]:
            hand = probe["hand"]
            combos = probe["combos"]
            expected = 6 if len(hand) == 2 else 4 if hand.endswith("s") else 12
            if len(combos) != expected or len({c["combo"] for c in combos}) != expected:
                raise ValueError("Incomplete or duplicate combo coverage: " + hand)
            normalized = []
            for combo in combos:
                if canonical_hand(combo["combo"]) != hand:
                    raise ValueError("Wrong hand captured: " + hand)
                actions = {}
                for action in combo["actions"]:
                    name = action["action"]
                    if name in actions:
                        raise ValueError("Duplicate action")
                    p = finite(action["percent"].removesuffix("%")) / 100
                    if not 0 <= p <= 1:
                        raise ValueError("Invalid probability")
                    actions[name] = {"p": p, "ev": finite(action["ev"])}
                if abs(sum(a["p"] for a in actions.values()) - 1) > 0.00021:
                    raise ValueError("Probabilities do not sum to one")
                normalized.append(actions)
            if any(a != normalized[0] for a in normalized):
                raise ValueError("Suit-specific values require combo-level scoring")
            if hand in hands:
                raise ValueError("Duplicate hand")
            hands[hand] = normalized[0]
        result[case["id"]] = hands
    return result


def score(capture, candidate):
    refs = references(capture)
    # The context is an explicit audit record, not a claim that the entire
    # proprietary Wizard tree/postflop abstraction has been reproduced.
    if candidate.get("context") != capture["context"]:
        raise ValueError("Configuration audit differs or is missing; comparison refused")
    rows = []
    seen = set()
    for case in candidate["cases"]:
        key = case["id"]
        if key not in refs or key in seen:
            raise ValueError("Unknown or duplicate case")
        seen.add(key)
        for hand, probs in case["hands"].items():
            ref = refs[key].get(hand)
            if ref is None or set(probs) != set(ref):
                raise ValueError("Hand or legal-action mismatch")
            p = {a: finite(v) for a, v in probs.items()}
            if any(not 0 <= v <= 1 for v in p.values()) or abs(sum(p.values()) - 1) > 1e-6:
                raise ValueError("Candidate probabilities must sum to one")
            evs = {a: v["ev"] for a, v in ref.items()}
            regret = max(evs.values()) - sum(p[a] * evs[a] for a in p)
            rows.append({"case": key, "hand": hand,
                         "local_regret_bb": regret,
                         "rounding_only_interval_bb": [max(0, regret - .01), regret + .01],
                         "frequency_total_variation": sum(abs(p[a] - ref[a]["p"]) for a in p) / 2})
    total = sum(len(hands) for hands in refs.values())
    return {"scored_probes": len(rows), "available_probes": total,
            "complete_probe_coverage": len(rows) == total,
            "interpretation": "Local Wizard-action regret, not exploitability; no population average.",
            "rows": rows}


if __name__ == "__main__":
    capture = json.loads((ROOT / "ui-captures.json").read_text())
    if len(sys.argv) == 1:
        refs = references(capture)
        print(json.dumps({"validated_cases": len(refs),
                          "validated_probes": sum(map(len, refs.values()))}))
    else:
        candidate = json.loads(Path(sys.argv[1]).read_text())
        print(json.dumps(score(capture, candidate), indent=2, allow_nan=False))
