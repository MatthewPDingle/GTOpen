"""Assess the one fixed fold-input census; no timing measurement or acceptance."""
import collections, hashlib, json, math, re, struct, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
HERE=Path(__file__).resolve().parent
OUT=ROOT/'comparisons/D066-fold-zero-census'
artifacts={};checks=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(condition,label):
    if not condition:raise AssertionError(label)
    checks.append(label)
def artifact(path,expected=None):
    path=Path(path);actual=sha(path)
    if expected is not None:need(actual==expected,'pin '+str(path))
    artifacts[str(path)]=actual
    return actual
def read(path,expected=None):artifact(path,expected);return json.loads(Path(path).read_text(encoding='utf-8'))
def markers(text,prefix):return [json.loads(line.split(prefix,1)[1]) for line in text.splitlines() if prefix in line]
def write(name,value):
    with (OUT/name).open('x',encoding='utf-8',newline='\n') as f:
        f.write(value if isinstance(value,str) else json.dumps(value,indent=2,allow_nan=False)+'\n')
def finite(value):return isinstance(value,(float,int)) and not isinstance(value,bool) and math.isfinite(value) and value>=0

def fnv(data):
    h=0xcbf29ce484222325
    for b in data:h=((h^b)*0x100000001b3)&0xffffffffffffffff
    return f'{h:016x}'

def whole(value):return type(value) is int and value>=0

def tally(rows,flags,p,start,count):
    result=dict.fromkeys(['fold_ctas','all_positive_zero','any_negative_zero','any_finite_nonzero','any_nonfinite','finite_selected_amount','all_positive_zero_and_finite_amount'],0)
    result['fold_ctas']=count
    for row in rows[start:start+count]:
        flag=flags[row[1+(1-p)]]
        finite_amount=(row[3+p]&0x7f800000)!=0x7f800000
        result['all_positive_zero']+=int(flag==0)
        result['any_negative_zero']+=int(bool(flag&1))
        result['any_finite_nonzero']+=int(bool(flag&2))
        result['any_nonfinite']+=int(bool(flag&4))
        result['finite_selected_amount']+=int(finite_amount)
        result['all_positive_zero_and_finite_amount']+=int(flag==0 and finite_amount)
    return result


