"""Prepare E070's up-action controls inside the permitted workspace.

This does not run GPU code or write scientific bulk output. The final native
protocol and all raw results must still be frozen under the existing S: root.
"""
from pathlib import Path
import ast
import hashlib
import json
import shutil

ROOT = Path(r"S:\GTOpen-research\postflop-gpu-20261016")
HERE = Path(__file__).resolve().parent
OUT = HERE / "up-action"
CANDIDATE = "ffe6c46aa48fbae149ace1288ea512814da11b840c648e6a260759e427c54ec8"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(text, before, after):
    assert text.count(before) == 1, before
    return text.replace(before, after)


def prepare():
    assert sha(ROOT / "runs/E070-source/candidate.cu") == CANDIDATE
    assert not OUT.exists(), "Preserve any earlier prepared version"
    prior = ROOT / "runs/E054-kernel-control"
    resource = ROOT / "runs/E070-resource"
    report = json.loads((resource / "report.json").read_text(encoding="utf-8"))
    assert report["status"] == "pass_resource_and_encoding_prerequisites"
    code = (prior / "probe.rs").read_text(encoding="utf-8").replace("E054", "E070_UP")
    assert code.count("vec![-7i32;nn]") == 2
    code = code.replace("vec![-7i32;nn]", "vec![255i32;nn]")
    code = replace_once(
        code,
        "  let immutable=vec![",
        "  let attrs:Vec<u16>=player.iter().zip(&arity).map(|(&p,&a)|{"
        "assert!((0..=255).contains(&p)&&(0..=255).contains(&a));"
        "((p as u16)<<8)|(a as u16)}).collect();\n  let immutable=vec![",
    )
    code = replace_once(
        code,
        "slots.clone(),fb(&disc)];",
        "slots.clone(),fb(&disc),attrs.iter().map(|&x|x as u32).collect()];",
    )
    code = replace_once(
        code,
        "let dd=stream.clone_htod(&disc).unwrap();",
        "let dd=stream.clone_htod(&disc).unwrap();"
        "let dattrs=stream.clone_htod(&attrs).unwrap();",
    )
    before = (
        "   unsafe{stream.launch_builder(f).arg(&dn).arg(&start).arg(&count)"
        ".arg(&p).arg(&dp).arg(&da).arg(&doff).arg(&dcs).arg(&dc).arg(&mut dr)"
        ".arg(&mut ds).arg(&drs).arg(&drp).arg(&dl).arg(&dls).arg(&dslot)"
        ".arg(&mut dv).arg(&dd).arg(&nharg).arg(&maxarg).launch(LaunchConfig{"
        "grid_dim:(3,1,1),block_dim:(block,1,1),shared_mem_bytes:0}).unwrap();}"
    )
    after = '''   unsafe{
    let mut launch=stream.launch_builder(f);
    launch.arg(&dn).arg(&start).arg(&count).arg(&p);
    if label=="baseline"{launch.arg(&dp).arg(&da);}else{launch.arg(&dattrs);}
    launch.arg(&doff).arg(&dcs).arg(&dc).arg(&mut dr).arg(&mut ds)
        .arg(&drs).arg(&drp).arg(&dl).arg(&dls).arg(&dslot).arg(&mut dv)
        .arg(&dd).arg(&nharg).arg(&maxarg).launch(LaunchConfig{
            grid_dim:(3,1,1),block_dim:(block,1,1),shared_mem_bytes:0}).unwrap();
   }'''
    code = replace_once(code, before, after)
    code = replace_once(
        code,
        "post.push(readf(&stream,&dd));stream.synchronize().unwrap();",
        "post.push(readf(&stream,&dd));"
        "post.push(stream.clone_dtoh(&dattrs).unwrap().iter().map(|&x|x as u32)"
        ".collect());stream.synchronize().unwrap();",
    )
    audit = (prior / "audit.py").read_text(encoding="utf-8").replace("E054", "E070_UP")
    audit = audit.replace("range(12)", "range(13)")
    audit = replace_once(audit, "5+na*nh+17,nn,3]", "5+na*nh+17,nn,3,nn]")
    before = " req([len(v) for v in imm]==lengths,'complete immutable geometry')"
    audit = replace_once(
        audit,
        before,
        before + "\n req(all(p<=255 and a<=255 and packed==((p<<8)|a) "
        "for p,a,packed in zip(imm[1],imm[2],imm[12])),"
        "'packed device metadata exactly matches both byte fields')",
    )
    ast.parse(audit)
    OUT.mkdir()
    (OUT / "probe.rs").write_text(code, encoding="utf-8", newline="\n")
    (OUT / "audit.py").write_text(audit, encoding="utf-8", newline="\n")
    for name in ["discounts.rs", "corpus.json"]:
        shutil.copyfile(prior / name, OUT / name)
    for arm in ["baseline", "candidate"]:
        path = resource / "execution" / f"{arm}-compute_120.ptx"
        assert sha(path) == report["ptx_sha256"][arm + "-compute_120"]
        shutil.copyfile(path, OUT / (arm + ".ptx"))
    protocol = json.loads((resource / "protocol.json").read_text(encoding="utf-8"))
    command = [
        str(OUT / "probe.rs") if x == str(resource / "probe.rs") else
        str(OUT / "probe.exe") if x == str(resource / "probe.exe") else x
        for x in protocol["rustc_command"]
    ]
    metadata = {
        "id": "E070-up-action-preparation",
        "stage": "Unexecuted control source; three other kernel families pending",
        "candidate_cuda_sha256": CANDIDATE,
        "cases": 819,
        "input_fields": 13,
        "guard_metadata": "Unconsumed guards become byte value255 instead of i32 -7; "
            "all launched parent player/arity values and floating data are unchanged.",
        "ABI": "Baseline20arguments; candidate19arguments. Only player/arity "
            "pointer pair becomes one packed-u16 pointer.",
        "GPUexecutions": 0,
        "raw_output_must_be_on_S": True,
        "host_integration_implemented": False,
        "rustc_command": command,
        "input_sha256": {p.name: sha(p) for p in OUT.iterdir() if p.is_file()},
        "scope": "Small source/compiler preparation inside the permitted workspace. "
            "No runtime output or off-workspace write is authorized by this file.",
    }
    (OUT / "preparation.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps({"stage": str(OUT), "GPUexecutions": 0, "cases": 819}))


if __name__ == "__main__":
    prepare()
