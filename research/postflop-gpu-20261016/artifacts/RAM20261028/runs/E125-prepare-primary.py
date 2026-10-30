"""Freeze six complete-solve observations and original strict acceptance rules."""
import ast,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();h.ar.refuse_active(h.ar.live_status())
assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
bp=ROOT/'runs/E125-build-plan/protocol.json';b=h.read(bp);build=ROOT/'runs/E125-final-build/complete.json';done=h.read(build)
assert done['all_compilers_terminal']and done['native_executions']==0
for path,digest in done['evidence_sha256'].items():h.pin(path,digest)
direct=ROOT/'runs/E125-kernel-control/reader-report.json';r=h.read(direct)
assert r['cases']==1688 and r['application_kernel_launches']==3376 and r['all_original_inputs_and_seeds_independently_regenerated']and len(r['negative_reader_fixtures_rejected'])==4
H=ROOT/'runs/E125-primary-plan';H.mkdir(exist_ok=False);scripts=[]
for suffix in['primary-native','primary-assess','primary-root-check','run-primary']:
    source=ROOT/'runs'/('E122-'+suffix+'.py');path=ROOT/'runs'/('E125-'+suffix+'.py')
    assert not path.exists();code=source.read_text(encoding='utf-8').replace('E122','E125');ast.parse(code);path.write_bytes(code.encode());scripts += [source,path]
sequence=[{'id':'V125-unit','binary':'E125-solver','unit':True}]+[{'id':ident,'binary':'E080-postflop_autoresearch'if ident.startswith('B')else'E125-postflop_autoresearch','unit':False}for ident in['B378','E125R1','E125R2','B379','B380','E125R3']]
for rec in sequence:assert not(ROOT/'runs'/rec['id']).exists()
files=[Path(__file__),bp,build,ROOT/'runs/E125-build.py',ROOT/'epoch/runner.py',ROOT/'epoch/common.py',ROOT/'epoch/exact-anchor.json',ROOT/'epoch/accepted-source.json',ROOT/'epoch/protected-main.json',ROOT/'epoch/preexisting-target-artifacts.json',direct,ROOT/'runs/E125-kernel-control/protocol.json',ROOT/'runs/E125-source/manifest.json',ROOT/'runs/E125-resource/protocol.json',ROOT/'runs/E125-resource/report.json',ROOT/'runs/E125-resource/emitted-report.json',ROOT/'comparisons/RAM20261028-baseline/report.json',h.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md']+scripts
for stem in['E125-feature-solver','E125-solver','E125-postflop_autoresearch','E080-postflop_autoresearch']:
    exe=ROOT/'binaries'/(stem+'.exe');mp=exe.with_suffix('.manifest.json');m=h.read(mp);h.pin(exe,m['binary_sha256'])
    assert m['source_sha256']==b['accepted_source_sha256']|(b['candidate_owned_sha256']if stem.startswith('E125')else{})
    files += [exe,mp]
parent=h.read(ROOT/'runs/E122-primary-plan/protocol.json')
h.save(H/'protocol.json',{'id':'E125-primary','at':h.now(),'status':'FROZEN_PRE_ORDINARY_UNITS_AND_PRIMARY_TIMING','measurement_epoch':'RAM20261028',
    'build_protocol_sha256':h.sha(bp),'accepted_source_sha256':b['accepted_source_sha256'],'candidate_owned_sha256':b['candidate_owned_sha256'],
    'sequence':sequence,'pairs':[{'baseline':'B378','candidate':'E125R1'},{'baseline':'B379','candidate':'E125R2'},{'baseline':'B380','candidate':'E125R3'}],
    'required_ordinary_units':86,'required_aggregate_gain_pct':1.,'fixture_guard':parent['fixture_guard'],
    'excluded_samples_allowed':False,'extension_runs_allowed':False,'historical_or_RAM_baseline_timing_pooling_allowed':False,'required_free_bytes':66*1024**3,
    'adoption_requirements':parent['adoption_requirements'],
    'scope':'Sameoriginal3compressedcompletecycles/16workers/defaultaffinity/.3%pot/check20/cap400/stops200/200/60/exactscienceanchor. BothordinarybuildsactualNVRTC12.9/JIT+setup/upload/solve/fullreadback included; fingerprints/destruction/Cargo/browser/API/saveexcludedasoriginal. Fixed4fileu16handpermtablefromoriginalSpotu16values, same FPmath/ordering/identity/branch/launch. All1688directoriginalcases/3376launches fullraw exactinclphysicalu16; resource30to40warningkept. Perprospectiveprotocol direct+ordinaryprecedesinitialspeed; fullCPUplan/rawengine/canonical/broad/material/capacity/fresh16/holdout/freshoriginalRAMcumulative/actualappbeforeadoption. No width/field/packing/helper/layout/scope/source/quality/sample rescue after genuinefailure. No timingspooled/excluded/extended.',
    'input_sha256':{str(path):h.sha(path)for path in files},'candidate_accepted':False})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);row=next(x for x in status['experiments']if x['id']=='E125')
    row.update(at=h.now(),stage='86ordinaryunits then fixed3pairedcompletecycles',correctness='1688original_direct_cases_all_raw_exact',reason='FixedB378/E125R1,E125R2/B379,B380/E125R3, samequality/scienceanchor. No extra/excluded/pooledsamples. 1%unrounded+fixtureguard; alladoptionqualificationpending.')
    status.update(updated_at=h.now(),active_experiment='E125',stage=row['stage'],activity=row['reason']);h.ar.atomic_json(h.ar.STATUS,status)
print(json.dumps({'protocol_sha256':h.sha(H/'protocol.json'),'sequence':[x['id']for x in sequence]}),flush=True)
