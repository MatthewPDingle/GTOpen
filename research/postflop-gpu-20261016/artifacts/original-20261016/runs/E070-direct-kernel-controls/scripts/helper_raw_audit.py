"""Root full-array decoder for the fixed E070 three-helper GPU comparison.

No subprocesses. Run only after the separately sealed native control completes.
"""
from pathlib import Path
import hashlib
import json
import math
import struct
import sys

checks = 0


def req(value, message):
    global checks
    assert value, message
    checks += 1


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Reader:
    def __init__(self, path, magic):
        self.data = path.read_bytes()
        req(self.data.startswith(magic), "raw magic")
        self.at = len(magic)

    def id(self):
        req(self.at+4 <= len(self.data), "id bounds")
        value, = struct.unpack_from("<I", self.data, self.at)
        self.at += 4
        return value

    def vec(self):
        req(self.at+8 <= len(self.data), "array header bounds")
        size, = struct.unpack_from("<Q", self.data, self.at)
        self.at += 8
        req(size <= 2_000_000 and self.at+4*size <= len(self.data), "raw array bounds")
        result = memoryview(self.data)[self.at:self.at+4*size].cast("I")
        self.at += 4*size
        return result

    def eof(self):
        req(self.at == len(self.data), "complete raw endpoint")


def split(values):
    return [part for value in values for part in [value & 0xffffffff, value >> 32]]


def f32(word):
    return struct.unpack("<f", struct.pack("<I", word))[0]


def bits(value):
    return struct.unpack("<I", struct.pack("<f", value))[0]


