"""Freeze original three paired complete solves for one fixed E127 host+shader form."""
import ast,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
bp=ROOT/'runs/E127-build-plan/protocol.json';b=h.read(bp);build=ROOT/'runs/E127-final-build/complete.json';done=h.read(build)
assert done['all_compilers_terminal']and done['native_executions']==0
for path,digest in done['evidence_sha256'].items():h.pin(path,digest)
direct=ROOT/'runs/E127-direct/report.json';r=h.read(direct);assert r['status']=='pass_all2457_original_and_derived_whole_physical_cases'and r['counts']['cases']==2457 and r['kernel_launches']==7914
H=ROOT/'runs/E127-primary-plan';H.mkdir(exist_ok=False);scripts=[]
for suffix in['primary-native','primary-assess','primary-root-check','run-primary']:
    source=ROOT/'runs'/('E125-'+suffix+'.py');path=ROOT/'runs'/('E127-'+suffix+'.py');assert not path.exists()
    code=source.read_text(encoding='utf-8').replace('E125','E127');ast.parse(code);path.write_bytes(code.encode());scripts +=[source,path]
sequence=[{'id':'V127-unit','binary':'E127-solver','unit':True}]+[{'id':ident,'binary':'E080-postflop_autoresearch'if ident.startswith('B')else'E127-postflop_autoresearch','unit':False}for ident in['B381','E127R1','E127R2','B382','B383','E127R3']]
for rec in sequence:assert not(ROOT/'runs'/rec['id']).exists()
files=[Path(__file__),bp,build,ROOT/'runs/E127-build.py',ROOT/'epoch/runner.py',ROOT/'epoch/common.py',ROOT/'epoch/exact-anchor.json',ROOT/'epoch/accepted-source.json',ROOT/'epoch/protected-main.json',ROOT/'epoch/preexisting-target-artifacts.json',direct,ROOT/'runs/E127-direct/protocol.json',ROOT/'runs/E127-direct/reader-repair.json',ROOT/'runs/E127-read-direct-v2.py',ROOT/'runs/E127-host-source/manifest.json',ROOT/'runs/E127-host-source/design.json',ROOT/'runs/E127-host-control/report.json',ROOT/'runs/E127-native/control-report.json',ROOT/'runs/E127-resource/protocol.json',ROOT/'runs/E127-resource/report.json',ROOT/'comparisons/RAM20261028-baseline/report.json',h.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md']+scripts
for stem in['E127-feature-solver','E127-solver','E127-postflop_autoresearch','E080-postflop_autoresearch']:
    exe=ROOT/'binaries'/(stem+'.exe');mp=exe.with_suffix('.manifest.json');m=h.read(mp);h.pin(exe,m['binary_sha256'])
    assert m['source_sha256']==b['accepted_source_sha256']|(b['candidate_owned_sha256']if stem.startswith('E127')else{});files +=[exe,mp]
parent=h.read(ROOT/'runs/E125-primary-plan/protocol.json')
h.save(H/'protocol.json',{'id':'E127-primary','at':h.now(),'status':'FROZEN_PRE_ORDINARY_UNITS_AND_PRIMARY_TIMING','measurement_epoch':'RAM20261028',
    'build_protocol_sha256':h.sha(bp),'accepted_source_sha256':b['accepted_source_sha256'],'candidate_owned_sha256':b['candidate_owned_sha256'],
    'sequence':sequence,'pairs':[{'baseline':'B381','candidate':'E127R1'},{'baseline':'B382','candidate':'E127R2'},{'baseline':'B383','candidate':'E127R3'}],
    'required_ordinary_units':86,'required_aggregate_gain_pct':1.,'fixture_guard':parent['fixture_guard'],
    'excluded_samples_allowed':False,'extension_runs_allowed':False,'historical_or_RAM_baseline_timing_pooling_allowed':False,'required_free_bytes':66*1024**3,
    'adoption_requirements':parent['adoption_requirements'],
    'scope':'Sameoriginal3compressedcompletecycles/16workers/defaultaffinity/.3%pot/check20/cap400/stops200/200/60/exactscienceanchor. BothordinarybuildsactualNVRTC12.9/JIT+setup/upload/solve/fullreadback included; fingerprints/destruction/Cargo/browser/API/saveexcludedasoriginal. Fixed4fileD313deepest-firstdisjointstarform, original9kernels/CFVmap/math/qualityunchanged. AddedCPUbuilder/oneu32GPUworklist/wrapper+heaps/moduleJIT/graphs/allocationcostsincluded,nottreatedfree. All2457directcases/7914launches/12immutableand3wholemutableoutputs/guardsexact; actualCPUbuilder6originalplans/typespassed. Perprospectiveprotocol direct+ordinaryprecedesinitialspeed; fullrawengine/canonical/newphysicalfield/broad/material/capacity/fresh16/holdout/freshoriginalRAMcumulative/actualappbeforeadoption. No width/phase/group/guard/helper/layout/scope/source/quality/sample rescue after genuinefailure. No timingspooled/excluded/extended.',
    'input_sha256':{str(path):h.sha(path)for path in files},'candidate_accepted':False})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);row=next(x for x in status['experiments']if x['id']=='E127')
    row.update(at=h.now(),stage='86 ordinary units then three paired complete solves',correctness='2457direct_cases_allphysical_words_exact',reason='FixedB381/E127R1,E127R2/B382,B383/E127R3, samequality/scienceanchor. Original1%unroundedaggregate/strictfixtureguard. Allnewplanner/worklist/JIT/graphcostsincluded; noextra/excluded/pooledsamples. Fulladoptionqualificationpending.')
    status.update(updated_at=h.now(),active_experiment='E127',stage=row['stage'],activity=row['reason']);h.ar.atomic_json(h.ar.STATUS,status)
print(json.dumps({'protocol_sha256':h.sha(H/'protocol.json'),'sequence':[x['id']for x in sequence]}),flush=True)
