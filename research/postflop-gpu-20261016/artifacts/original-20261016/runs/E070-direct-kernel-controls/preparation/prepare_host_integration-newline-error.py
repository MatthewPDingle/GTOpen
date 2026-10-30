"""Prepare the complete E070 ABI patch without editing either solver checkout.

The core CUDA candidate remains frozen. Continuation kernels need the same ABI
conversion because their callers borrow GpuSolver's private metadata buffers.
No kernel, solver, NVRTC or Cargo process is started by this preparation.
"""
from pathlib import Path
from datetime import datetime, timezone
import difflib
import hashlib
import json
import re

ROOT = Path(r"S:\GTOpen-research\postflop-gpu-20261016")
REPO = Path(r"X:\Dev\GTOpen-gpu-research-20261016")
HERE = Path(__file__).resolve().parent
OUT = HERE / "host-integration"
REL = "crates/solver/src/gpu/"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def once(s, before, after):
    assert s.count(before) == 1, before
    return s.replace(before, after)


baseline = json.loads((ROOT / "runs/accepted-E051/baseline.json").read_text(encoding="utf-8"))
for name, expected in baseline["source_sha256"].items():
    assert sha(REPO / name) == expected, name
assert not OUT.exists()
names = ["mod.rs", "continuation.rs", "continuation_storage.rs", "continuation_capacity.rs",
         "continuation_projection.cu", "continuation_storage_copy.cu", "kernels.cu"]
original = {name: (REPO / REL / name).read_text(encoding="utf-8") for name in names}
candidate = dict(original)
source = candidate["mod.rs"]
source = once(source, "    d_node_player: CudaSlice<i32>,\n    d_node_na: CudaSlice<i32>,",
              "    d_node_attrs: CudaSlice<u16>,")
source = once(source, "        Ok(GpuSolver {", """        // The public CPU plan remains unchanged. Node fields are u8 at source;
        // pack both bytes losslessly for the private device representation.
        // Keep the temporary alive for the whole constructor, as for plan uploads.
        let node_attrs: Vec<u16> = solver.spot.tree.nodes.iter()
            .map(|node| ((node.player as u16) << 8) | node.num_children as u16)
            .collect();

        Ok(GpuSolver {""")
source = once(source, "            d_node_player: upi32(&plan.node_player)?,\n            d_node_na: upi32(&plan.node_na)?,",
              "            d_node_attrs: stream.clone_htod(&node_attrs).map_err(e)?,")
pattern = r"\.arg\(&(?P<receiver>self|gpu)\.d_node_player\)\s*\.arg\(&(?P=receiver)\.d_node_na\)"
source, count = re.subn(pattern, lambda m: ".arg(&" + m["receiver"] + ".d_node_attrs)", source)
assert count == 5, count  # eager/evaluation/training and full-down reference
assert source.count(".arg(&self.d_node_player)") == 2
source = source.replace(".arg(&self.d_node_player)", ".arg(&self.d_node_attrs)")
candidate["mod.rs"] = source
assert candidate["continuation.rs"].count(".arg(&self.gpu.d_node_player).arg(&self.gpu.d_node_na)") == 2
candidate["continuation.rs"] = candidate["continuation.rs"].replace(
    ".arg(&self.gpu.d_node_player).arg(&self.gpu.d_node_na)", ".arg(&self.gpu.d_node_attrs)")
candidate["continuation_storage.rs"] = once(candidate["continuation_storage.rs"],
    ".arg(&g.d_node_player).arg(&g.d_node_na)", ".arg(&g.d_node_attrs)")
source = candidate["continuation_capacity.rs"]
source = once(source, "        node_player,node_na,node_data_off", "        node_data_off")
source = once(source, "cc_start,cc_count,cc_card,cc_child,cc_perm,cfv_slot)+bytes(&s.tree.children);",
              "cc_start,cc_count,cc_card,cc_child,cc_perm,cfv_slot)+bytes(&s.tree.children)\n        +(p.num_nodes as u64)*size_of::<u16>() as u64;")
source = once(source, "d_show_nodes:u32,d_node_player:i32,d_node_na:i32,d_node_data_off:u64",
              "d_show_nodes:u32,d_node_attrs:u16,d_node_data_off:u64")
