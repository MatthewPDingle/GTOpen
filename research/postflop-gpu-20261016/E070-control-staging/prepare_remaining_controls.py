"""Stage small E070 correctness sources. This script never starts CUDA.

Execution protocols, raw GPU results and bulk outputs still belong on S:.
Existing E070 CUDA and resource outputs are immutable inputs, not rebuilt here.
"""
from pathlib import Path
import ast
import hashlib
import json
import shutil

ROOT = Path(r"S:\GTOpen-research\postflop-gpu-20261016")
HERE = Path(__file__).resolve().parent
CANDIDATE = "ffe6c46aa48fbae149ace1288ea512814da11b840c648e6a260759e427c54ec8"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def once(text, before, after):
    assert text.count(before) == 1, before
    return text.replace(before, after)


def seal(name, code, blueprint, cases, abi, extra=None):
    out = HERE / name
    assert not out.exists(), "Preserve earlier preparation"
    assert sha(ROOT / "runs/E070-source/candidate.cu") == CANDIDATE
    resource = ROOT / "runs/E070-resource"
    report = json.loads((resource / "report.json").read_text(encoding="utf-8"))
    assert report["status"] == "pass_resource_and_encoding_prerequisites"
    out.mkdir()
    (out / "probe.rs").write_text(code, encoding="utf-8", newline="\n")
    (out / "corpus.json").write_text(json.dumps(blueprint, indent=2), encoding="utf-8")
    if extra:
        for filename, content in extra.items():
            if filename.endswith(".py"):
                ast.parse(content)
            (out / filename).write_text(content, encoding="utf-8", newline="\n")
    for arm in ["baseline", "candidate"]:
        source = resource / "execution" / f"{arm}-compute_120.ptx"
        assert sha(source) == report["ptx_sha256"][arm + "-compute_120"]
        shutil.copyfile(source, out / (arm + ".ptx"))
    prior = json.loads((resource / "protocol.json").read_text(encoding="utf-8"))
    command = [str(out / "probe.rs") if x == str(resource / "probe.rs") else
               str(out / "probe.exe") if x == str(resource / "probe.exe") else x
               for x in prior["rustc_command"]]
    metadata = {
        "id": "E070-" + name + "-preparation",
        "stage": "Unexecuted correctness control source",
        "candidate_cuda_sha256": CANDIDATE,
        "cases": cases,
        "ABI": abi,
        "GPUexecutions": 0,
        "raw_output_must_be_on_S": True,
        "host_integration_implemented": False,
        "rustc_command": command,
        "input_sha256": {p.name: sha(p) for p in out.iterdir() if p.is_file()},
        "scope": "Small compiler preparation within the writable project root; "
                 "does not authorize a GPU execution or off-workspace write.",
    }
    (out / "preparation.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps({"prepared": name, "cases": cases, "GPUexecutions": 0}))


def down():
    prior = ROOT / "runs/E067-kernel-control"
    code = (prior / "probe.rs").read_text(encoding="utf-8").replace("E067", "E070")
    assert code.count("vec![-7i32;nn]") == 2
    code = code.replace("vec![-7i32;nn]", "vec![255i32;nn]")
    code = once(code, "  let immutable=vec![", "  let attrs:Vec<u16>=player.iter().zip(&arity).map(|(&p,&a)|{"
                "assert!((0..=255).contains(&p)&&(0..=255).contains(&a));"
                "((p as u16)<<8)|(a as u16)}).collect();\n  let immutable=vec![")
    code = once(code, "split64(lock.iter().map(|x|*x as u64)),fb(&sigma)];",
                "split64(lock.iter().map(|x|*x as u64)),fb(&sigma),"
                "attrs.iter().map(|&x|x as u32).collect()];")
    code = once(code, "let dls=stream.clone_htod(&sigma).unwrap();",
                "let dls=stream.clone_htod(&sigma).unwrap();let dattrs=stream.clone_htod(&attrs).unwrap();")
    code = once(code,
        "   unsafe{stream.launch_builder(f).arg(&dn).arg(&start).arg(&count).arg(&dp).arg(&da).arg(&doff).arg(&dcs).arg(&dc).arg(&drs0).arg(&drs1).arg(&dg0).arg(&dg1).arg(&dl).arg(&dls).arg(&mut dr0).arg(&mut dr1).arg(&n0).arg(&n1).launch(LaunchConfig{grid_dim:(3,1,1),block_dim:(block,1,1),shared_mem_bytes:0}).unwrap();}",
        '''   unsafe{
    let mut launch=stream.launch_builder(f);launch.arg(&dn).arg(&start).arg(&count);
    if label=="baseline"{launch.arg(&dp).arg(&da);}else{launch.arg(&dattrs);}
    launch.arg(&doff).arg(&dcs).arg(&dc).arg(&drs0).arg(&drs1)
      .arg(&dg0).arg(&dg1).arg(&dl).arg(&dls).arg(&mut dr0).arg(&mut dr1)
      .arg(&n0).arg(&n1).launch(LaunchConfig{grid_dim:(3,1,1),block_dim:(block,1,1),shared_mem_bytes:0}).unwrap();
   }''')
    code = once(code, "readf(&stream,&dls)];stream.synchronize().unwrap();",
                "readf(&stream,&dls),stream.clone_dtoh(&dattrs).unwrap().iter().map(|&x|x as u32).collect()];stream.synchronize().unwrap();")
    source = json.loads((prior / "corpus.json").read_text(encoding="utf-8"))
    corpus = {"id": "E070-down-action-unexecuted-blueprint", "case_count": 1196,
              "kernel_launches_if_executed": 2392, "cases": source["cases"],
              "E070_source_blueprint_sha256": sha(prior / "corpus.json"),
              "E070_note": "1196 original down-action descriptors; metadata guards become valid byte255. No old result reused."}
    seal("down-action", code, corpus, 1196,
         "Baseline18arguments/candidate17; player and arity pointer pair becomes one packed-u16 pointer. Full reach outputs and13actual immutable images retained.")


def evaluation():
    prior = HERE / "up-action"
    code = (prior / "probe.rs").read_text(encoding="utf-8").replace("E070_UP", "E070_EVAL")
    code = once(code, "original/candidate up_action raw comparison", "original/candidate up_action_eval raw comparison")
    code = code.replace('load_function("up_action")', 'load_function("up_action_eval")')
    code = once(code, " assert_eq!(cases.len(),819);",
        " assert_eq!(cases.len(),819);\n let cases:Vec<Case>=cases.into_iter().flat_map(|c|[Case{algo:0,..c},Case{algo:1,..c}]).collect();\n assert_eq!(cases.len(),1638);")
    code = once(code, '''    launch.arg(&dn).arg(&start).arg(&count).arg(&p);
    if label=="baseline"{launch.arg(&dp).arg(&da);}else{launch.arg(&dattrs);}
    launch.arg(&doff).arg(&dcs).arg(&dc).arg(&mut dr).arg(&mut ds)
        .arg(&drs).arg(&drp).arg(&dl).arg(&dls).arg(&dslot).arg(&mut dv)
        .arg(&dd).arg(&nharg).arg(&maxarg).launch(LaunchConfig{''',
        '''    let eval_mode=algo as i32;
    launch.arg(&dn).arg(&start).arg(&count).arg(&p).arg(&eval_mode);
    if label=="baseline"{launch.arg(&dp).arg(&da);}else{launch.arg(&dattrs);}
    launch.arg(&doff).arg(&dcs).arg(&dc).arg(&ds)
        .arg(&dl).arg(&dls).arg(&dslot).arg(&mut dv)
        .arg(&nharg).arg(&maxarg).launch(LaunchConfig{''')
    code = once(code,
        "let owned=count!=0 && if kind<2 {role==0 && i>=off && i<off+na*nh}else{i>=parent*max && i<parent*max+nh};",
        "let owned=count!=0 && kind==2 && i>=parent*max && i<parent*max+nh;")
    code = code.replace('"algorithm":algo', '"eval_mode":algo')
    corpus = json.loads((prior / "corpus.json").read_text(encoding="utf-8"))
    expanded = []
    for source in corpus["cases"]:
        for mode in [0, 1]:
            c = dict(source)
            c["source_case_id"] = source["id"]
            c["id"] = len(expanded)
            c["eval_mode"] = mode
            c["algorithm"] = mode
            c["descriptor"] = source["descriptor"].copy()
            c["descriptor"][5] = mode
            # Discount buffer is unused, but retain the actual corresponding
            # production discount bits selected by the probe for that mode.
            candidates = [x for x in corpus["cases"] if x["algorithm"] == mode
                          and x["iteration"] == source["iteration"]]
            assert candidates
            c["discount_bits"] = candidates[0]["discount_bits"]
            expanded.append(c)
    corpus = {"id": "E070-up-action-eval-unexecuted-blueprint", "case_count": 1638,
              "kernel_launches_if_executed": 3276, "cases": expanded,
              "E070_note": "All819 up-action geometries in both best-response and average-strategy evaluation modes (1638declared cases). Regrets and strategy must remain unchanged; only parent CFV words are writable.",
              "E070_source_blueprint_sha256": sha(prior / "corpus.json")}
    audit = (prior / "audit.py").read_text(encoding="utf-8").replace("E070_UP", "E070_EVAL")
    audit = audit.replace("==819", "==1638").replace("==1638,'launch/case", "==3276,'launch/case")
    audit = audit.replace("'cases':819,'kernel_launches':1638", "'cases':1638,'kernel_launches':3276")
    audit = once(audit, "   if count and (kind==2 or role==0):", "   if count and kind==2:")
    audit = audit.replace("pass_scoped_up_action_raw_equivalence", "pass_scoped_up_action_eval_raw_equivalence")
    seal("up-action-eval", code, corpus, 1638,
         "Baseline17arguments/candidate16; packed-u16 pointer replaces player/arity pair. Best-response(mode0) and average-strategy(mode1), full CFV outputs, all guard/strategy/regret words,13immutable images.",
         {"audit.py": audit, "discounts.rs": (prior / "discounts.rs").read_text(encoding="utf-8")})


if __name__ == "__main__":
    down()
    evaluation()
