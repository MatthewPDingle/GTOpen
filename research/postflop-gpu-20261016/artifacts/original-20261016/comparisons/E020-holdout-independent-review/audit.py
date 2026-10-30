"""Independent read-only CPU audit of terminal E020 resource/holdout evidence."""
from pathlib import Path
import datetime,hashlib,json,math,re,statistics,struct
ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
P=ROOT/'runs/E020-wide-turn-holdout-implementation-r2'
OUT=Path(__file__).resolve().parent
ORDER=['B1','C1','C2','B2','B3','C3']
TIMING={'build_ms','init_ms','solve_ms','readback_ms','full_cycle_ms','fingerprint_ms_excluded'}
PINS={}
def sha(p):
    p=Path(p);h=hashlib.sha256()
    with p.open('rb') as f:
        while block:=f.read(1024*1024):h.update(block)
    value=h.hexdigest();PINS[str(p)]=value;return value
def read(p):
    sha(p);return json.loads(Path(p).read_text(encoding='utf-8'))
def pin(r):
    assert sha(r['path'])==r['sha256'],r['path'];return Path(r['path'])
def markers(p,name):
    sha(p);rows=[]
    for line in p.read_text(encoding='utf-8').splitlines():
        m=re.search(re.escape(name)+r'\s+(\{.*\})$',line)
        if m:rows.append(json.loads(m.group(1)))
    return rows
def passed(d,name):
    e=read(d/'exit.json');assert e['returncode']==0 and e['error'] is None and e['cleanup'] is None
    s=(d/'stdout.log').read_text(encoding='utf-8');sha(d/'stdout.log');sha(d/'stderr.log')
    assert 'test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out;' in s
    assert name in s and 'FAILED' not in s
    assert (d/'stderr.log').read_text(encoding='utf-8').strip()==''
    return e
def raw(p,result,reference):
    with p.open('rb') as f:
        assert f.read(16)==b'GTO-WIDE-RAW-v1\0'
        n=struct.unpack('<Q',f.read(8))[0];assert n<65536
        meta=json.loads(f.read(n));assert meta=={k:result[k] for k in ['algorithm','exploit_bits','iteration','use_isomorphism']}
        frames=[]
        for player,arena,kind in [(0,0,1),(0,1,2),(1,0,1),(1,1,2)]:
            head=f.read(19);assert len(head)==19
            a,b,c,entries,scales=struct.unpack('<BBBQQ',head);assert (a,b,c)==(player,arena,kind)
            expected=result['state_fingerprint']['arenas'][len(frames)]
            assert entries==expected['entries'] and scales==expected['scale_entries']
            assert expected['player']==player and expected['kind']==['','i16','u16'][kind]
            payload=entries*2+scales*4;assert payload==expected['bytes'] and f.tell()+payload<=p.stat().st_size
            f.seek(payload,1);frames.append({'player':player,'arena':arena,'kind':kind,'entries':entries,'scales':scales,'payload_bytes':payload})
        assert f.read(1)==b''
    h=hashlib.sha256();compared=0
    with p.open('rb') as f,reference.open('rb') as r:
        while True:
            a=f.read(1024*1024);b=r.read(1024*1024);assert a==b,(str(p),compared)
            if not a:break
            h.update(a);compared+=len(a)
    digest=h.hexdigest();PINS[str(p)]=digest
    return {'metadata':meta,'frames':frames,'bytes':compared,'sha256':digest}
assert sha(P/'prepared-manifest.json')=='3e55bec74defdbc3a5e87d299c08722bccfbfc9d388c2908f8e7f5273cafac91'
prepared=read(P/'prepared-manifest.json')
for rel,h in prepared['artifact_sha256'].items():assert sha(P/rel)==h,rel
for rel,h in prepared['nvrtc_dll_sha256'].items():assert sha(Path(r'X:\Dev\GTOpen\.cuda-nvrtc\nvidia\cuda_nvrtc\bin')/rel)==h
ready_path=ROOT/'runs/E020-qualification-plan-r3/all-builds-ready.json'
assert sha(ready_path)=='4c53c85b4d7e83915ce31ec93d13a0dc916d8aca5c722441152e10886a6fdda0'
ready=read(ready_path)
assert all(ready[k] is True for k in ['all_required_builds_terminal','all_builds_terminal','holdout_builds_terminal','holdout_build_source_review_pass'])
for name,h in ready['artifacts'].items():assert sha(name)==h,name
binaries={}
for name in ['E015-holdout','E020-holdout','E015-resource']:
    path=P/'build/binaries'/f'{name}.exe';m=read(path.with_suffix('.manifest.json'));digest=sha(path)
    assert digest==m['binary_sha256'];assert m['prepared_manifest_sha256']==sha(P/'prepared-manifest.json')
    assert m['target_empty_before_build'] is True and m['cargo_artifact']['fresh'] is False and m['solver_artifact']['fresh'] is False
    target=ROOT/'build-holdout-e020-r2'/m['role'];assert Path(m['target_dir'])==target
    assert Path(m['cargo_artifact']['executable']).is_relative_to(target)
    assert sha(m['cargo_artifact']['executable'])==digest
    counts={role:path.read_bytes().count((P/f'{role}-kernels.cu').read_bytes()) for role in ['E015','E020']}
    if name=='E015-resource':assert counts=={'E015':1,'E020':1}
    else:assert counts=={m['role']:1,('E020' if m['role']=='E015' else 'E015'):0}
    assert counts==m['embedded_cuda_occurrences']
    binaries[name]={'binary_sha256':digest,'manifest_sha256':sha(path.with_suffix('.manifest.json')),'embedded_cuda':counts}
