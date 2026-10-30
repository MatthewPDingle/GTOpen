"""Decode all declared D291 raw words after the separately authorized GPU run.

This script starts no subprocess. It needs one family, its staged source folder,
an S: raw directory and an S: JSON report path. It is not a timing assessment.
"""
from pathlib import Path
import hashlib
import json
import struct
import sys

checks = 0


def req(value, message):
    global checks
    assert value, message
    checks += 1


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


class Reader:
    def __init__(self, path, magic):
        self.data = path.read_bytes()
        req(self.data.startswith(magic), "raw magic")
        self.at = len(magic)

    def id(self):
        req(self.at + 4 <= len(self.data), "record id bounds")
        value, = struct.unpack_from("<I", self.data, self.at)
        self.at += 4
        return value

    def vec(self):
        req(self.at + 8 <= len(self.data), "vector header bounds")
        length, = struct.unpack_from("<Q", self.data, self.at)
        self.at += 8
        req(length <= 2_000_000 and self.at + 4 * length <= len(self.data), "array bounds")
        value = memoryview(self.data)[self.at:self.at + 4 * length].cast("I")
        self.at += 4 * length
        return value

    def eof(self):
        req(self.at == len(self.data), "complete raw endpoint")


def equal(actual, expected, label):
    req(list(actual) == list(expected), label)


def fold_expected(s):
    meta = s["node_meta"]
    return [s["nodes"], [m["owner"] for m in meta],
            [m["twin_bits"] for m in meta], [m["tlose_bits"] for m in meta],
            s["rsrc0"], s["rsrc1"], s["reach0_bits"], s["reach1_bits"],
            s["pc1"] or [0x4b123456], s["pc2"] or [0x4b123456],
            s["card_off"], s["card_idx"] or [0x4b123456],
            s["same_p"] or [0x4b123456], s["cfv_slot"]]


