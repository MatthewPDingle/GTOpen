"""Freeze six fresh two-tone processes after the guard-only observer build."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
H=ROOT/'runs/D096-two-tone-profile';prior=ROOT/'runs/D087-cupti-driver-profile';B=H/'diagnostic-build'
c=old.read(B/'complete.json');assert c['compiler_terminal'] and c['native_executions']==0
buildplan=old.read(H/'diagnostic-build-plan.json')
for p,h in buildplan['input_sha256'].items():old.pin(p,h)
# Preserve the unexecuted frozen first reporting script. Fix its inherited
# dashboard parent-row selector before any cohort observation or report write.
source=(H/'root-and-publish.py').read_text();needle="x['id']=='D087'";assert source.count(needle)==1
fixed=source.replace(needle,"x['id']=='D096'")
assert not (H/'root-and-publish-r2.py').exists();(H/'root-and-publish-r2.py').write_text(fixed,encoding='utf-8',newline='\n')
old.save(H/'pre-cohort-reporting-repair.json',{'at':old.now(),'original_script_sha256':old.sha(H/'root-and-publish.py'),'repaired_script_sha256':old.sha(H/'root-and-publish-r2.py'),'change':'Only inherited dashboard parent-row selector D087->D096 in the reporting script. First script preserved/unexecuted. No solver, binary, observer, sampling, quality or analysis arithmetic change.','cohort_native_executions':0})
wrapper='''import json,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
assert len(sys.argv)==2;old.pin(H/'cohort-plan.json',sys.argv[1]);P=old.read(H/'cohort-plan.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
old.custody();M=ROOT/'runs/D096-manager';assert not M.exists();M.mkdir()
old.child([sys.executable,str(H/'run-cohort.py'),sys.argv[1]],M,'cohort',old.env(),1200)
old.custody();old.child([sys.executable,str(H/'root-and-publish-r2.py')],M,'root',old.env(),300)
q=old.read(H/'cohort-report.json');r=old.read(ROOT/'comparisons/D096-two-tone-root-check/report.json')
old.save(M/'complete.json',{'at':old.now(),'all_owned_children_terminal':True,'cohort_report_sha256':old.sha(H/'cohort-report.json'),'root_report_sha256':old.sha(ROOT/'comparisons/D096-two-tone-root-check/report.json'),'observer_usefulness_pass':q['observer_usefulness_pass'],'source_main_live_ptx_unchanged':True})
old.custody();print(json.dumps({'status':q['status'],'root_checks':r['checks_passed'],'observer_cycle_changes_pct':r['observer_cycle_changes_pct'],'median_phase_intervals':r['median_phase_intervals']}),flush=True)
'''
assert not (H/'run-and-root.py').exists();(H/'run-and-root.py').write_text(wrapper,encoding='utf-8',newline='\n')
binaries={}
for name,p in [('baseline',ROOT/'binaries/E051-postflop_autoresearch.exe'),('trace',B/'postflop-trace.exe')]:
    mp=p.with_suffix('.manifest.json');m=old.read(mp);old.pin(p,m['binary_sha256']);assert m['source_sha256']==old.BASE
    if name=='trace':assert m['harness_sha256']==old.sha(H/'evaluator.rs') and m['build_protocol_sha256']==old.sha(H/'diagnostic-build-plan.json')
    binaries[name]={'path':str(p),'sha256':old.sha(p),'manifest':str(mp),'manifest_sha256':old.sha(mp)}
P=old.read(prior/'cohort-plan.json');topology=old.read(H/'topology-inputs.json');ids=['D096B1','D096T1','D096T2','D096B2','D096B3','D096T3']
for identity in ids:assert not (ROOT/'runs'/identity).exists() and not any(e['id']==identity for e in old.read(old.ar.STATUS)['experiments'])
assert not (H/'cohort-execution').exists() and not (ROOT/'runs/D096-manager').exists() and not (ROOT/'comparisons/D096-two-tone-root-check').exists()
P.update(id='D096-two-tone-cohort',at=old.now(),status='FROZEN_BEFORE_FULL_SOLVES',order=ids,pairs=[{'baseline':'D096B1','trace':'D096T1'},{'baseline':'D096B2','trace':'D096T2'},{'baseline':'D096B3','trace':'D096T3'}],binaries=binaries,fixture='two-tone',expected_graph_kernel_nodes_sorted=topology['expected_two_tone_graph_kernel_nodes_sorted'],expected_kernel_records=topology['expected_kernel_records'],trace_quality_rule='Same full non-timing result/fingerprint and10checkpoints as accepted two-tone. Zero collector errors/drops/bad timestamps/outstanding buffers.3graphs with63/63/103kernel nodes and199/199/9repeats,407GraphLaunchAPIrecords and exact kernel/API correlation; six ordered phase timestamps and26230application kernels pertrace. Identical family counts across3traces.',scope='Second registered fixture, two-tone only. Fresh diagnostic to observe device/kernel/API/phase overlaps; no optimizer or primary whole-suite gain claim. Preserve original1%/exactness/fixture/fresh16/broader/material/holdout/cumulative gates.')
inputs={p:h for p,h in buildplan['input_sha256'].items() if Path(p).suffix in ['.rlib','.rmeta','.lib','.dll']}
paths=[*H.iterdir(),B/'complete.json',prior/'ability-report.json',prior/'collector.cpp',prior/'build/D087Collector.dll',prior/'build/D087Collector.lib',Path(P['driver_cbid_header']),ROOT/'runs/accepted-E051/common_e051.py',Path(__file__)]+[Path(v[k]) for v in binaries.values() for k in ['path','manifest']]
inputs.update({str(p):old.sha(p) for p in paths if p.is_file()});P['input_sha256']=inputs
old.save(H/'cohort-plan.json',P)
published={}
for p in [H/'cohort-plan.json',H/'root-and-publish-r2.py',H/'run-and-root.py',H/'pre-cohort-reporting-repair.json',B/'complete.json']:
    key='evidence/'+H.name+'/'+p.relative_to(H).as_posix();dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True)
    assert not dst.exists();dst.write_bytes(p.read_bytes())
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=15) as response:assert response.read()==p.read_bytes()
    published[key]=old.sha(p)
old.save(H/'pre-timing-publication.json',{'at':old.now(),'published':published,'http_bytes_verified':True,'native_cohort_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);e=next(e for e in s['experiments'] if e['id']=='D096');e.update(stage='Three fixed ordinary/traced two-tone pairs',reason='Fresh diagnostic executable links exact accepted E051solver and unchanged D087observer DLL. Only fixture guard changed. Six new runs, exact full fingerprints/checkpoints, trace/API quality and <=10%observer clocks required.');e['evidence'].append({'label':'Frozen six-process matched two-tone cohort','url':'evidence/'+H.name+'/cohort-plan.json'});s.update(updated_at=old.now(),stage='D096 matched two-tone profiling',activity='Run exactly D096B1/T1,T2/B2,B3/T3. Measure scoped device/API overlaps and observer cost; no optimization acceptance.');old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(json.dumps({'cohort_protocol_sha256':old.sha(H/'cohort-plan.json'),'published':len(published),'fixture':'two-tone','source_activated':False}),flush=True)
