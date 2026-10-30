"""Source-level ABI audit; neither CUDA compilation nor execution is performed."""
from pathlib import Path
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
OUT = HERE / "host-integration-r2"
REL = Path("crates/solver/src/gpu")


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def compact(s):
    return re.sub(r"\s+", "", s)


def balanced(s, pos):
    assert s[pos] == "("
    level = 1
    i = pos + 1
    while level:
        assert i < len(s)
        level += (s[i] == "(") - (s[i] == ")")
        i += 1
    return s[pos+1:i-1], i


targets = {"f_down_action": ("kernels.cu", "down_action", 3),
           "f_up_fold": ("kernels.cu", "up_fold", 2),
           "f_up_action": ("kernels.cu", "up_action", 1),
           "f_up_action_eval": ("kernels.cu", "up_action_eval", 1),
           "project": ("continuation_projection.cu", "continuation_project", 1),
           "transport": ("continuation_projection.cu", "continuation_transport", 1),
           "copy_kernel": ("continuation_storage_copy.cu", "continuation_storage_copy", 1)}


def launches(s):
    found = []
    for match in re.finditer(r"\.launch_builder\(", s):
        name, end = balanced(s, match.end()-1)
        target = name.split(".")[-1].lstrip("&")
        if target not in targets:
            continue
        args = []
        stop = s.index(".launch(", end)
        while True:
            m = re.search(r"\.arg\(", s[end:stop])
            if m is None:
                break
            arg, end = balanced(s, end+m.end()-1)
            args.append(compact(arg))
        found.append((target, args, s.count("\n", 0, match.start())+1))
    return found


def parameters(s, name):
    match = re.search(r'extern "C" __global__ void '+name+r'\(', s)
    assert match, name
    signature, _ = balanced(s, match.end()-1)
    return [compact(x) for x in signature.split(",")]


manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
for arm, hashes in [("baseline", manifest["staged_baseline_sha256"]), ("candidate", manifest["candidate_source_sha256"])]:
    for p, expected in hashes.items():
        assert sha(OUT / arm / p) == expected, (arm, p)
seen = {name: 0 for name in targets}
sites = []
for filename in ["mod.rs", "continuation.rs", "continuation_storage.rs"]:
    before = launches((OUT / "baseline" / REL / filename).read_text(encoding="utf-8"))
    after = launches((OUT / "candidate" / REL / filename).read_text(encoding="utf-8"))
    assert len(before) == len(after)
    for (name, args, line), (newname, newargs, newline) in zip(before, after):
        assert name == newname
        expected = []
        i = 0
        while i < len(args):
            if args[i].endswith(".d_node_player"):
                expected.append(args[i][:-len("d_node_player")]+"d_node_attrs")
                if i+1 < len(args) and args[i+1] == args[i][:-len("d_node_player")]+"d_node_na":
                    i += 1
            else:
                expected.append(args[i])
            i += 1
        assert expected == newargs, (filename, line, name)
        cuda, kernel, _ = targets[name]
        oldparams = parameters((OUT / "baseline" / REL / cuda).read_text(encoding="utf-8"), kernel)
        newparams = parameters((OUT / "candidate" / REL / cuda).read_text(encoding="utf-8"), kernel)
        assert len(args) == len(oldparams) and len(newargs) == len(newparams), (name, len(args), len(oldparams), len(newargs), len(newparams))
        old_position = next(j for j, param in enumerate(oldparams) if re.search(r"\*(?:__restrict__)?(?:node_player|players)$", param))
        assert newparams[old_position] in {"constunsignedshort*__restrict__node_attrs", "constunsignedshort*node_attrs"}
        expectedparams = oldparams[:old_position]+[newparams[old_position]]+oldparams[old_position+1:]
        if kernel != "up_fold":
            assert re.search(r"\*(?:__restrict__)?(?:node_na|na)$", expectedparams[old_position+1])
            del expectedparams[old_position+1]
        assert expectedparams == newparams, kernel
        assert newargs[old_position].endswith(".d_node_attrs")
        seen[name] += 1
        sites.append({"file": str(REL/filename), "baseline_line": line, "candidate_line": newline,
                      "kernel": kernel, "baseline_arguments": len(args), "candidate_arguments": len(newargs),
                      "metadata_argument_index_zero_based": old_position,
                      "all_other_argument_expressions_and_CUDA_parameter_types_unchanged": True})
assert all(seen[name] == config[2] for name, config in targets.items()), seen
assert len(sites) == 10
candidate_mod = (OUT / "candidate" / REL / "mod.rs").read_text(encoding="utf-8")
assert "d_node_attrs: CudaSlice<u16>" in candidate_mod
assert "d_node_attrs: stream.clone_htod(&node_attrs).map_err(e)?" in candidate_mod
capacity = (OUT / "candidate" / REL / "continuation_capacity.rs").read_text(encoding="utf-8")
assert "+(p.num_nodes as u64)*size_of::<u16>() as u64" in capacity
assert "d_node_attrs:u16" in capacity
report = {"id": "E070-complete-host-ABI-source-audit", "status": "pass_source_abi_only",
          "launch_sites": sites, "site_count": 10, "kernel_entries": 7,
          "all_nonmetadata_host_arguments_unchanged": True,
          "all_nonmetadata_CUDA_parameter_types_unchanged": True,
          "all_changed_metadata_arguments_match_u16_device_field": True,
          "candidate_manifest_sha256": sha(OUT / "manifest.json"),
          "audit_source_sha256": sha(Path(__file__)),
          "CUDA_Rust_typecheck": False, "CUDA_compilation": False, "GPUexecutions": 0,
          "limits": "Finite source/parser audit, not an integrated Rust type check, driver ABI/resource check or GPU numerical result. The three continuation helper entries still require their prospective numerical/resource controls.",
          "candidate_accepted": False}
with (OUT / "abi-source-audit.json").open("x", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
print(json.dumps({"status": report["status"], "sites": 10, "kernels": 7, "GPUexecutions": 0}))