def value(i, mode):
    if mode == 1:
        return [0, 0x80000000][i % 2]
    if mode == 2:
        return [0x7f800000, 0xff800000, 0x7fc01234, 0xffc05678, 0x3e800000, 0xbf400000, 0x3f800000][i % 7]
    if mode == 3:
        return [0x7f7fffff, 0xff7fffff, 0x3f800000, 0xbf800000][i % 4]
    if mode == 4:
        return [1, 0x80000001, 0, 0x80000000, 0x00800000, 0x80800000, 0x00800001][i % 7]
    return [bits(x) for x in [0., -0., .25, -.75, 13.25, -7.125, 1e10, -1e10, 1e-20, -1e-20]][(i*5+i//11) % 10]


def main():
    req(sys.byteorder == "little" and len(sys.argv) == 7, "source/raw/stdout/report/admission/admission-sha256 arguments")
    source, raw, stdout, output, admission_path = map(Path, sys.argv[1:6])
    root = Path(r"S:\GTOpen-research\postflop-gpu-20261016").resolve()
    req(all(p.resolve().is_relative_to(root) for p in [source, raw, stdout, output, admission_path]), "all admitted inputs/results on S")
    req(sha(admission_path) == sys.argv[6], "prospective numerical admission seal")
    admission = json.loads(admission_path.read_text(encoding="utf-8"))
    ptx_sha256 = admission["helper_ptx_input_sha256"]
    req(len(ptx_sha256) == 4, "four sealed helper PTX inputs")
    for path, expected in ptx_sha256.items():
        req(Path(path).resolve().is_relative_to(root) and sha(Path(path)) == expected, "sealed helper PTX bytes")
    req(not output.exists(), "immutable new audit report")
    prep = json.loads((source/"preparation.json").read_text(encoding="utf-8"))
    for name, expected in prep["input_sha256"].items():
        req(sha(source/name) == expected, "frozen source hash: "+name)
    corpus = json.loads((source/"corpus.json").read_text(encoding="utf-8"))
    req(len(corpus["cases"]) == corpus["case_count"] == prep["cases"] == 2120, "declared case count")
    inp = Reader(raw/"inputs.bin", b"E070_HELPER_IN1")
    base = Reader(raw/"baseline.bin", b"E070_HELPER_OUT1"); cand = Reader(raw/"candidate.bin", b"E070_HELPER_OUT1")
    bi = Reader(raw/"baseline-inputs.bin", b"E070_HELPER_IM1"); ci = Reader(raw/"candidate-inputs.bin", b"E070_HELPER_IM1")
    req(base.data == cand.data, "every baseline/candidate output byte exact")
    req(bi.data == ci.data, "all actual immutable images equal between arms")
    output_words = immutable_words = guards = oracle_words = nonfinite_reductions = 0
    for index, c in enumerate(corpus["cases"]):
        req(c["id"] == index and all(r.id() == index for r in [inp, base, cand, bi, ci]), "case identities")
        req(list(inp.vec()) == c["descriptor"], "actual full descriptor")
        kind, nh, na, p, op, count, mode = [c[k] for k in ["kind", "hands", "actions", "p", "operation", "count", "value_mode"]]
        offset = [13+n*(na*nh+7) for n in range(5)]
        packed = [11+n*(na*nh+5) for n in range(5)]
        nodes, players = [2, 1, 3, 0xdeadbeef, 0xdeadbeef], [0, 1, 0, 1, 255]
        arity = [na]*4+[255]
        expected = [nodes, players, arity, [(x << 8) | a for x, a in zip(players, arity)],
                    split(offset), [3, 1, 3, 3, 1], list(range(nh))+list(reversed(range(nh))) if nh else [0xdeadbeef],
                    [0, 1, 0, 1, 4], [0, 0, 1, 1, 0], split(packed)]
        immutable = [inp.vec() for _ in range(10)]
        req(all(list(v) == e for v, e in zip(immutable, expected)), "all declared actual immutable inputs")
        seeds = [inp.vec() for _ in range(4)]
        req([len(v) for v in seeds] == [offset[4]+na*nh+17]*2+[packed[4]+na*nh+17]*2, "full mutable geometry")
        for k, seed in enumerate(seeds):
            # Explicit samples verify the declared value-mode factory; all words
            # are retained, and all owned results/guards below are checked.
            sample = set(range(min(32, len(seed)))) | set(range(max(0, len(seed)-32), len(seed)))
            req(all(seed[at] == value(at+index*7+k*31, mode) for at in sample), "declared value-mode endpoint samples")
        results = [base.vec() for _ in range(4)]
        other = [cand.vec() for _ in range(4)]
        before_image = [bi.vec() for _ in range(10)]; after_image = [ci.vec() for _ in range(10)]
        req(all(a == b == d for a, b, d in zip(immutable, before_image, after_image)), "every actual immutable device word unchanged")
        req([len(v) for v in results] == [len(v) for v in seeds] and all(a == b for a, b in zip(results, other)), "full output geometry and equality")
        owned = [[] for _ in range(4)]
        for b, node in enumerate(nodes[:count]):
            if players[node] != p:
                continue
            if kind == 0:
                if expected[5][node] == 1:
                    continue
                lo, hi = (0, (nh+1)//2) if op == 0 else ((nh+1)//2, nh)
                for action in range(na):
                    start = offset[node]+action*nh
                    for k in [0, 1]:
                        owned[k].append((start+lo, start+hi))
                        if op == 1:
                            req(results[k][start+lo:start+hi] == seeds[k][start:start+nh-lo][::-1], "full broadcast copy oracle")
                            oracle_words += 2*(hi-lo)
                        else:
                            for hand in range(lo, hi):
                                x, y = f32(seeds[k][start+hand]), f32(seeds[k][start+nh-1-hand])
                                if math.isfinite(x) and math.isfinite(y):
                                    total = 0.; total += x; total += y
                                    req(results[k][start+hand] == bits(total/2.), "ordered double-average/f32 projection oracle")
                                    oracle_words += 2
                                else:
                                    nonfinite_reductions += 2
            elif kind == 1:
                origin = expected[7][node]
                if origin == node:
                    continue
                req(expected[7][origin] == origin and origin not in [n for n in nodes[:count] if n != expected[7][n]], "transport source is never written")
                for k in [0, 1]:
                    owned[k].append((offset[node], offset[node]+na*nh))
                    for action in range(na):
                        at, src = offset[node]+action*nh, offset[origin]+action*nh
                        req(results[k][at:at+nh] == seeds[k][src:src+nh][::-1], "full transport source-bit oracle")
                        oracle_words += 2*nh
            else:
                for k in [0, 1]:
                    dst, at, origin, src = (k+2, packed[b], k, offset[node]) if op else (k, offset[node], k+2, packed[b])
                    owned[dst].append((at, at+na*nh))
                    req(results[dst][at:at+na*nh] == seeds[origin][src:src+na*nh], "full stored gather/scatter source-bit oracle")
                    oracle_words += 2*na*nh
        for k, (result, seed) in enumerate(zip(results, seeds)):
            position = 0
            for lo, hi in sorted(owned[k]):
                req(position <= lo <= hi <= len(seed), "disjoint owned mutable ranges")
                req(result[position:lo] == seed[position:lo], "all intervening nonowned guard words exact")
                guards += 2*(lo-position)
                position = hi
            req(result[position:] == seed[position:], "all trailing nonowned guards exact")
            guards += 2*(len(seed)-position)
        output_words += 2*sum(map(len, results)); immutable_words += 2*sum(map(len, immutable))
    for r in [inp, base, cand, bi, ci]:
        r.eof()
    prefix = "E070_HELPER_RAW "
    markers = [json.loads(line[len(prefix):]) for line in stdout.read_text(encoding="utf-8").splitlines() if line.startswith(prefix)]
    module_rows = [x for x in markers if x["stage"] == "PTX_input"]
    req(len(markers) == 2125, "no missing or extra raw-control markers")
    req(len(module_rows) == 4 and [(x["module"], x["arm"]) for x in module_rows] == [(m, a) for m in ["projection", "storage-copy"] for a in ["baseline", "candidate"]], "exact four loaded PTX identities")
    req(set(x["path"] for x in module_rows) == set(ptx_sha256), "actual loaded PTX paths match prospective seal")
    for row in module_rows:
        req(row["bytes"] == Path(row["path"]).stat().st_size and sha(Path(row["path"])) == ptx_sha256[row["path"]], "actual loaded module byte inventory and hash")
    case_rows = [x for x in markers if x["stage"] == "case"]
    req(len(case_rows) == 2120 and [x["id"] for x in case_rows] == list(range(2120)), "all native case markers")
    for c, marker in zip(corpus["cases"], case_rows):
        req(all(marker[k] == c[k] for k in ["kind", "hands", "actions", "threads", "p", "operation", "count", "value_mode"]), "native case identity")
        witnesses = marker["disjoint_device_ranges"]
        req([w["arm"] for w in witnesses] == ["baseline", "candidate"], "both pointer witnesses")
        nh, na = c["hands"], c["actions"]
        extents = [4*(13+4*(na*nh+7)+na*nh+17)]*2+[4*(11+4*(na*nh+5)+na*nh+17)]*2
        for w in witnesses:
            regions = w["regions"]
            req(len(regions) == 4 and [r[1] for r in regions] == extents, "actual pointer byte extents")
            req(all(isinstance(p, int) and p > 0 and size >= 0 and p+size < 2**64 for p, size in regions), "valid actual device extents")
            req(all(p+size <= q or q+other <= p for j, (p, size) in enumerate(regions) for q, other in regions[j+1:]), "actual four mutable allocations disjoint")
    summary = markers[-1]
    req(summary["stage"] == "complete" and summary["cases"] == 2120 and summary["kernel_launches"] == 4240, "native completion inventory")
    req(summary["all_raw_exact"] and summary["all_inputs_and_guards_exact"], "native exactness assertions")
    req([summary[k] for k in ["output_words_both_arms", "immutable_words_both_arms", "guard_words_both_arms", "CPU_oracle_words_both_arms"]] == [output_words, immutable_words, guards, oracle_words], "full word inventories")
    report = {"id": "E070-three-helper-root-full-raw-audit", "status": "pass_scoped_full_raw_equivalence_and_CPU_oracles",
              "checks": checks, "cases": 2120, "kernel_launches": 4240,
              "output_words_both_arms": output_words, "immutable_words_both_arms": immutable_words,
              "guard_words_both_arms": guards, "CPU_oracle_words_both_arms": oracle_words,
              "nonfinite_reduction_words_without_cross_platform_CPU_payload_oracle": nonfinite_reductions,
              "all_raw_files_sha256": {p.name: sha(p) for p in raw.iterdir() if p.is_file()},
              "corpus_sha256": sha(source/"corpus.json"), "audit_source_sha256": sha(Path(__file__)),
              "numerical_admission_sha256": sha(admission_path), "helper_ptx_input_sha256": ptx_sha256,
              "performance_measured": False, "candidate_accepted": False,
              "limits": "Finite declared synthetic layouts and order2 groups. Root replay is not external independent review. Complete baseline/candidate bits include nonfinite reductions; CPU NaN-payload parity is not claimed. Full solver/group/continuation/storage/capacity/material/speed checks remain required."}
    with output.open("x", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(json.dumps({k: report[k] for k in ["status", "checks", "cases", "output_words_both_arms", "immutable_words_both_arms", "guard_words_both_arms", "CPU_oracle_words_both_arms"]}))


if __name__ == "__main__":
    main()