def main():
    req(sys.byteorder == "little", "raw reader endianness")
    req(len(sys.argv) == 5, "family/source/raw/report arguments")
    family, source, raw, output = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
    req(family in {"up-action", "down-action", "up-action-eval", "up-fold"}, "known family")
    root = Path(r"X:\Dev\GTOpen-research\postflop-gpu-20261028").resolve()
    req(raw.resolve().is_relative_to(root) and output.resolve().is_relative_to(root), "bulk evidence stays on X")
    req(not output.exists(), "immutable new report")
    corpus = json.loads((source / "corpus.json").read_text(encoding="utf-8"))
    prep = json.loads((source / "preparation.json").read_text(encoding="utf-8"))
    for name, expected in prep["input_sha256"].items():
        req(sha(source / name) == expected, "prepared source hash: " + name)
    prefixes = {"up-action": b"D291_UP_", "up-action-eval": b"D291_EVAL_", "up-fold": b"D291_FOLD_"}
    if family == "down-action":
        magic = [b"D291-DOWN-IN1\0\0\0", b"D291-DOWN-OUT1\0\0", b"D291-DOWN-IM1\0\0\0"]
    else:
        prefix = prefixes[family]
        magic = [prefix + b"IN1", prefix + b"OUT1", prefix + b"IM1"]
    inp = Reader(raw / "inputs.bin", magic[0])
    base = Reader(raw / "baseline.bin", magic[1]); cand = Reader(raw / "candidate.bin", magic[1])
    bi = Reader(raw / "baseline-inputs.bin", magic[2]); ci = Reader(raw / "candidate-inputs.bin", magic[2])
    req(base.data == cand.data, "all baseline/candidate output bytes equal")
    req(bi.data == ci.data, "all actual immutable device bytes equal between arms")
    output_words = immutable_words = guards = required_finite = nonzero = 0
    for index, case in enumerate(corpus["cases"]):
        req(case["id"] == index, "declared case order")
        for reader in [inp, base, cand, bi, ci]:
            req(reader.id() == index, "actual case order")
        descriptor = inp.vec()
        fields = 14 if family == "up-fold" else 13
        imm = [inp.vec() for _ in range(fields)]
        if family in {"up-action", "up-action-eval"}:
            equal(descriptor, case["descriptor"], "actual action descriptor")
            nh, na, role, count = case["hands"], case["actions"], case["role"], case["count"]
            nn, stride = na + 8, nh + 5
            req([len(v) for v in imm] == [3, nn, nn, 2*nn, nn, na+4, nn, 6*max(nh, 1)+7, 2*nn, 5+na*nh+17, nn, 3, nn], "action immutable geometry")
            req(all(p <= 255 and a <= 255 and packed == ((p << 8) | a) for p, a, packed in zip(imm[1], imm[2], imm[12])), "lossless actual packed action metadata")
            equal(imm[11], case["discount_bits"], "actual discounts, unused during evaluation")
            req(imm[0][1] == 2 and imm[1][2] == (1-case["p"] if role == 2 else case["p"]) and imm[2][2] == na, "actual parent and byte fields")
            req(imm[3][4] == 13 and imm[3][5] == 0 and imm[4][2] == 2 and imm[6][2] == 3, "actual action offsets")
            equal(imm[5][2:2+na], range(4, 4+na), "actual children")
            equal(imm[10][4:4+na], reversed(range(4, 4+na)), "permuted physical child rows")
            req(imm[10][2] == 2 and all(imm[10][2] != imm[10][x] for x in imm[5][2:2+na]), "parent/child CFV disjoint")
            equal(imm[8][4:6], [5, 0] if role == 1 else [0xffffffff, 0xffffffff], "actual lock branch")
            seeds = [inp.vec() for _ in range(3)]
            req([len(v) for v in seeds] == [13+na*nh+17, 13+na*nh+17, (nn+3)*stride+17], "action seed geometry")
            owned = []
            for kind, seed in enumerate(seeds):
                if count and (kind == 2 or (family == "up-action" and role == 0)):
                    lo, size = (2*stride, nh) if kind == 2 else (13, na*nh)
                else:
                    lo, size = 0, 0
                owned.append((lo, lo+size))
        elif family == "down-action":
            nh0, nh1, na = case["nh0"], case["nh1"], case["actions"]
            count, actor, loff = case["count"], case["actor"], case["sigma_offset"]
            equal(descriptor, [nh0, nh1, na, case["threads"], actor, case["locked"], case["value_mode"], count, loff, 2, 3, 13], "down descriptor")
            nn, nha = na+9, nh0 if actor == 0 else nh1
            req([len(v) for v in imm] == [5, nn, nn, 2*nn, nn, na+4, nn, nn, 13+na*nh0+17, 13+na*nh1+17, 2*nn, loff+na*nha+17, nn], "down immutable geometry")
            req(all(p <= 255 and a <= 255 and packed == ((p << 8) | a) for p, a, packed in zip(imm[1], imm[2], imm[12])), "lossless actual packed down metadata")
            req(imm[0][2] == 3 and imm[1][3] == actor and imm[2][3] == na, "down parent bytes")
            equal(imm[3][6:8], [13, 0], "down data offset")
            req(imm[4][3] == 2 and imm[6][3] == 3 and imm[7][3] == 5, "down reach sources")
            equal(imm[5][2:2+na], range(4, 4+na), "down children")
            equal(imm[6][4:4+na], [8+2*(na-1-a) for a in range(na)], "down first physical child slots")
            equal(imm[7][4:4+na], [9+2*a for a in range(na)], "down second physical child slots")
            equal(imm[10][6:8], [loff, 0] if case["locked"] else [0xffffffff, 0xffffffff], "down lock path")
            seeds = [inp.vec(), inp.vec()]
            req([len(v) for v in seeds] == [(10+2*na)*max(nh0, 1)+17, (10+2*na)*max(nh1, 1)+17], "down seed geometry")
            owned = []
            for arm, nh in enumerate([nh0, nh1]):
                ranges = [(imm[6+arm][4+a]*nh, (imm[6+arm][4+a]+1)*nh) for a in range(na)] if count and arm == actor else []
                req(all(x[1] <= y[0] or y[1] <= x[0] for i, x in enumerate(ranges) for y in ranges[i+1:]), "down distinct child rows")
                owned.append(ranges)
        else:
            scenario = corpus["full_scenarios"][case["scenario_index"]]
            equal(descriptor, [case["scenario_index"], case["p"], case["threads"], case["count"], scenario["nh_p"], scenario["nh_o"], scenario["nh_max"], scenario["start"]], "fold descriptor")
            req(all(list(a) == b for a, b in zip(imm, fold_expected(scenario))), "all fold inputs match declared raw corpus")
            seeds = [inp.vec()]
            req(len(seeds[0]) == scenario["cfv_words"] and all(x == 0x4b123456 for x in seeds[0]), "fold initial output guards")
            active = {}; start = scenario["start"]
            for node in scenario["nodes"][start:start+case["count"]]:
                for hand in range(scenario["nh_p"]):
                    at = scenario["cfv_slot"][node]*scenario["nh_max"]+hand
                    req(at not in active and 0 <= at < len(seeds[0]), "fold unique output ownership")
                    active[at] = scenario["node_meta"][node]["required"]
        for out, image in [(base, bi), (cand, ci)]:
            result = [out.vec() for _ in seeds]
            post = [image.vec() for _ in range(fields)]
            req(all(a == b for a, b in zip(imm, post)), "all actual immutable device inputs unchanged")
            req([len(v) for v in result] == [len(v) for v in seeds], "complete output geometry")
            for kind, (actual, seed) in enumerate(zip(result, seeds)):
                if family in {"up-action", "up-action-eval"}:
                    lo, hi = owned[kind]
                    req(actual[:lo] == seed[:lo] and actual[hi:] == seed[hi:], "all action nonowned/guard/child words unchanged")
                    guards += len(actual) - (hi-lo)
                elif family == "down-action":
                    for at, word in enumerate(actual):
                        if not any(lo <= at < hi for lo, hi in owned[kind]):
                            req(word == seed[at], "all down nonowned reach words unchanged")
                            guards += 1
                else:
                    changed = this_required = 0
                    for at, word in enumerate(actual):
                        if at not in active:
                            req(word == seed[at], "all fold guards unchanged")
                            guards += 1
                        elif active[at]:
                            req(word & 0x7f800000 != 0x7f800000, "required fold result finite")
                            required_finite += 1; this_required += 1
                            if word != seed[at]:
                                changed += 1
                                nonzero += (word & 0x7fffffff != 0)
                    req(not this_required or changed > 0, "nonvacuous finite fold outputs")
                output_words += len(actual)
            immutable_words += sum(map(len, post))
    for reader in [inp, base, cand, bi, ci]:
        reader.eof()
    marker_prefix = {"up-action": "D291_UP_UNIT ", "down-action": "D291_DOWN_RAW ", "up-action-eval": "D291_EVAL_UNIT ", "up-fold": "D291_FOLD_UNIT "}[family]
    markers = [json.loads(line.split(marker_prefix, 1)[1]) for line in (raw.parent / "probe.stdout.log").read_text(encoding="utf-8").splitlines() if line.startswith(marker_prefix)]
    req(len(markers) == len(corpus["cases"])+1, "full case marker inventory")
    req([x["id"] for x in markers[:-1]] == list(range(len(corpus["cases"]))), "marker case identities")
    if family in {"up-action", "up-action-eval"}:
        for case, marker in zip(corpus["cases"], markers[:-1]):
            req(marker["parent_child_rows_disjoint"] is True, "native parent/child CFV row witness")
            witnesses = marker["disjoint_device_ranges"]
            req([w["arm"] for w in witnesses] == ["baseline", "candidate"], "both arm address witnesses")
            nh, na = case["hands"], case["actions"]
            extents = [(13+na*nh+17)*4, (13+na*nh+17)*4, ((na+11)*(nh+5)+17)*4]
            for witness in witnesses:
                regions = witness["regions"]
                req(len(regions) == 3 and [r[1] for r in regions] == extents, "actual mutable byte extents")
                req(all(isinstance(p, int) and p > 0 and size >= 0 and p+size < 2**64 for p, size in regions), "valid device pointer extents")
                req(all(p+size <= q or q+other <= p for i, (p, size) in enumerate(regions) for q, other in regions[i+1:]), "actual mutable device allocations disjoint")
    summary = markers[-1]
    req(summary["stage"] == "complete" and summary["cases"] == len(corpus["cases"]) and summary["kernel_launches"] == 2*len(corpus["cases"]), "case/launch inventory")
    req(summary["all_raw_exact"] and summary["all_inputs_and_guards_exact"], "native exactness assertions")
    req(summary["output_words_both_arms"] == output_words and summary["immutable_words_both_arms"] == immutable_words and summary["guard_words_both_arms"] == guards, "full word inventories")
    if family == "up-fold":
        req(nonzero > 0 and summary["required_finite_words_both_arms"] == required_finite and summary["required_nonzero_changed_words_both_arms"] == nonzero, "finite and nonzero fold inventory")
    report = {"id": "D291-"+family+"-root-raw-decoder", "status": "pass_scoped_full_raw_equivalence", "checks": checks,
              "cases": len(corpus["cases"]), "kernel_launches": 2*len(corpus["cases"]),
              "output_words_both_arms": output_words, "immutable_words_both_arms": immutable_words,
              "guard_words_both_arms": guards, "full_raw_files_equal": True,
              "raw_sha256": {p.name: sha(p) for p in raw.iterdir() if p.is_file()},
              "audit_sha256": sha(Path(__file__)), "corpus_sha256": sha(source / "corpus.json"),
              "limits": "Finite declared inputs only. Root replay is not external independent review; no solver accuracy, speed, universal NaN/layout or wide-address proof.",
              "performance_measured": False, "candidate_accepted": False}
    with output.open("x", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(json.dumps({k: report[k] for k in ["status", "cases", "checks", "output_words_both_arms", "immutable_words_both_arms", "guard_words_both_arms"]}))


if __name__ == "__main__":
    main()
