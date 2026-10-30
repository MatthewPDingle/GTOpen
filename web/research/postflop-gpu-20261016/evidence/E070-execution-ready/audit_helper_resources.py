"""Validate one frozen helper compiler/resource run; starts no subprocess."""
from pathlib import Path
import hashlib
import json
import re
import sys


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def balanced(text, at, opening="(", closing=")"):
    assert text[at] == opening
    level = 1
    end = at+1
    while level:
        assert end < len(text), "unclosed PTX block"
        level += (text[end] == opening) - (text[end] == closing)
        end += 1
    return text[at+1:end-1], end


def entry(ptx, name):
    ptx = re.sub(r"/\*[\s\S]*?\*/|//[^\n]*", "", ptx)
    match = re.search(r"\.visible\s+\.entry\s+"+name+r"\s*\(", ptx)
    assert match, name
    signature, end = balanced(ptx, match.end()-1)
    body_start = ptx.index("{", end)
    body, _ = balanced(ptx, body_start, "{", "}")
    params = []
    for declaration in signature.split(","):
        match = re.fullmatch(r"\s*\.param\s+((?:(?:\.\w+|\d+)\s+)+)([A-Za-z0-9_]+)(?:\[(\d+)\])?\s*", declaration)
        assert match, declaration
        qualifiers = " ".join(match[1].split())
        params.append((qualifiers, match[2], match[3] or ""))
    assert params and len(params) == signature.count(".param"), name
    return params, body