candidate["continuation_capacity.rs"] = source
helper_changes = []
for name, expected in [("continuation_projection.cu", 2), ("continuation_storage_copy.cu", 1)]:
    source = candidate[name]
    assert source.count("const int* players, const int* na,") == expected
    source = source.replace("const int* players, const int* na,", "const unsigned short* node_attrs,")
    source, players = re.subn(r"players\[(n|node)\]", r"(node_attrs[\1] >> 8)", source)
    source, arities = re.subn(r"na\[(n|node)\]", r"(node_attrs[\1] & 0xff)", source)
    assert players == expected and arities == (3 if expected == 2 else 1)
    reverse = source.replace("const unsigned short* node_attrs,", "const int* players, const int* na,")
    reverse = re.sub(r"\(node_attrs\[(n|node)\] >> 8\)", r"players[\1]", reverse)
    reverse = re.sub(r"\(node_attrs\[(n|node)\] & 0xff\)", r"na[\1]", reverse)
    assert reverse == original[name], name
    candidate[name] = source
    helper_changes.append({"path": REL+name, "entries": expected, "players_loads_replaced": players,
                           "arity_loads_replaced": arities, "reverse_to_E051_source_exact": True,
                           "floating_expressions_and_loop_order_unchanged": True})
frozen_cuda = ROOT / "runs/E070-source/candidate.cu"
assert sha(frozen_cuda) == "ffe6c46aa48fbae149ace1288ea512814da11b840c648e6a260759e427c54ec8"
candidate["kernels.cu"] = frozen_cuda.read_text(encoding="utf-8")
for name in names[:4]:
    assert not re.search(r"\bd_node_(player|na)\b", candidate[name]), name
OUT.mkdir()
for arm, content in [("baseline", original), ("candidate", candidate)]:
    for name, text in content.items():
        folder = OUT / arm / REL
        folder.mkdir(parents=True, exist_ok=True)
        (folder / name).write_text(text, encoding="utf-8", newline="\n")
assert sha(OUT / "candidate" / REL / "kernels.cu") == sha(frozen_cuda)
patch = "".join("".join(difflib.unified_diff(original[name].splitlines(True), candidate[name].splitlines(True),
              fromfile="a/"+REL+name, tofile="b/"+REL+name)) for name in names)
(OUT / "candidate.patch").write_text(patch, encoding="utf-8", newline="\n")
manifest = {
    "id": "E070-complete-host-ABI-preparation", "at": datetime.now(timezone.utc).isoformat(),
    "status": "prepared_off_tree_source_only", "files": len(names),
    "research_baseline_files_verified": len(baseline["source_sha256"]),
    "baseline_source_sha256": {REL+n: baseline["source_sha256"][REL+n] for n in names},
    "staged_baseline_sha256": {REL+n: sha(OUT/"baseline"/REL/n) for n in names},
    "candidate_source_sha256": {REL+n: sha(OUT/"candidate"/REL/n) for n in names},
    "patch_sha256": sha(OUT / "candidate.patch"),
    "helper_kernel_changes": helper_changes,
    "compatibility_discovery": "D114's host inventory found continuation.rs/storage.rs references, but mislabeled them as down-action callers. They launch continuation_project, continuation_transport and continuation_storage_copy from two other CUDA modules. Those three ABIs must also consume packed attrs; retaining both old buffers would defeat the2*N representation.",
    "existing_four_kernel_cuda_unchanged": True,
    "prior_GPU_floating_executions": 0,
    "prior_E070_speed_samples": 0,
    "host_pack": "One temporary Vec<u16>,2*Nbytes, directly from the original u8 Node.player/num_children. CPU GpuPlan vectors unchanged. Temporary remains in constructor scope as existing plan uploads do; no new stream synchronization or graph/launch order change.",
    "metadata_accounting": "Private predicted/observed device payload replaces8*N by2*N. Public GPU budget estimates and CPU plan layouts remain unchanged. Existing capacity tests must verify observed payload after integration.",
    "required_before_activation": ["Prospectively seal the three helper ABI/resource/raw controls in addition to the existing four main-kernel controls.",
                                   "Native prerequisite admission requires current runtime permissions and checksum-preserved S archive.",
                                   "All seven kernel numerical controls pass before candidate solver activation.",
                                   "Full host/caller type check and integrated ordinary/equivalence/continuation checks pass before timing qualification."],
    "production_and_research_sources_modified": False,
    "solver_builds": 0, "NVRTC_processes": 0, "GPUexecutions": 0,
    "candidate_accepted": False,
}
with (OUT / "manifest.json").open("x", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)
print(json.dumps({"prepared_files": len(names), "additional_helper_entries": 3,
                  "frozen_main_cuda_unchanged": True, "GPUexecutions": 0,
                  "patch_sha256": manifest["patch_sha256"]}))
