"""Assess the one fixed CPU-only planned showdown mapping derivation; no timing measurement or acceptance."""
import collections, hashlib, json, math, re, struct, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
HERE=Path(__file__).resolve().parent
OUT=ROOT/'comparisons/D067-planned-show-incidence'
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
    keys=['show_ctas','all_positive_zero','any_negative_zero','any_finite_nonzero','any_nonfinite','finite_payouts','all_positive_zero_and_finite_payouts','empty_own_sorted','empty_opponent_sorted','all_positive_zero_and_empty_own','all_positive_zero_and_empty_opponent']
    result=dict.fromkeys(keys,0);result['show_ctas']=count
    for row in rows[start:start+count]:
        flag=flags[row[1+(1-p)]]
        finite_payouts=all((bits&0x7f800000)!=0x7f800000 for bits in row[4:7])
        empty_own=row[7+p]==0;empty_opponent=row[7+(1-p)]==0
        result['all_positive_zero']+=int(flag==0)
        result['any_negative_zero']+=int(bool(flag&1))
        result['any_finite_nonzero']+=int(bool(flag&2))
        result['any_nonfinite']+=int(bool(flag&4))
        result['finite_payouts']+=int(finite_payouts)
        result['all_positive_zero_and_finite_payouts']+=int(flag==0 and finite_payouts)
        result['empty_own_sorted']+=int(empty_own)
        result['empty_opponent_sorted']+=int(empty_opponent)
        result['all_positive_zero_and_empty_own']+=int(flag==0 and empty_own)
        result['all_positive_zero_and_empty_opponent']+=int(flag==0 and empty_opponent)
    return result


