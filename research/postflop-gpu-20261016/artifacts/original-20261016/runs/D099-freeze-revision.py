"""Pre-native reporting/lifetime repair; keep the scratch transform and frozen gates."""
import ast,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();H=ROOT/'runs/D099-plan-posting-scratch';assert not (H/'build').exists() and not (H/'execution').exists()
P=old.read(H/'protocol.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
s=(H/'probe.rs').read_text(encoding='utf-8')
assert s.count('if pair==8{b=Some(p);}else{drop(p);}')==s.count('if pair==8{a=Some(p);}else{drop(p);}')==1
s=s.replace('if pair==8{b=Some(p);}else{drop(p);}','drop(p);').replace('if pair==8{a=Some(p);}else{drop(p);}','drop(p);')
s=s.replace('for (pair,&candidate_first) in orders.iter().enumerate(){','for &candidate_first in &orders{')
needle='ams=median(&baseline_samples);bms=median(&candidate_samples);';assert s.count(needle)==1
s=s.replace(needle,needle+'\n// Separate untimed final plans for complete raw field/capacity controls.\nlet mut pa=accepted::GpuPlan::build(&spot,iso);if full{pa.use_full_action_arenas(&spot);}a=Some(pa);\nlet mut pb=candidate::GpuPlan::build(&spot,iso);if full{pb.use_full_action_arenas(&spot);}b=Some(pb);')
needle='"first":if id%2==1{"candidate"}else{"baseline"}';assert s.count(needle)==1;s=s.replace(needle,'"first":"baseline"')
(H/'probe-r2.rs').write_text(s,encoding='utf-8',newline='\n')
s=(H/'execute.py').read_text(encoding='utf-8').replace("H/'protocol.json'","H/'protocol-r2.json'");ast.parse(s);(H/'execute-r2.py').write_text(s,encoding='utf-8',newline='\n')
old.save(H/'pre-native-repair.json',{'at':old.now(),'native_runs':0,'compiler_runs':0,'original_protocol_sha256':old.sha(H/'protocol.json'),'original_probe_sha256':old.sha(H/'probe.rs'),'candidate_source_sha256_unchanged':old.sha(H/'candidate-plan.rs'),'reason':'Static preflight found stale inherited first-arm metadata and asymmetrical final measured-pair retention. Correct first to baseline and drop every measured result after stopping its timer; build separate untimed final plans for raw equality. Original source/protocol retained; no timing results exist and no kernel/transform/gate changed.','additional_unscored_control_plan_builds_per_process':2})
P.update(at=old.now(),status='FROZEN_R2_PRE_COMPILE_AND_NATIVE',original_protocol_sha256=old.sha(H/'protocol.json'),preparation_revision='Metadata first-arm label fixed; identical per-arm measured lifetimes;2separate untimed final control plans. Fixed prototype/gates/counts/order unchanged.')
P['command']=[x.replace(str(H/'probe.rs'),str(H/'probe-r2.rs')) for x in P['command']]
for p in [H/'protocol.json',H/'probe-r2.rs',H/'execute-r2.py',H/'pre-native-repair.json',Path(__file__)]:P['input_sha256'][str(p)]=old.sha(p)
old.save(H/'protocol-r2.json',P);old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'protocol-r2.json'),'native_runs':0,'prototype_unchanged':True}),flush=True)