assert binaries['E015-holdout']['binary_sha256']!=binaries['E020-holdout']['binary_sha256']
for phase in ['resource','cohort']:
    started=read(P/phase/'started.json');auth=read(pin({'path':started['authorization_path'],'sha256':started['authorization_sha256']}))
    assert auth['prepared_manifest_sha256']==sha(P/'prepared-manifest.json')
    assert auth['phase']==phase and auth['primary_audit_pass'] and auth['holdout_source_review_pass']
    assert pin(auth['all_builds_ready'])==ready_path
    for record in auth['required_evidence']:pin(record)
assert sha(P/'cohort-authorization.json')=='6161971a92cc68fd55d6c07a7e602ba229b8237a8171369f53e85e3d4a09e8c3'
assert sha(P/'resource/report.json')=='84bf3edfdfd8645e2dbf882a6b14c6ce7f88b4a68ebb5fdc5caa429518e9ab4d'
resource=read(P/'resource/report.json');assert resource['status']=='pass' and resource['kernel_launches']==0 and resource['timings'] is False
resource_exit=passed(P/'resource/native','postflop_wide_turn_resources')
rrows=markers(P/'resource/native/stdout.log','WIDE_RESOURCE');assert rrows==resource['records'] and len(rrows)==4
for row,dynamic,blocks,regs in zip(rrows[1:3],[13160,21808],[6,4],[40,38]):
    assert row['kernel']=='up_show' and row['kernel_launches']==0 and row['solver_executions']==0 and row['performance_measurement'] is False
    assert row['dynamic_shared_bytes']==dynamic and row['static_shared_bytes']==1040 and row['local_bytes_per_thread']==0
    assert row['nh_o']==1128 and row['max_valid_opponent_hands']==1081 and row['registers']==regs
    assert row['occupancy_blocks_per_sm_128']==blocks and row['fits_queried_default_shared_and_thread_limits'] is True
    assert row['static_plus_dynamic_shared_bytes']==dynamic+1040<=rrows[0]['max_shared_bytes_per_block_default']