def assess():
    need(len(sys.argv)==2,'root authorization SHA argument')
    auth=read(HERE/'authorization.json',sys.argv[1])
    need(auth['candidate']=='D067' and all(auth[k] is True for k in ['E020_accepted','E020_server_qualification_pass','independent_source_review_pass','independent_script_review_pass']),'registered source/script prerequisites')
    seal=read(HERE/'scripts-manifest.json',auth['evidence_sha256'][str(HERE/'scripts-manifest.json')])
    need(seal['status']=='FROZEN_PROSPECTIVE_NOT_EXECUTED','prospective seal')
    for path,h in auth['evidence_sha256'].items():artifact(path,h)
    for path,h in seal['script_sha256'].items():artifact(HERE/path,h)
    for path,h in seal['reference_sha256'].items():artifact(path,h)
    protocol=read(HERE/'protocol.json','c7da2c45ab8c2b43861b316cb64b0745d530364f4c4a00c51db5fc274a40bc14')
    source=read(HERE/'source/source-manifest.json',protocol['source_archive_sha256'])
    schema=read(HERE/'source/output-schema.json',protocol['schema_sha256'])
    for name,h in source['artifact_sha256'].items():artifact(HERE/'source'/name,h)
    need(schema['prefix']==protocol['marker'] and schema['test_filter']==protocol['test_filter'] and schema['input_env']=='D067_CENSUS_DIR' and schema['output_env']=='D067_MAPPING_DIR','exact frozen helper interface')
    report=read(ROOT/'runs/D067R1/report.json')
    raw_path=ROOT/'runs/D067R1/stdout.log';artifact(raw_path,report['stdout_sha256'])
    raw=raw_path.read_text(encoding='utf-8')
    records=markers(raw,protocol['marker']);write('parsed-records.json',records)
    build_exit=read(ROOT/'runs/D067-build/exit.json')
    execution=read(ROOT/'runs/D067-execution/invocation.json')
    execution_exit=read(ROOT/'runs/D067-execution/exit.json')
    execution_complete=read(ROOT/'runs/D067-execution/complete.json')
    for name in ['stdout.log','stderr.log']:artifact(ROOT/'runs/D067-execution'/name)
    need(build_exit['returncode']==execution_exit['returncode']==report['returncode']==0,'build and native terminal success')
    need(execution_exit['error'] is None and execution_exit['cleanup'] is None,'no interrupted native process')
    need(report['id']=='D067R1' and report['kind']=='diagnostic' and report['fixture'] is None and report['status']=='measured' and report['test_pass_count']==1 and report['accepted'] is False,'exact one diagnostic and no acceptance')
    need(execution_complete['actual_run']=='D067R1' and execution_complete['native_test_pass'] and execution_complete['performance_acceptance'] is False,'fixed invocation terminal record')
    need(execution['actual_run']=='D067R1' and execution['logical_dashboard_row']=='D067' and execution['performance_acceptance'] is False,'fixed logical/run identity')
    need(execution['authorization_sha256']==sys.argv[1] and execution['protocol_sha256']==sha(HERE/'protocol.json') and execution['script_sha256']==sha(HERE/'run.py'),'execution sealed inputs')
    need(build_exit['at']<=execution['at']<=report['process_started_at']<=report['finished_at']<=execution_exit['at'],'build before run chronology')
    manifest_path=ROOT/'binaries/D067-solver.manifest.json'
    manifest=read(manifest_path,execution['build_manifest_sha256'])
    need(report['binary_build_manifest']['path']==str(manifest_path) and report['binary_build_manifest']['sha256']==sha(manifest_path) and report['binary_build_manifest']['data']==manifest,'runner embedded manifest identity')
    binary=ROOT/'binaries/D067-solver.exe'
    artifact(binary,manifest['binary_sha256'])
    need(manifest['binary_sha256']==execution['binary_sha256']==report['binary_sha256'],'binary build/run identity')
    need(manifest['candidate']=='D067' and manifest['test_only_append_verified'] and manifest['source_matches_prebuild'],'test-only source scope verified')
    need(manifest['primary_protocol_sha256']==sha(HERE/'protocol.json') and manifest['build_script_sha256']==sha(HERE/'build.py') and manifest['probe_authorization_sha256']==sys.argv[1] and manifest['probe_evidence_sha256']==auth['evidence_sha256'],'build sealed inputs')
    for key,hkey in [('build_log','build_log_sha256'),('build_stderr_log','build_stderr_sha256'),('patch','patch_sha256')]:artifact(manifest[key],manifest[hkey])
    need(manifest['patch_sha256']==sha(HERE/'source/candidate.patch'),'complete archived patch includes new helper')
    before=read(ROOT/'runs/D067-build/source-before.json')
    need(before['source_sha256']==manifest['source_sha256']==execution['source_sha256']==report['provenance']['source_sha256'] and len(before['source_sha256'])==163,'163 build/run source identities exact')
    for name,h in before['source_sha256'].items():artifact(REPO/name,h)
    for value in manifest['source_copies'].values():artifact(value['path'],value['sha256'])
    need(report['command']==[str(binary),protocol['test_filter'],'--nocapture','--test-threads=1','--ignored'],'exact ignored diagnostic invocation')
    need(re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',raw)==[('1','0','0','0','88')],'one executed test and88 filtered')
    need(not any(s in raw for s in ['panicked at','D067 invalid diagnostic']),'no native cleanup/panic error')
    need(not (ROOT/'runs/D067-execution/stderr.log').read_text(encoding='utf-8').strip(),'no orchestration stderr error')
    for key,value in [('RAYON_NUM_THREADS','16'),('POSTFLOP_AUTORESEARCH_PROFILE','0'),('POSTFLOP_AUTORESEARCH_STORAGE','compressed'),('POSTFLOP_AUTORESEARCH_FIXTURE',None)]:need(report['environment'][key]==value,'fixed env '+key)
    for snapshot in ['live_status_before','live_status_at_launch']:
        snap=report[snapshot];need(not snap['/api/status']['gpu'] and not snap['/api/preflop/status']['gpu'] and not snap['/api/reports/status']['running'],'live idle '+snapshot)

    for role,gate in protocol['prerequisite_reports'].items():
        pin=auth['prerequisites'][role]
        need(pin['path']==gate['path'] and auth['evidence_sha256'][pin['path']]==pin['sha256'],'canonical prerequisite '+role)
        value=read(pin['path'],pin['sha256'])
        for key,expected in gate['required_fields'].items():need(value[key]==expected,'prerequisite '+role+'/'+key)
    anchors=read(protocol['historical_anchors_path'])
    mapping_inputs=read(HERE/'source/inputs.json')
    need([(x['fixture_id'],x['fixture_index'],x['config']) for x in mapping_inputs]==[(a['fixture_id'],i,a['config']) for i,a in enumerate(anchors)],'native embedded3 configs equal historical anchors')
    historical_report=read(ROOT/'runs/D066R1/report.json')
    old_raw_path=Path(protocol['historical_raw_path'])
    artifact(old_raw_path,historical_report['stdout_sha256'])
    old_records=markers(old_raw_path.read_text(encoding='utf-8'),'D066_FOLD_ZERO_CENSUS ')
    need(historical_report['id']=='D066R1' and historical_report['returncode']==0 and len(old_records)==39,'bound historical D066 terminal evidence, not rerun')
    geometry={x['fixture_id']:x for x in old_records if x['stage']=='geometry'}
    snapshots={(x['fixture_id'],x['iteration']):x for x in old_records if x['stage']=='snapshot'}
    need(list(geometry)==protocol['expected_fixtures'] and len(snapshots)==6,'historical3 fixtures6 snapshots')
    catalog=read(protocol['historical_catalog_path'])
    historical_dir=Path(protocol['historical_census_directory'])
    need(catalog['census_directory']==str(historical_dir) and catalog['raw_float_payload_retained'] is False,'historical compact file scope')
    historical_names={f'{f}-fold-mapping.u32le' for f in protocol['expected_fixtures']}
    historical_names|={f'{f}-iteration{i}-reach{q}.rowflags' for f in protocol['expected_fixtures'] for i in protocol['snapshot_iterations'][f] for q in [0,1]}
    need(set(catalog['files'])==historical_names and len(historical_names)==15,'exact historical15 file inventory')
    for name,pin in catalog['files'].items():
        path=historical_dir/name
        need(path.is_file() and not path.is_symlink(),'historical regular file '+name)
        artifact(path,pin['sha256']);need(path.stat().st_size==pin['bytes'],'historical byte size '+name)
    expected_order=[('admission',None)]+[('fixture_mapping',f) for f in protocol['expected_fixtures']]+[('complete',None)]
    need([r[0]+(':'+r[1] if r[1] else '') for r in expected_order]==schema['marker_order'] and expected_order==[(r['stage'],r.get('fixture_id')) for r in protocol['expected_stage_order']],'frozen5-record order')
    need(len(records)==5 and [(r['stage'],r.get('fixture_id')) for r in records]==expected_order,'complete5-record mapping invocation')
    need(not markers(raw,'AUTORESEARCH_RESULT ') and not markers(raw,'D066_FOLD_ZERO_CENSUS '),'no benchmark or repeated census records')
    admission=records[0]
    need(set(admission)=={'stage','fixtures','available_host_ram_bytes','required_available_host_ram_bytes','cpu_only','gpu_calls'} and admission['fixtures']==3 and admission['cpu_only'] is True and admission['gpu_calls']==0,'exact CPU-only admission declaration')
    need(whole(admission['available_host_ram_bytes']) and admission['available_host_ram_bytes']>=admission['required_available_host_ram_bytes']==16*1024**3,'host RAM admission')
    complete=records[-1]
    need(complete=={'stage':'complete','fixtures':3,'fold_mapping_exact':True,'fold_mapping_checks':3,'planned_show_mapping_files':3,'cpu_only':True,'gpu_calls':0,'planned_source_only':True,'new_show_upload_validation':False,'performance_measurement':False,'candidate_accepted':False},'exact all3 checks completed CPU-only marker')
    planned={x['fixture_id']:x for x in records if x['stage']=='fixture_mapping'}
    for index,a in enumerate(anchors):
        f=a['fixture_id'];g=planned[f];old=geometry[f]
        need(mapping_inputs[index]['geometry']==old,'native input geometry equals raw historical record '+f)
        need(set(g)==set(schema['fixture_mapping_fields'])|{'stage'} and g['fixture_index']==index,'exact fixture schema/index '+f)
        need(g['planned_source_only'] is True and g['new_show_upload_validation'] is False and g['cleanup_complete'] is True,'source-derived metadata and CPU cleanup scope '+f)
        need(g['fold_ctas_per_traverser']==old['fold_ctas_per_traverser'] and g['fold_mapping']==old['mapping'],'retained fold count and complete metadata '+f)
        need(g['fold_mapping_exact'] is True,'native complete fold bytes matched '+f)
        need(g['nodes']==old['nodes']==a['nodes'] and g['nh']==old['nh']==a['nh'] and g['reach_blocks']==old['reach_blocks'],'exact historical geometry '+f)
        need(g['num_levels']==len(old['fold_spans']) and g['fold_spans']==old['fold_spans'],'exact historical fold spans '+f)
    # No row-flag joins occur before the complete marker and all3 checks above.
    mapping_dir=Path(protocol['mapping_directory'])
    need(execution['mapping_directory']==str(mapping_dir),'fresh mapping directory')
    expected_env={'D067_MAPPING_DIR':str(mapping_dir),'D067_CENSUS_DIR':str(historical_dir),'POSTFLOP_AUTORESEARCH_FIXTURE':None,'POSTFLOP_AUTORESEARCH_LIFECYCLE_PROFILE':None,'POSTFLOP_AUTORESEARCH_PROFILE':'0','POSTFLOP_AUTORESEARCH_STORAGE':'compressed','RAYON_NUM_THREADS':'16'}
    need(execution['run_env']==expected_env,'recorded exact runtime environment')
    maps=read(ROOT/'runs/D067-execution/mapping-artifacts.json',execution_complete['mapping_artifacts_sha256'])
    expected_files={f'{f}-planned-show-mapping.u32le' for f in protocol['expected_fixtures']}
    need(schema['mapping']['name']=='<fixture>-planned-show-mapping.u32le' and expected_files==set(protocol['expected_files']),'frozen3 output file inventory')
    need(maps['mapping_directory']==str(mapping_dir) and maps['cpu_only_mapping'] is True and maps['raw_float_payload_retained'] is False,'planned mapping catalog scope')
    need(set(maps['files'])=={p.name for p in mapping_dir.iterdir()}==expected_files,'all3 mappings without extras')
    for name,pin in maps['files'].items():
        path=mapping_dir/name
        need(path.is_file() and not path.is_symlink() and path.resolve().parent==mapping_dir.resolve(),'owned regular mapping '+name)
        artifact(path,pin['sha256']);need(path.stat().st_size==pin['bytes'],'mapping size '+name)
    for name,pin in protocol['preexisting_target_artifacts'].items():
        artifact(REPO/name,pin['sha256']);need((REPO/name).stat().st_size==pin['bytes'],'preserved PTX size '+name)
    fixture_results=[]
    for a in anchors:
        f=a['fixture_id'];g=planned[f];old=geometry[f]
        need(all(whole(v) and v>0 for v in g['nh']+g['reach_blocks']) and whole(g['num_slots']) and g['num_slots']>0,'positive physical/planned geometry '+f)
        spans=g['show_spans'];cursor=0
        need(len(spans)==g['num_levels'],'one show span per level '+f)
        for level,span in enumerate(spans):
            need(span['level']==level and span['start']==cursor and whole(span['count']),'contiguous show span '+f+'/'+str(level))
            cursor+=span['count']
        need(cursor==g['show_ctas_per_traverser'],'complete show coverage '+f)
        m=g['mapping'];mname=f'{f}-planned-show-mapping.u32le';data=(mapping_dir/mname).read_bytes()
        need(m['file']==mname and len(data)==m['bytes']==36*cursor and fnv(data)==m['fnv1a64'],'mapping complete byte/hash '+f)
        need(m['record']=='nine little-endian u32: '+','.join(schema['mapping']['record']),'exact9-u32 show codec '+f)
        rows=list(struct.iter_unpack('<9I',data))
        need(len({row[0] for row in rows})==cursor,'unique planned terminal node IDs '+f)
        need(all(n<g['nodes'] and s0<g['reach_blocks'][0] and s1<g['reach_blocks'][1] and slot<g['num_slots'] and m0<=g['nh'][0] and m1<=g['nh'][1] for n,s0,s1,slot,_,_,_,m0,m1 in rows),'all planned node/row/river/hand bounds '+f)
        slot_counts={}
        for row in rows:
            pair=(row[7],row[8]);slot=row[3]
            if slot in slot_counts and slot_counts[slot]!=pair:raise AssertionError('inconsistent planned river counts '+f+'/'+str(slot))
            slot_counts[slot]=pair
        need(all(slot<g['num_slots'] for slot in slot_counts),'per-slot logical counts consistent '+f)
        for sp in spans:
            ns=[r[0] for r in rows[sp['start']:sp['start']+sp['count']]]
            need(ns==sorted(ns),'ascending node order perlevel '+f+'/'+str(sp['level']))
        output=[]
        for iteration in protocol['snapshot_iterations'][f]:
            snap=snapshots[(f,iteration)]
            need(snap['before_exploitability'] is True and snap['paired_reach_bits_exact'] is True and snap['raw_float_payload_retained'] is False,'historical pre-eval source scope '+f+'/'+str(iteration))
            need([(v['opponent'],v['traverser']) for v in snap['arrays']]==[(0,1),(1,0)],'both historical opponent arrays')
            arrays=[]
            for arr in snap['arrays']:
                q=arr['opponent'];p=1-q;nh=g['nh'][q];nr=g['reach_blocks'][q]
                need(arr['logical_nh']==nh and arr['physical_rows']==nr and arr['entries']==nh*nr,'historical array dimensions')
                fn=f'{f}-iteration{iteration}-reach{q}.rowflags';flags=(historical_dir/fn).read_bytes();rc=arr['rowclass']
                need(rc['file']==fn and rc['bytes']==len(flags)==nr and rc['fnv1a64']==fnv(flags) and all(v<=7 for v in flags),'historical exact row flags '+fn)
                rowclasses=collections.Counter(flags);wc=arr['whole_reach_word_categories']
                need(set(wc)=={'positive_zero','negative_zero','finite_nonzero','nonfinite'} and all(whole(v) for v in wc.values()) and sum(wc.values())==nh*nr,'historical whole-array category bounds')
                for bit,name in [(1,'negative_zero'),(2,'finite_nonzero'),(4,'nonfinite')]:
                    count=sum(n for flag,n in rowclasses.items() if flag&bit)
                    need(count<=wc[name]<=count*nh,'historical row/word bounds '+name)
                counts=tally(rows,flags,p,0,cursor)
                levels=[{**sp,'counts':tally(rows,flags,p,sp['start'],sp['count'])} for sp in spans]
                need(all(sum(level['counts'][k] for level in levels)==v for k,v in counts.items()),'all-level sums equal complete show counts')
                arrays.append({'opponent':q,'traverser':p,'historical_rowflag_file':fn,'physical_rows':nr,'planned_show_counts':counts,'levels':levels,'all_positive_zero_fraction':counts['all_positive_zero']/cursor if cursor else None,'finite_payout_eligible_fraction':counts['all_positive_zero_and_finite_payouts']/cursor if cursor else None})
            output.append({'historical_iteration':iteration,'arrays':arrays})
        fixture_results.append({'fixture_id':f,'nodes':g['nodes'],'nh':g['nh'],'reach_blocks':g['reach_blocks'],'num_slots':g['num_slots'],'show_ctas_per_traverser':cursor,'show_spans':spans,'historical_snapshots':output})
    return {'id':'D067','actual_run':'D067R1','status':'pass','diagnostic_only':True,'mapping_validation_pass':True,'historical_flag_join_pass':True,'protocol_sha256':sha(HERE/'protocol.json'),'binary_sha256':manifest['binary_sha256'],'native_test_passed':1,'native_test_filtered':88,'marker_count':5,'fixture_count':3,'new_mapping_files':3,'complete_fold_maps_matched':3,'historical_snapshot_count':6,'historical_rowflag_files':12,'new_gpu_snapshots':0,'new_checkpoints':0,'new_full_state_tests':0,'fixtures':fixture_results,'performance_measurement':False,'candidate_accepted':False,'deployment_changed':False,'extension_allowed':False,'scope':'CPU reconstructed planned-showdown CTA incidence at six historical D066 pre-evaluation training boundaries; no new reach measurements.','limitations':['All three old fold mappings are byte-matched by the source-pinned native test before these historical joins. New show/river-slot/tie metadata have deterministic source/constructor provenance, not newly downloaded GPU evidence.','Whole-row exact+0 is a conservative sufficient input predicate. Flags cannot expose the river-filtered subset or reconstruct raw floats.','Raw reach equality,23 convergence checkpoints and3 final full-state controls belong to closed D066 and were not rerun.','Independent row flag categories can overlap; count each planned CTA per traverser, never deduplicate owner rows.','Counts do not prove shortcut correctness, all-iteration frequency, kernel latency, savings or complete-cycle headroom.']}

OUT.mkdir(exist_ok=False)
try:
    result=assess()
except BaseException as error:
    write('report.json',{'id':'D067','status':'invalid','diagnostic_only':True,'error':repr(error),'checks_passed':checks,'artifact_sha256':artifacts,'candidate_accepted':False,'performance_measurement':False,'deployment_changed':False,'extension_allowed':False})
    raise
result.update(created_at=datetime.now(timezone.utc).isoformat(),checks_passed=checks,artifact_sha256=artifacts)
write('report.json',result)
write('summary.md','# D067 planned-showdown incidence\n\nAll three reconstructed fold mappings and geometry matched historical D066 before joining twelve retained row-flag files to three new planned-show maps. Five native records passed. This is planned incidence at six historical boundaries; no GPU census, numerical shortcut validation, timing or acceptance.\n')
write('assessor.py',Path(__file__).read_text(encoding='utf-8'))
write('manifest.json',{'id':'D067-planned-show-incidence','files':{p.name:sha(p) for p in OUT.iterdir() if p.is_file()},'diagnostic_only':True,'candidate_accepted':False})
print(json.dumps({'status':result['status'],'historical_snapshots':6,'report_sha256':sha(OUT/'report.json'),'performance_measurement':False}))
