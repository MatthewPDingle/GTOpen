"""D067 independent retained-file audit; no package imports or native workload calls."""
from pathlib import Path
import collections, datetime, hashlib, json, re, struct, subprocess, traceback
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016'); REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
P=R/'runs/D067-planned-show-incidence'; O=R/'comparisons/D067-independent-review'
checks=[]; pins={}
def need(ok,label):
    if not ok: raise AssertionError(label)
    checks.append(label)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p,h=None):
    p=Path(p); x=sha(p)
    if h is not None: need(x==h,'SHA '+str(p))
    pins[str(p)]=x; return x
def read(p,h=None): pin(p,h); return json.loads(Path(p).read_text('utf-8'))
def parse(text,prefix): return [json.loads(x.split(prefix,1)[1]) for x in text.splitlines() if prefix in x]
def write(p,x):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:f.write(x if isinstance(x,str) else json.dumps(x,indent=2,allow_nan=False)+'\n')
def fnv(b):
    h=14695981039346656037
    for x in b:h=((h^x)*1099511628211)&0xffffffffffffffff
    return f'{h:016x}'
def audit():
    seal=read(P/'scripts-manifest.json','592c0f55f2da699949b241a14f90549681a93849ae9b6e2157d09f4191cfa2d7')
    for n,h in seal['script_sha256'].items():pin(P/n,h)
    for n,h in seal['reference_sha256'].items():pin(n,h)
    protocol=read(P/'protocol.json'); source=read(P/'source/source-manifest.json'); schema=read(P/'source/output-schema.json')
    auth=read(P/'authorization.json','2ea35712a3040028be519616ae3fd532de43d51c4c211879791343de347cc103')
    for n,h in auth['evidence_sha256'].items():pin(n,h)
    need(auth['candidate']=='D067' and all(auth[k] is True for k in ['E020_accepted','E020_server_qualification_pass','independent_source_review_pass','independent_script_review_pass']),'root authorization scope')
    for role,gate in protocol['prerequisite_reports'].items():
        p=auth['prerequisites'][role]; v=read(p['path'],p['sha256'])
        need(p['path']==gate['path'] and all(v[k]==x for k,x in gate['required_fields'].items()),'prerequisite '+role)
    activation=read(R/'runs/D067-source/activation.json','31eda00150eb316227d027a8e798be8eea11ce164629c4d9135eeb6157777e02')
    cleanup=read(R/'runs/D067-cleanup/report.json','3804b6c76687a39bd167788df3800c09c7c4186000b16c79501c1eadf1a3df62')
    accepted=read(R/'binaries/E020-postflop_autoresearch.manifest.json')['source_sha256']
    expected=dict(accepted); expected.update(source['candidate_sha256'])
    need(len(accepted)==162 and len(expected)==163,'162 accepted / 163 temporary source inventory')
    need(activation['source_before']['source_sha256']==accepted and activation['source_after']['source_sha256']==expected,'exact two-file activation')
    need(activation['authorization_sha256']==sha(P/'authorization.json') and activation['temporary_test_only'] is True,'activation authorization binding')
    before=read(R/'runs/D067-build/source-before.json'); manifest=read(R/'binaries/D067-solver.manifest.json')
    inv=read(R/'runs/D067-execution/invocation.json'); run=read(R/'runs/D067R1/report.json')
    need(before['source_sha256']==manifest['source_sha256']==inv['source_sha256']==run['provenance']['source_sha256']==expected,'actual build/run candidate source identity')
    for n,v in manifest['source_copies'].items():pin(v['path'],source['candidate_sha256'][n])
    for n,v in cleanup['preserved_candidate_sources'].items():pin(v['path'],source['candidate_sha256'][n])
    need(set(manifest['source_copies'])==set(cleanup['preserved_candidate_sources'])==set(source['candidate_sha256']),'owned source copies complete')
    build_exit=read(R/'runs/D067-build/exit.json',cleanup['build_exit_sha256']); exit_record=read(R/'runs/D067-execution/exit.json',cleanup['execution_exit_sha256']); complete=read(R/'runs/D067-execution/complete.json')
    need(build_exit['returncode']==exit_record['returncode']==run['returncode']==0 and all(v['error'] is None and v['cleanup'] is None for v in [build_exit,exit_record]),'terminal build/run zero without interrupted cleanup')
    need(auth['at']<=activation['at']<=build_exit['at']<=manifest['built_at']<=inv['at']<=run['process_started_at']<=run['finished_at']<=exit_record['at']<=cleanup['at'],'root/build/run/cleanup chronology')
    cmd=['cargo','test','--release','--locked','--offline','-p','solver','--features','gpu','--lib','--no-run','--message-format=json']
    need(build_exit['command']==manifest['build_command']==cmd,'single registered compile-only command')
    env=read(R/'runs/D067-build/build-environment.json')
    need(env['target_previously_absent'] is True and env['compiler_override_absence']=={} and env['target_dir']==manifest['target_dir']==protocol['build_target_root'],'fresh build target and absent overrides')
    for key,hkey in [('build_log','build_log_sha256'),('build_stderr_log','build_stderr_sha256'),('patch','patch_sha256')]:pin(manifest[key],manifest[hkey])
    need(manifest['patch_sha256']==sha(P/'source/candidate.patch'),'complete frozen patch used')
    cargo=[json.loads(x) for x in Path(manifest['build_log']).read_text('utf-8').splitlines()]
    need(cargo[-1]['reason']=='build-finished' and cargo[-1]['success'] is True,'Cargo terminal success')
    need(not any(x.get('reason')=='compiler-message' and x['message']['level'] in ['error','failure-note'] for x in cargo),'no Cargo errors')
    a=[x for x in cargo if x.get('reason')=='compiler-artifact' and x.get('executable') and x['target']['name']=='solver']
    need(len(a)==1 and a[0]==manifest['cargo_artifact'] and a[0]['fresh'] is False and a[0]['features']==['gpu'] and a[0]['profile']['test'] is True,'fresh gpu-only library test artifact')
    need(Path(a[0]['target']['src_path'])==REPO/'crates/solver/src/lib.rs' and Path(a[0]['manifest_path'])==REPO/'crates/solver/Cargo.toml','compiled exact crate source')
    need(all(Path(f).is_relative_to(Path(manifest['target_dir'])) for x in cargo if x.get('reason')=='compiler-artifact' for f in x.get('filenames',[])),'all Cargo outputs in pristine target')
    binary=Path(protocol['binary']); pin(binary,manifest['binary_sha256']); pin(a[0]['executable'],manifest['binary_sha256'])
    need(sha(binary)==inv['binary_sha256']==run['binary_sha256'] and sha(R/'binaries/D067-solver.manifest.json')==inv['build_manifest_sha256'],'frozen/linked/executed binary identity')
    need(run['binary_build_manifest']['data']==manifest and run['binary_build_manifest']['sha256']==inv['build_manifest_sha256'],'runner complete build manifest binding')
    need(manifest['probe_authorization_sha256']==sha(P/'authorization.json') and manifest['probe_evidence_sha256']==auth['evidence_sha256'] and manifest['primary_protocol_sha256']==sha(P/'protocol.json'),'build authorization/protocol binding')
    data=binary.read_bytes(); cuda=(R/'runs/E035-design/base/kernels.cu').read_bytes()
    need(cuda in data and b'D067_PLANNED_SHOW_INCIDENCE' in data,'unchanged accepted CUDA and selected helper embedded')
    rawpath=R/'runs/D067R1/stdout.log'; pin(rawpath,run['stdout_sha256']); raw=rawpath.read_text('utf-8')
    for name in ['stdout.log','stderr.log']:pin(R/'runs/D067-execution'/name)
    need(not (R/'runs/D067-execution/stderr.log').read_text('utf-8').strip(),'empty wrapper stderr')
    need(not any(x in raw for x in ['panicked at','FAILED','D067 planned-show mapping failed']),'no raw native failure')
    need(re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',raw)==[('1','0','0','0','88')],'exact selected test summary')
    need(run['command']==[str(binary),protocol['test_filter'],'--nocapture','--test-threads=1','--ignored'] and run['test_pass_count']==1,'exact one selected ignored test')
    need(run['id']=='D067R1' and run['kind']=='diagnostic' and run['fixture'] is None and run['results']==[] and run['stages']==[] and run['accepted'] is False,'no benchmark/solve output or acceptance')
    need(sorted(x.name for x in (R/'runs').glob('D067R*'))==['D067R1'],'one registered native run directory only')
    need(complete['native_test_pass'] is True and complete['actual_run']=='D067R1' and complete['performance_acceptance'] is False,'wrapper terminal complete')
    for k in ['live_status_before','live_status_at_launch']:
        x=run[k]; need(not x['/api/status']['gpu'] and not x['/api/preflop/status']['gpu'] and not x['/api/reports/status']['running'],'live idle '+k)
    records=parse(raw,protocol['marker']); need(len(records)==5 and [(x['stage'],x.get('fixture_id')) for x in records]==[('admission',None),('fixture_mapping','rainbow'),('fixture_mapping','two-tone'),('fixture_mapping','river'),('complete',None)],'five complete markers in fixed order')
    need(records[0]['cpu_only'] is True and records[0]['gpu_calls']==0 and records[0]['available_host_ram_bytes']>=records[0]['required_available_host_ram_bytes']==16*1024**3,'CPU-only memory admission')
    need(records[-1]=={'stage':'complete','fixtures':3,'fold_mapping_exact':True,'fold_mapping_checks':3,'planned_show_mapping_files':3,'cpu_only':True,'gpu_calls':0,'planned_source_only':True,'new_show_upload_validation':False,'performance_measurement':False,'candidate_accepted':False},'all-three fold gate complete')
    inputs=read(P/'source/inputs.json'); oldraw=Path(protocol['historical_raw_path']).read_text('utf-8'); oldrecords=parse(oldraw,'D066_FOLD_ZERO_CENSUS ')
    oldgeo={x['fixture_id']:x for x in oldrecords if x['stage']=='geometry'}
    for i,(rec,inp) in enumerate(zip(records[1:4],inputs)):
        old=oldgeo[rec['fixture_id']]
        need(set(rec)==set(schema['fixture_mapping_fields'])|{'stage'} and rec['fixture_index']==i,'exact fixture record schema')
        need(rec['fold_mapping_exact'] is True and rec['planned_source_only'] is True and rec['new_show_upload_validation'] is False and rec['cleanup_complete'] is True,'native mapping/cleanup assertions')
        need(inp['geometry']==old and all(rec[k]==old[k] for k in ['nodes','nh','reach_blocks','fold_spans','fold_ctas_per_traverser']) and rec['fold_mapping']==old['mapping'],'all recorded historical geometry and complete fold metadata')
    # All three native fold assertions and complete marker above precede any incidence join below.
    maps=read(R/'runs/D067-execution/mapping-artifacts.json',complete['mapping_artifacts_sha256']); directory=Path(maps['mapping_directory'])
    need(directory==Path(protocol['mapping_directory']) and set(maps['files'])==set(protocol['expected_files'])=={x.name for x in directory.iterdir()},'exact new map inventory')
    catalog=read(protocol['historical_catalog_path']); historical=Path(protocol['historical_census_directory'])
    need(catalog['files']==protocol['historical_input_files'] and len(catalog['files'])==15,'immutable historical inventory')
    for n,x in catalog['files'].items():pin(historical/n,x['sha256']);need((historical/n).stat().st_size==x['bytes'],'historical bytes '+n)
    assessed=read(R/'comparisons/D067-planned-show-incidence/report.json','bc2abc4281d230d3e8348758bd12795c3ec5a8bf00d6a2c0ac074ba57f831c94')
    need(assessed['status']=='pass' and assessed['protocol_sha256']==sha(P/'protocol.json') and assessed['binary_sha256']==sha(binary) and assessed['performance_measurement'] is False and assessed['candidate_accepted'] is False,'assessment identity and scope')
    recomputed=[]; levels_compared=0
    names=['show_ctas','all_positive_zero','any_negative_zero','any_finite_nonzero','any_nonfinite','finite_payouts','all_positive_zero_and_finite_payouts','empty_own_sorted','empty_opponent_sorted','all_positive_zero_and_empty_own','all_positive_zero_and_empty_opponent']
    for rec,af in zip(records[1:4],assessed['fixtures']):
        fid=rec['fixture_id']; need(af['fixture_id']==fid,'fixture result order')
        name=rec['mapping']['file']; pin(directory/name,maps['files'][name]['sha256']); payload=(directory/name).read_bytes()
        need(len(payload)==maps['files'][name]['bytes']==rec['mapping']['bytes']==36*rec['show_ctas_per_traverser'] and fnv(payload)==rec['mapping']['fnv1a64'],'new complete mapping codec/hash '+fid)
        rows=list(struct.iter_unpack('<9I',payload)); need(len({x[0] for x in rows})==len(rows),'unique planned node IDs '+fid)
        spans=rec['show_spans']; cursor=0
        for l,sp in enumerate(spans):need(sp['level']==l and sp['start']==cursor and sp['count']>=0,'contiguous span '+fid+'/'+str(l));cursor+=sp['count']
        need(cursor==len(rows) and len(spans)==rec['num_levels'] and af['show_spans']==spans and af['show_ctas_per_traverser']==len(rows),'complete planned worklist '+fid)
        need(all(n<rec['nodes'] and s0<rec['reach_blocks'][0] and s1<rec['reach_blocks'][1] and rs<rec['num_slots'] and m0<=rec['nh'][0] and m1<=rec['nh'][1] for n,s0,s1,rs,w,l,t,m0,m1 in rows),'all node/row/river/hand bounds '+fid)
        for snap in af['historical_snapshots']:
            iteration=snap['historical_iteration']; need(iteration in protocol['snapshot_iterations'][fid],'fixed historical snapshot')
            need([(a['opponent'],a['traverser']) for a in snap['arrays']]==[(0,1),(1,0)],'both traversers once')
            for a in snap['arrays']:
                q=a['opponent']; p=1-q; flagname=f'{fid}-iteration{iteration}-reach{q}.rowflags'; flags=(historical/flagname).read_bytes()
                need(len(flags)==rec['reach_blocks'][q] and all(x<=7 for x in flags),'logical rowflags geometry '+flagname)
                totals=[0]*11; all_levels=[]
                for sp in spans:
                    ct=[0]*11
                    for row in rows[sp['start']:sp['start']+sp['count']]:
                        flag=flags[row[q+1]]; zero=flag==0; finite=all(((x>>23)&255)!=255 for x in row[4:7]); own_empty=row[7+p]==0; opp_empty=row[7+q]==0
                        values=[1,zero,bool(flag&1),bool(flag&2),bool(flag&4),finite,zero and finite,own_empty,opp_empty,zero and own_empty,zero and opp_empty]
                        ct=[v+int(x) for v,x in zip(ct,values)]
                    totals=[v+x for v,x in zip(totals,ct)]; all_levels.append({**sp,'counts':dict(zip(names,ct))})
                counted=dict(zip(names,totals)); need(counted==a['planned_show_counts'] and all_levels==a['levels'],'independent all categories/levels '+flagname);levels_compared+=len(spans)
                need(a['all_positive_zero_fraction']==totals[1]/len(rows) and a['finite_payout_eligible_fraction']==totals[6]/len(rows),'reported fractions '+flagname)
                recomputed.append({'fixture_id':fid,'historical_iteration':iteration,'traverser':p,'opponent':q,'counts':counted,'levels':all_levels,'finite_payout_eligible_percent':100*totals[6]/len(rows)})
    need(len(recomputed)==12 and len({(x['fixture_id'],x['historical_iteration'],x['traverser']) for x in recomputed})==12,'twelve unique fixed incidence totals')
    need(cleanup['status']=='restored' and cleanup['source_before']['source_sha256']==expected and cleanup['source_after']['source_sha256']==accepted and cleanup['all162_accepted_entries_exact'] is True,'candidate archived and accepted sources restored')
    for name,h in accepted.items():pin(REPO/name,h)
    need(not (REPO/'crates/solver/src/gpu/planned_show_incidence.rs').exists(),'temporary helper removed')
    for n,x in protocol['preexisting_target_artifacts'].items():pin(REPO/n,x['sha256']);need((REPO/n).stat().st_size==x['bytes'],'preserved PTX size')
    live=Path(r'X:\Dev\GTOpen\target\desktop-runtime\release\gto-server.exe');pin(live,cleanup['live_exe_sha256'])
    need(cleanup['live_exe_sha256']==activation['live_binary_sha256']=='b7b808b8baff6b3a92c4f3cc8c54ee74ee2c0bb079a8ca68be4da9703f6b84bd','exact live executable unchanged')
    mainhead=subprocess.check_output(['git','-C',r'X:\Dev\GTOpen','rev-parse','HEAD'],text=True).strip()
    need(mainhead==cleanup['main_head']==activation['main_head']=='ae823c8bd6d723c75e096da139fd638d7dd397eb','main HEAD unchanged')
    need(not (R/'gpu-run.lock').exists(),'research execution lock released')
    write(O/'recomputed-incidence.json',{'id':'D067','totals':recomputed,'level_rows_compared':levels_compared,'performance_measurement':False})
    return {'id':'D067','verdict':'PASS_SCOPED_PLANNED_INCIDENCE_AUDIT','independent_terminal_audit_pass':True,'mapping_validation_pass':True,'incidence_recomputation_pass':True,'custody_and_cleanup_pass':True,'actual_run':'D067R1','test_summary':{'passed':1,'failed':0,'ignored':0,'measured':0,'filtered':88},'marker_count':5,'fold_maps_matched':3,'planned_mapping_files':3,'historical_flag_files':12,'incidence_totals_recomputed':12,'level_rows_compared':levels_compared,'current_accepted_source_entries':162,'binary_sha256':sha(binary),'performance_measurement':False,'candidate_accepted':False,'new_gpu_snapshots':0,'new_checkpoints':0,'new_full_state_tests':0,'compiler_native_gpu_executed_by_reviewer':False,'scope':'CPU planned-showdown mapping joined to six historical D066 pre-evaluation training boundaries only.','limitations':['Fold-byte equality rests on the reviewed native exact comparison and successful five-marker execution, not a new retained regenerated fold dump.','Show/river/tie mappings are source-derived CPU plan metadata, not newly downloaded GPU metadata. Historical rowflags are source-pinned D066 classifications; raw reach floats were not retained.','This audit does not establish shortcut output correctness, all-iteration incidence, latency, savings or complete-cycle headroom. No new solve or performance cohort was run.'],'reviewer_observations':['An initial unrestricted JSON display was truncated by output limits; subsequent reads selected required fields. No assertion or evidence changed.']}
try:
    result=audit(); result.update(created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),checks_passed=checks,input_sha256=pins)
    write(O/'report.json',result)
    write(O/'summary.md','D067 independent audit passed: one CPU-only selected invocation, three native fold-map matches, five markers and all twelve planned incidence totals/per-level categories reproduced from retained maps and historical flags. Accepted E020 source, two PTX files, main HEAD and live executable are restored/unchanged. No timing or shortcut-correctness claim.\n')
    write(O/'manifest.json',{'id':'D067-independent-review','artifact_sha256':{p.name:sha(p) for p in O.iterdir() if p.is_file()},'performance_measurement':False,'candidate_accepted':False})
    print(json.dumps({'verdict':result['verdict'],'checks':len(checks),'pins':len(pins),'report_sha256':sha(O/'report.json'),'manifest_sha256':sha(O/'manifest.json')}))
except BaseException as error:
    path=O/('reviewer-failure-'+str(len(list(O.glob('reviewer-failure-*.json')))+1)+'.json')
    write(path,{'error':repr(error),'traceback':traceback.format_exc(),'checks_passed':checks,'input_sha256':pins});raise