assert resource['binary_sha256']==binaries['E015-resource']['binary_sha256'] and resource['build_manifest_sha256']==binaries['E015-resource']['manifest_sha256']
assert sha(P/'cohort/report.json')=='97061633cd79146984c66494d5119aaf628078c47488e2486122dd1d92ee25f4'
cohort=read(P/'cohort/report.json');fixture=read(P/'fixture.json')
assert cohort['protocol_sha256']==sha(P/'plan-protocol.json')=='33d4a047f67d1b23bd125cbfc8c31b564b6cf6a8417da768023beb8389c71510'
assert list(cohort['run_report_sha256'])==ORDER
assert sorted(d.name for d in (P/'cohort').iterdir() if d.is_dir())==sorted(ORDER)
assert not list((P/'resource').rglob('failure.json')) and not list((P/'cohort').rglob('failure.json'))
results={};proofs={};prior_end=datetime.datetime.fromisoformat(resource_exit['at'])
for label in ORDER:
    d=P/'cohort'/label;assert sha(d/'report.json')==cohort['run_report_sha256'][label]
    rr=read(d/'report.json');inv=read(d/'invocation.json');exit=passed(d,'postflop_wide_turn_holdout')
    start=datetime.datetime.fromisoformat(inv['at']);end=datetime.datetime.fromisoformat(exit['at']);assert prior_end<start<end;prior_end=end
    name=('E015' if label.startswith('B') else 'E020')+'-holdout'
    assert Path(inv['args'][0])==P/'build/binaries'/f'{name}.exe'
    assert inv['args'][1:]==['postflop_wide_turn_holdout','--exact','--ignored','--nocapture','--test-threads=1']
    assert inv['environment']['RAYON_NUM_THREADS']=='16' and inv['compiler_override_absence_check']['present']=={}
    assert Path(inv['environment']['POSTFLOP_HOLDOUT_STATE'])==d/'state.bin'
    assert rr['binary_sha256']==binaries[name]['binary_sha256'] and rr['build_manifest_sha256']==binaries[name]['manifest_sha256']
    rows=markers(d/'stdout.log','AUTORESEARCH_RESULT');assert len(rows)==1 and rows[0]==rr['result'];r=rows[0]
    stages=markers(d/'stdout.log','AUTORESEARCH_STAGE');s0=stages[0];assert s0['stage']=='suite_start' and s0['profile_after_timing'] is False and s0['primary_suite'] is False and s0['fixture_filter'] is None
    assert r['config']==fixture and r['algorithm']=='Dcfr' and r['storage']=='compressed' and r['use_isomorphism'] is True
    assert r['iteration']==120 and r['max_iterations']==400 and r['target_pct']==0.3 and r['check_every']==20 and r['target_met'] is True
    assert r['nodes']==9387 and r['cpu_arena_bytes']==40550640
    for key in TIMING:assert math.isfinite(r[key]) and r[key]>=0
    timing=next(s for s in stages if s['stage']=='timing_complete')
    for key in TIMING-{'fingerprint_ms_excluded'}:assert timing[key]==r[key]
    checks=[{k:s[k] for k in ['iteration','exploit_bits','exploit_pct_pot','exploit_chips']} for s in stages if s['stage']=='convergence_check']
    assert checks==rr['checks'] and [s['iteration'] for s in checks]==list(range(20,121,20))
    assert all(s['exploit_pct_pot']>0.3 for s in checks[:-1]) and checks[-1]['exploit_pct_pot']<=0.3
    assert checks[-1]['exploit_bits']==r['exploit_bits']==4583032647229998282
    for s in checks:assert struct.unpack('<Q',struct.pack('<d',s['exploit_chips']))[0]==s['exploit_bits']
    admission=next(s for s in stages if s['stage']=='holdout_admission');assert admission==rr['admission']
    assert admission['hands']==[1128,1128] and admission['river_max']==[1081,1081] and admission['river_cards']==48
    assert admission['public_vram_estimate_bytes']<=admission['gpu_budget_bytes']==2*1024**3 and admission['duplicate_plan_built'] is False
    decoded=raw(d/'state.bin',r,P/'cohort/B1/state.bin');assert decoded==rr['raw_state']
    assert sum(x['payload_bytes'] for x in decoded['frames'])==r['cpu_arena_bytes']
    rawstage=next(s for s in stages if s['stage']=='raw_state_complete');assert rawstage['bytes']==decoded['bytes']
    assert stages[-1]['stage']=='suite_complete' and stages[-1]['fixtures_completed']==1
    if label!='B1':
        assert {k:v for k,v in r.items() if k not in TIMING}=={k:v for k,v in results['B1'].items() if k not in TIMING}
        assert checks==proofs['B1']['checks']
    results[label]=r;proofs[label]={'checks':checks,'state':decoded,'start':inv['at'],'end':exit['at'],'binary':name,'stdout_sha256':sha(d/'stdout.log'),'stderr_sha256':sha(d/'stderr.log'),'report_sha256':sha(d/'report.json')}
b=[results['B'+str(i)]['full_cycle_ms'] for i in range(1,4)];c=[results['C'+str(i)]['full_cycle_ms'] for i in range(1,4)]
paired=[100*(y/x-1) for x,y in zip(b,c)];medianchange=100*(statistics.median(c)/statistics.median(b)-1)
reject=medianchange>3 and sum(x>3 for x in paired)>=2
assert b==cohort['baseline_full_cycle_ms'] and c==cohort['candidate_full_cycle_ms'] and paired==cohort['paired_slowdown_pct'] and medianchange==cohort['median_slowdown_pct']
assert cohort['repeatable_regression']==reject==False and cohort['pairs_over_3pct']==0 and cohort['status']=='pass'
assert cohort['candidate_accepted'] is False and cohort['deployment_changed'] is False
validation={'id':'E020-holdout-independent-review','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'verdict':'PASS_HOLDOUT_NONREGRESSION_ONLY','resource_feasible':True,'theoretical_blocks_per_sm':[6,4],'resource_kernel_launches':0,'order':ORDER,'all_six_raw_files_byte_equal_to_B1':True,'raw_bytes_per_run':40550834,'common_raw_sha256':proofs['B1']['state']['sha256'],'all_six_complete_non_timing_results_exact':True,'timing_fields_excluded':sorted(TIMING),'all_six_convergence_trajectories_exact':True,'iteration':120,'exploit_bits':4583032647229998282,'baseline_full_cycle_ms':b,'candidate_full_cycle_ms':c,'baseline_median_ms':statistics.median(b),'candidate_median_ms':statistics.median(c),'median_slowdown_pct':medianchange,'paired_slowdown_pct':paired,'repeatable_regression':reject,'binary_identity':binaries,'run_proofs':proofs,'checked_input_sha256':PINS,'candidate_accepted':False,'deployment_changed':False,'audit_builds':0,'audit_gpu_jobs':0}
with (OUT/'validation.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(validation,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in validation.items() if k not in ['run_proofs','checked_input_sha256']},indent=2))
