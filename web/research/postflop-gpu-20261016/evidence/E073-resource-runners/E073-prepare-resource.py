"""Freeze a single E073 resource prerequisite after source/domain proof."""
from pathlib import Path
import ast,json,shutil,sys
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
D=R/'runs/D118-river-boundaries';S=R/'runs/E073-source';H=R/'runs/E073-resource';q=old.read(D/'report.json');assert q['status']=='pass_legal_boundary_domain_and_retained_raw_equivalence'and q['retained_boundary_words']==9182716
assert not H.exists();H.mkdir()
for n in ['baseline.cu','candidate.cu']:shutil.copyfile(S/n,H/n)
probe=(R/'runs/E066-resource/probe.rs').read_text(encoding='utf-8').replace('E066_RESOURCE','E073_RESOURCE');assert probe.count('E073_RESOURCE')==1
(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n');executor=R/'runs/E073-resource-execute.py';ast.parse(executor.read_text(encoding='utf-8'))
prior=old.read(R/'runs/E072-resource/protocol.json');command=[str(x).replace('E072-resource','E073-resource')for x in prior['rustc_command']]
deps={p:h for p,h in prior['input_sha256'].items()if 'release\\deps' in p}
for p,h in deps.items():old.pin(p,h)
paths=[Path(__file__),R/'runs/D118-prepare.py',D/'protocol.json',D/'history.json',D/'report.json',D/'publication.json',*[p for p in S.iterdir()if p.is_file()],H/'baseline.cu',H/'candidate.cu',H/'probe.rs',executor,R/'runs/E073-run-resource.py',C/'common_e051_live.py',C/'protected-main.json',old.REPO/'tools/postflop_resource_feasibility.py',old.REPO/'tools/postflop_resource_admission.py']
P={'id':'E073-resource','at':old.now(),'status':'FROZEN_PRE_COMPILE_RESOURCE','rustc_command':command,'gpu_uuid':prior['gpu_uuid'],'allocation_proof':prior['allocation_proof'],'expected_entries':prior['expected_entries'],'changed_entries':['up_show'],'shapes':['rainbow_p0','rainbow_p1','two_tone_p0','two_tone_p1','river_p0','river_p1','wide_turn','full_hand_upper_bound','empty_sorted_opponent','single_sorted_opponent'],'input_sha256':deps|{str(p):old.sha(p)for p in paths},'scope':'One Rustcompiler, one no-application-kernel process with4NVRTCcompiles (both sources x compute120/75),2driver resource sets x10unchanged shapes; no source activation or timing.','gates':'Exact other8PTXentry bodies and27parameterABI; address-only origin tracing proves32to16bit global boundary loads. D108default feasibility/positiveoccupancy and exact local/static/dynamic reservations. Static FPopcode counts diagnostic only, source float recurrence and full raw GPU controls mandatory.','prospective_payload_change':'Only4private lower/upper buffers shrink4to2bytes per entry. CPU/public plan, logical elements and all other payload/shape/allocation counts unchanged. Temporary host packing4allocations/4synchronizations remain inside complete clocks, actual material costs/capacity require qualification.','no_variants_or_rescue':True,'candidate_accepted':False};old.save(H/'protocol.json',P)
print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'input_files':len(P['input_sha256']),'compiler_or_native_executions':0}),flush=True)