def assess():
    need(len(sys.argv)==2,'root authorization SHA argument')
    auth=read(HERE/'authorization.json',sys.argv[1])
    need(auth['candidate']=='D066' and all(auth[k] is True for k in ['E020_accepted','E020_server_qualification_pass','independent_source_review_pass','independent_script_review_pass']),'registered source/script prerequisites')
    seal=read(HERE/'scripts-manifest.json',auth['evidence_sha256'][str(HERE/'scripts-manifest.json')])
    need(seal['status']=='FROZEN_PROSPECTIVE_NOT_EXECUTED','prospective seal')
    for path,h in auth['evidence_sha256'].items():artifact(path,h)
    for path,h in seal['script_sha256'].items():artifact(HERE/path,h)
    for path,h in seal['reference_sha256'].items():artifact(path,h)
    protocol=read(HERE/'protocol.json','43916bb15c53ab011964ef7e37946caa2bb6c1e91c42af4f68888b3b9eaad389')
    source=read(HERE/'source/source-manifest.json',protocol['source_archive_sha256'])
    schema=read(HERE/'source/output-schema.json',protocol['schema_sha256'])
    for name,h in source['artifact_sha256'].items():artifact(HERE/'source'/name,h)
    report=read(ROOT/'runs/D066R1/report.json')
    raw_path=ROOT/'runs/D066R1/stdout.log';artifact(raw_path,report['stdout_sha256'])
    raw=raw_path.read_text(encoding='utf-8')
    records=markers(raw,protocol['marker']);write('parsed-records.json',records)
    build_exit=read(ROOT/'runs/D066-build/exit.json')
    execution=read(ROOT/'runs/D066-execution/invocation.json')
    execution_exit=read(ROOT/'runs/D066-execution/exit.json')
    execution_complete=read(ROOT/'runs/D066-execution/complete.json')
    for name in ['stdout.log','stderr.log']:artifact(ROOT/'runs/D066-execution'/name)
    need(build_exit['returncode']==execution_exit['returncode']==report['returncode']==0,'build and native terminal success')
    need(execution_exit['error'] is None and execution_exit['cleanup'] is None,'no interrupted native process')
    need(report['id']=='D066R1' and report['kind']=='diagnostic' and report['fixture'] is None and report['status']=='measured' and report['test_pass_count']==1 and report['accepted'] is False,'exact one diagnostic and no acceptance')
    need(execution_complete['actual_run']=='D066R1' and execution_complete['native_test_pass'] and execution_complete['performance_acceptance'] is False,'fixed invocation terminal record')
    need(execution['actual_run']=='D066R1' and execution['logical_dashboard_row']=='D066' and execution['performance_acceptance'] is False,'fixed logical/run identity')
    need(execution['authorization_sha256']==sys.argv[1] and execution['protocol_sha256']==sha(HERE/'protocol.json') and execution['script_sha256']==sha(HERE/'run.py'),'execution sealed inputs')
    need(build_exit['at']<=execution['at']<=report['process_started_at']<=report['finished_at']<=execution_exit['at'],'build before run chronology')
    manifest_path=ROOT/'binaries/D066-solver.manifest.json'
    manifest=read(manifest_path,execution['build_manifest_sha256'])
    need(report['binary_build_manifest']['path']==str(manifest_path) and report['binary_build_manifest']['sha256']==sha(manifest_path) and report['binary_build_manifest']['data']==manifest,'runner embedded manifest identity')
    binary=ROOT/'binaries/D066-solver.exe'
    artifact(binary,manifest['binary_sha256'])
    need(manifest['binary_sha256']==execution['binary_sha256']==report['binary_sha256'],'binary build/run identity')
    need(manifest['candidate']=='D066' and manifest['test_only_append_verified'] and manifest['source_matches_prebuild'],'test-only source scope verified')
    need(manifest['primary_protocol_sha256']==sha(HERE/'protocol.json') and manifest['build_script_sha256']==sha(HERE/'build.py') and manifest['probe_authorization_sha256']==sys.argv[1] and manifest['probe_evidence_sha256']==auth['evidence_sha256'],'build sealed inputs')
    for key,hkey in [('build_log','build_log_sha256'),('build_stderr_log','build_stderr_sha256'),('patch','patch_sha256')]:artifact(manifest[key],manifest[hkey])
    need(manifest['patch_sha256']==sha(HERE/'source/candidate.patch'),'complete archived patch includes new helper')
    before=read(ROOT/'runs/D066-build/source-before.json')
    need(before['source_sha256']==manifest['source_sha256']==execution['source_sha256']==report['provenance']['source_sha256'] and len(before['source_sha256'])==163,'163 build/run source identities exact')
    for name,h in before['source_sha256'].items():artifact(REPO/name,h)
    for value in manifest['source_copies'].values():artifact(value['path'],value['sha256'])
    need(report['command']==[str(binary),protocol['test_filter'],'--nocapture','--test-threads=1','--ignored'],'exact ignored diagnostic invocation')
    need(re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',raw)==[('1','0','0','0','88')],'one executed test and88 filtered')
    need(not any(s in raw for s in ['D066_SOLVER_CLEANUP_ERROR','panicked at','D066 invalid diagnostic']),'no native cleanup/panic error')
    need(not (ROOT/'runs/D066-execution/stderr.log').read_text(encoding='utf-8').strip(),'no orchestration stderr error')
    for key,value in [('RAYON_NUM_THREADS','16'),('POSTFLOP_AUTORESEARCH_PROFILE','0'),('POSTFLOP_AUTORESEARCH_STORAGE','compressed'),('POSTFLOP_AUTORESEARCH_FIXTURE',None)]:need(report['environment'][key]==value,'fixed env '+key)
    for snapshot in ['live_status_before','live_status_at_launch']:
        snap=report[snapshot];need(not snap['/api/status']['gpu'] and not snap['/api/preflop/status']['gpu'] and not snap['/api/reports/status']['running'],'live idle '+snapshot)
    anchors=read(HERE/'design/anchors.json')
    expected_order=[]
    for a in anchors:
        f=a['fixture_id']; expected_order.extend([('admission',f,None),('geometry',f,None)])
        for i in range(20,a['final_iteration']+1,20):
            if i in [20,a['final_iteration']]:expected_order.append(('snapshot',f,i))
            expected_order.append(('checkpoint',f,i))
        expected_order.append(('final_anchor_exact',f,a['final_iteration']))
    expected_order.append(('complete',None,None))
    need(expected_order==[(r['stage'],r.get('fixture_id'),r.get('iteration')) for r in schema['expected_stage_order']]==[(r['stage'],r.get('fixture_id'),r.get('iteration')) for r in protocol['expected_stage_order']],'frozen schema and derived order exact')
    need(len(records)==39 and [(r['stage'],r.get('fixture_id'),r.get('iteration')) for r in records]==expected_order,'all39 records in fixed fixture/checkpoint order')
    need(not markers(raw,'AUTORESEARCH_RESULT '),'no benchmark or performance-result records')
    for run in ['B065','E020C1']:
        hist=read(ROOT/f'runs/{run}/report.json')
        lp=ROOT/f'runs/{run}/stdout.log';artifact(lp,hist['stdout_sha256'])
        text=lp.read_text(encoding='utf-8');results=markers(text,'AUTORESEARCH_RESULT ')
        need(results==hist['results'] and [x['fixture_id'] for x in results]==protocol['expected_fixtures'],'historical complete suite '+run)
        for a,r in zip(anchors,results):
            need(r['config']==a['config'] and r['state_fingerprint']==a['state_fingerprint'],'historical complete config/state '+run+'/'+a['fixture_id'])
            conv=[{'iteration':x['iteration'],'exploit_bits':x['exploit_bits']} for x in markers(text,'AUTORESEARCH_STAGE ') if x.get('stage')=='convergence_check' and x.get('fixture_id')==a['fixture_id']]
            need(conv==a['convergence'],'historical convergence anchors '+run+'/'+a['fixture_id'])
    census=ROOT/'runs/D066-execution/census'
    need(execution['census_directory']==str(census),'fixed compact artifact directory')
    expected_env={'D066_CENSUS_DIR':str(census),'POSTFLOP_AUTORESEARCH_FIXTURE':None,'POSTFLOP_AUTORESEARCH_LIFECYCLE_PROFILE':None,'POSTFLOP_AUTORESEARCH_PROFILE':'0','POSTFLOP_AUTORESEARCH_STORAGE':'compressed','RAYON_NUM_THREADS':'16'}
    need(execution['run_env']==expected_env,'recorded exact runtime environment')
    catalog=read(ROOT/'runs/D066-execution/census-artifacts.json',execution_complete['census_artifacts_sha256'])
    expected_files={f'{f}-fold-mapping.u32le' for f in protocol['expected_fixtures']}
    expected_files|={f'{f}-iteration{i}-reach{q}.rowflags' for f in protocol['expected_fixtures'] for i in [20,protocol['expected_stops'][f]] for q in [0,1]}
    need(catalog['census_directory']==str(census) and catalog['raw_float_payload_retained'] is False,'compact evidence scope')
    need(expected_files==set(schema['expected_files'])==set(protocol['expected_files']),'frozen compact file inventory')
    need(set(catalog['files'])=={p.name for p in census.iterdir()}==expected_files and len(expected_files)==15,'all15 files without omissions or extras')
    for name,pin in catalog['files'].items():
        path=census/name
        need(path.is_file() and not path.is_symlink() and path.resolve().parent==census.resolve(),'owned regular census file '+name)
        artifact(path,pin['sha256']);need(path.stat().st_size==pin['bytes'],'census file byte size '+name)
    for name,pin in protocol['preexisting_target_artifacts'].items():
        artifact(REPO/name,pin['sha256']);need((REPO/name).stat().st_size==pin['bytes'],'preserved PTX size '+name)
    fixture_results=[];total_words=0
    for a in anchors:
        f=a['fixture_id']; subset=[x for x in records if x.get('fixture_id')==f]
        admission=next(x for x in subset if x['stage']=='admission')
        g=next(x for x in subset if x['stage']=='geometry')
        need(g['nodes']==a['nodes'] and g['nh']==a['nh'],'frozen fixture geometry '+f)
        need(g['uploaded_metadata_exact_both_arms'] is True and g['physical_reach_has_padding'] is False,'native uploaded metadata and unpadded E020 layout '+f)
        need(all(whole(v) and v>0 for v in g['nh']+g['reach_blocks']),'positive physical/logical geometry '+f)
        spans=g['fold_spans'];cursor=0
        for level,span in enumerate(spans):
            need(span['level']==level and span['start']==cursor and whole(span['count']),'contiguous fold span '+f+'/'+str(level))
            cursor+=span['count']
        need(cursor==g['fold_ctas_per_traverser'],'complete fold span coverage '+f)
        m=g['mapping'];mname=f'{f}-fold-mapping.u32le';data=(census/mname).read_bytes()
        need(m['file']==mname and len(data)==m['bytes']==20*cursor and fnv(data)==m['fnv1a64'],'mapping byte coverage/hash '+f)
        need(m['record']=='five little-endian u32: node,slot0,slot1,amount0bits,amount1bits','mapping codec '+f)
        rows=list(struct.iter_unpack('<IIIII',data))
        need(all(n<a['nodes'] and s0<g['reach_blocks'][0] and s1<g['reach_blocks'][1] for n,s0,s1,_,_ in rows),'every node/slot bound '+f)
        need(all(whole(v) for k,v in admission.items() if k not in ['stage','fixture_id','device_arena_elements']),'nonnegative admission counters '+f)
        need(admission['device_reserve_bytes']==2*1024**3 and admission['host_reserve_bytes']==8*1024**3 and admission['raw_compare_max_bytes']==8388608,'fixed reserves/chunk '+f)
        need(admission['host_free_before_spot']>=16*1024**3,'pre-Spot RAM admission '+f)
        need(admission['device_free_bytes']<=admission['device_total_bytes'] and admission['device_free_bytes']>=admission['dual_device_required_with_reserve']==2*admission['device_per_arm_payload_bytes']+2*1024**3,'dual GPU admission '+f)
        elems=admission['device_arena_elements'];need(len(elems)==2 and all(whole(v) and v>0 for v in elems),'actual device arena geometry '+f)
        need(admission['pinned_bytes_per_arm']==4*max(elems),'pinned arena extent '+f)
        need(admission['cpu_arena_bytes_per_arm']==sum(x['bytes'] for x in a['state_fingerprint']['arenas']),'full CPU arena bytes '+f)
        geometry_bytes=20*cursor+8*len(spans)+max(g['reach_blocks'])
        need(admission['compact_geometry_and_rowclass_bytes']==geometry_bytes,'compact geometry/flags admission '+f)
        host_required=2*admission['cpu_arena_bytes_per_arm']+2*admission['pinned_bytes_per_arm']+8388608+geometry_bytes+8*1024**3
        need(admission['host_additional_required']==host_required and admission['host_free_after_spot_and_plan']>=host_required,'dual host admission '+f)
        checkpoints=[x for x in subset if x['stage']=='checkpoint']
        need([{'iteration':x['iteration'],'exploit_bits':x['exploit_bits']} for x in checkpoints]==a['convergence'],'all immutable convergence bits '+f)
        need(all(x['ordinary_and_observed_exact'] is True and x['immutable_original_and_E020_anchor_exact'] is True for x in checkpoints),'both ordinary arms match anchors '+f)
        final=next(x for x in subset if x['stage']=='final_anchor_exact')
        need(final['complete_cpu_q_and_scale_bits_exact'] is True and final['cleanup_complete'] is True and final['state_fingerprint']==a['state_fingerprint'],'complete final compressed state and cleanup '+f)
        snapshots=[]
        for snap in [x for x in subset if x['stage']=='snapshot']:
            iteration=snap['iteration']
            need(snap['before_exploitability'] is True and snap['paired_reach_bits_exact'] is True and snap['raw_float_payload_retained'] is False and snap['performance_measurement'] is False,'pre-eval exact snapshot scope '+f+'/'+str(iteration))
            need(snap['chunk_floats']==1048576 and snap['peak_float_snapshot_bytes']==8388608,'bounded float snapshots '+f+'/'+str(iteration))
            need([(v['opponent'],v['traverser']) for v in snap['arrays']]==[(0,1),(1,0)],'both opponent reach arrays '+f+'/'+str(iteration))
            arrays=[]
            for arr in snap['arrays']:
                q=arr['opponent'];p=1-q;nh=g['nh'][q];nr=g['reach_blocks'][q]
                need(arr['logical_nh']==nh and arr['physical_rows']==nr and arr['entries']==nh*nr and arr['paired_bits_exact'] is True,'complete logical array equality '+f+'/'+str((iteration,q)))
                need(re.fullmatch('[0-9a-f]{16}',arr['reach_fnv1a64']) is not None,'native reach fingerprint encoding')
                total_words+=arr['entries']
                wc=arr['whole_reach_word_categories']
                need(set(wc)=={'positive_zero','negative_zero','finite_nonzero','nonfinite'} and all(whole(v) for v in wc.values()) and sum(wc.values())==nh*nr,'whole reach category coverage')
                fn=f'{f}-iteration{iteration}-reach{q}.rowflags';flags=(census/fn).read_bytes();rc=arr['rowclass']
                need(rc['file']==fn and rc['bytes']==len(flags)==nr and rc['fnv1a64']==fnv(flags) and all(v<=7 for v in flags),'exact row-flag codec/hash '+fn)
                rowclasses=collections.Counter(flags)
                need(wc['positive_zero']>=rowclasses[0]*nh and sum(wc[k] for k in ['negative_zero','finite_nonzero','nonfinite'])>=nr-rowclasses[0],'zero-row and nonzero-word consistency')
                for bit,name in [(1,'negative_zero'),(2,'finite_nonzero'),(4,'nonfinite')]:
                    count=sum(n for flag,n in rowclasses.items() if flag&bit)
                    need(count<=wc[name]<=count*nh,'row/word category bounds '+name)
                need(arr['fold_counts']==tally(rows,flags,p,0,cursor),'recomputed all-fold incidence '+fn)
                expected_levels=[{**sp,'counts':tally(rows,flags,p,sp['start'],sp['count'])} for sp in spans]
                need(arr['levels']==expected_levels,'recomputed every-level incidence '+fn)
                counts=arr['fold_counts']
                arrays.append({'opponent':q,'traverser':p,'entries':arr['entries'],'physical_rows':nr,'reach_fnv1a64':arr['reach_fnv1a64'],'whole_reach_word_categories':wc,'physical_row_flag_histogram':{str(k):rowclasses.get(k,0) for k in range(8)},'fold_counts':counts,'all_positive_zero_fraction':counts['all_positive_zero']/cursor if cursor else None,'eligible_finite_amount_fraction':counts['all_positive_zero_and_finite_amount']/cursor if cursor else None})
            snapshots.append({'iteration':iteration,'arrays':arrays})
        fixture_results.append({'fixture_id':f,'nh':g['nh'],'reach_blocks':g['reach_blocks'],'fold_ctas_per_traverser':cursor,'fold_spans':spans,'admission':admission,'snapshots':snapshots,'final_state_fingerprint':final['state_fingerprint']})
    complete=records[-1]
    need(complete=={'stage':'complete','fixtures':3,'snapshots':6,'reach_array_snapshots':12,'checkpoints':23,'final_full_state_checks':3,'mapping_files':3,'rowclass_files':12,'performance_measurement':False,'candidate_accepted':False},'exact complete marker')
    return {'id':'D066','actual_run':'D066R1','status':'pass','diagnostic_only':True,'exactness_pass':True,'census_validation_pass':True,'protocol_sha256':sha(HERE/'protocol.json'),'binary_sha256':manifest['binary_sha256'],'native_test_passed':1,'native_test_filtered':88,'marker_count':39,'fixture_count':3,'snapshot_count':6,'reach_array_snapshots':12,'checkpoint_count':23,'final_full_state_checks':3,'compact_file_count':15,'native_paired_reach_words_compared':total_words,'fixtures':fixture_results,'performance_measurement':False,'candidate_accepted':False,'deployment_changed':False,'extension_allowed':False,'scope':'Exact-positive-zero incidence at six fixed pre-evaluation snapshots of ordinary E020 training reach. Counts include each listed fold CTA with its selected opponent row and payout.','limitations':['No timing, dynamic all-iteration work share, kernel cost, speedup, complete-cycle headroom or fast-path correctness is established.','Raw reach float payloads are not retained: paired word equality, whole-array categories and reach fingerprints are native source-pinned assertions; compact row flags and fold incidence are independently decoded and recomputed here.','Row flag classes can overlap; individual category counts are not a partition of CTAs.','All-positive-zero incidence does not authorize skipping stores or imply positive-zero payout results; finite selected amount eligibility is reported separately.','Final full CPU q/scales are compared in native code and full fingerprints checked against immutable original/E020 anchors; raw full CPU payloads are not retained.']}

OUT.mkdir(exist_ok=False)
try:
    result=assess()
except BaseException as error:
    write('report.json',{'id':'D066','status':'invalid','diagnostic_only':True,'error':repr(error),'checks_passed':checks,'artifact_sha256':artifacts,'candidate_accepted':False,'performance_measurement':False,'deployment_changed':False,'extension_allowed':False})
    raise
result.update(created_at=datetime.now(timezone.utc).isoformat(),checks_passed=checks,artifact_sha256=artifacts)
write('report.json',result)
write('summary.md','# D066 fold positive-zero census\n\nAll 39 markers, 15 compact evidence files, 23 immutable convergence anchors and 3 complete final state records passed. Counts are incidence at six fixed snapshots only. No timing, optimization correctness or speed claim.\n')
write('assessor.py',Path(__file__).read_text(encoding='utf-8'))
write('manifest.json',{'id':'D066-fold-zero-census','files':{p.name:sha(p) for p in OUT.iterdir() if p.is_file()},'diagnostic_only':True,'candidate_accepted':False})
print(json.dumps({'status':result['status'],'snapshots':6,'report_sha256':sha(OUT/'report.json'),'performance_measurement':False}))