def main():
    assert len(sys.argv) == 5, "source/ptx/stdout/report arguments"
    source, ptxdir, stdout, output = map(Path, sys.argv[1:])
    root = Path(r"S:\GTOpen-research\postflop-gpu-20261016").resolve()
    assert all(p.resolve().is_relative_to(root) for p in [source, ptxdir, stdout, output])
    assert not output.exists()
    prep = json.loads((source/"preparation.json").read_text(encoding="utf-8"))
    for name, expected in prep["input_sha256"].items():
        assert sha(source/name) == expected, name
    rows = [json.loads(line.split("E070_HELPER_RESOURCE ", 1)[1]) for line in stdout.read_text(encoding="utf-8").splitlines() if line.startswith("E070_HELPER_RESOURCE ")]
    assert len(rows) == 8 and rows[0]["stage"] == "device" and rows[-1]["stage"] == "complete"
    complete = rows[-1]
    assert complete["resource_rows"] == 6 and complete["compile_variants"] == 8 and complete["kernel_launches"] == complete["solver_executions"] == 0
    resource_rows = rows[1:-1]
    expected_keys = [("projection", arm, k) for arm in ["baseline", "candidate"] for k in ["continuation_project", "continuation_transport"]]+[("storage-copy", arm, "continuation_storage_copy") for arm in ["baseline", "candidate"]]
    assert [(r["module"], r["variant"], r["kernel"]) for r in resource_rows] == expected_keys
    gates = []

    def gate(name, passed, details):
        gates.append({"gate": name, "pass": bool(passed), "details": details})

    ptx_hashes = {}
    expected_ptx_names = {f"{module}-{arm}-{arch}.ptx" for module in ["projection", "storage-copy"] for arm in ["baseline", "candidate"] for arch in ["compute_120", "compute_75"]}
    assert set(p.name for p in ptxdir.iterdir()) == expected_ptx_names
    for module, kernels, arity in [("projection", ["continuation_project", "continuation_transport"], 12), ("storage-copy", ["continuation_storage_copy"], 13)]:
        before = (source/("baseline-"+module+".cu")).read_text(encoding="utf-8")
        after = (source/("candidate-"+module+".cu")).read_text(encoding="utf-8")
        reverse = after.replace("const unsigned short* node_attrs,", "const int* players, const int* na,")
        reverse = re.sub(r"\(node_attrs\[(n|node)\] >> 8\)", r"players[\1]", reverse)
        reverse = re.sub(r"\(node_attrs\[(n|node)\] & 0xff\)", r"na[\1]", reverse)
        gate(module+":source_reverse", reverse == before, "Only pointer pair and integer metadata decodes may change.")
        for arch in ["compute_120", "compute_75"]:
            texts = {}
            for arm in ["baseline", "candidate"]:
                p = ptxdir/f"{module}-{arm}-{arch}.ptx"
                texts[arm] = p.read_text(encoding="utf-8")
                ptx_hashes[str(p)] = sha(p)
                names = re.findall(r"\.visible\s+\.entry\s+(\w+)\s*\(", texts[arm])
                gate(module+":"+arm+":"+arch+":entry_inventory", names == kernels, names)
            for kernel in kernels:
                bp, _ = entry(texts["baseline"], kernel)
                cp, body = entry(texts["candidate"], kernel)
                before_types = [(p[0], p[2]) for p in bp]
                after_types = [(p[0], p[2]) for p in cp]
                gate(kernel+":"+arch+":ABI", len(bp) == arity and len(cp) == arity-1 and before_types[:2]+after_types[2:3]+before_types[4:] == after_types and before_types[2][0].startswith(".u64") and before_types[3][0].startswith(".u64") and after_types[2][0].startswith(".u64"),
                     {"baseline_count": len(bp), "candidate_count": len(cp), "baseline_types": before_types, "candidate_types": after_types})
                narrow = re.findall(r"ld\.global(?:\.nc)?\.(u8|u16)\b", body)
                gate(kernel+":"+arch+":narrow_load", bool(narrow), {"widths": narrow, "scope": "PTX metadata load, not driver SASS/cache-transaction proof"})
    warnings = []
    for module, kernel in [("projection", "continuation_project"), ("projection", "continuation_transport"), ("storage-copy", "continuation_storage_copy")]:
        b = next(r for r in resource_rows if r["module"] == module and r["kernel"] == kernel and r["variant"] == "baseline")
        c = next(r for r in resource_rows if r["module"] == module and r["kernel"] == kernel and r["variant"] == "candidate")
        gate(kernel+":no_new_local_bytes", c["local_bytes_per_thread"] <= b["local_bytes_per_thread"], [b["local_bytes_per_thread"], c["local_bytes_per_thread"]])
        gate(kernel+":shared_unchanged", c["static_shared_bytes"] == b["static_shared_bytes"] and c["dynamic_shared_bytes"] == b["dynamic_shared_bytes"] == 0,
             [b["static_shared_bytes"], c["static_shared_bytes"]])
        gate(kernel+":maxthreads_and_fit", c["max_threads"] >= b["max_threads"] and c["max_threads"] >= 256 and b["fits_default_limits"] and c["fits_default_limits"],
             [b["max_threads"], c["max_threads"]])
        gate(kernel+":residency_positive", [x[0] for x in c["occupancy_by_threads"]] == [64, 128, 256] and all(x[1] > 0 for x in c["occupancy_by_threads"]), c["occupancy_by_threads"])
        if c["registers"] > b["registers"] or any(y[1] < x[1] for x, y in zip(b["occupancy_by_threads"], c["occupancy_by_threads"])):
            warnings.append({"kernel": kernel, "baseline_registers": b["registers"], "candidate_registers": c["registers"], "baseline_residency": b["occupancy_by_threads"], "candidate_residency": c["occupancy_by_threads"], "qualification": "Prospective D108 warning; does not establish no material tradeoff."})
    passed = all(g["pass"] for g in gates)
    report = {"id": "E070-continuation-helper-resource-audit", "status": "pass_helper_compiler_ABI_and_resource_prerequisites" if passed else "fail_helper_resource_prerequisite",
              "gates": gates, "warnings": warnings, "resource_rows": resource_rows,
              "all_eight_PTX_sha256": ptx_hashes, "application_kernel_launches": 0,
              "preparation_sha256": sha(source/"preparation.json"), "audit_source_sha256": sha(Path(__file__)),
              "stdout_sha256": sha(stdout), "performance_measured": False, "candidate_accepted": False,
              "limits": "Compiler/PTX/driver resource prerequisites only. No GPU floating-result, actual memory traffic, complete-solver performance or no-tradeoff proof. compute_75 is compiler coverage, not a tested second physical GPU."}
    with output.open("x", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(json.dumps({"status": report["status"], "gates": len(gates), "warnings": warnings, "application_kernel_launches": 0}))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
