import sys,json,re,shutil,hashlib,urllib.request,collections
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'))
import common as h
assert len(sys.argv)==2;P=h.read(H/'protocol.json')
def verify():
    h.pin(H/'protocol.json',sys.argv[1]);h.custody()
    for path,digest in P['input_sha256'].items():h.pin(path,digest)
def entries(path):
    text=path.read_text(encoding='utf-8');result={};i=0
    while True:
        i=text.find('.visible .entry ',i)
        if i<0:return result
        n=text.index('(',i);name=text[i+len('.visible .entry '):n].strip();b=text.index('{',n);j=b+1;depth=1
        while depth:depth+=int(text[j]=='{')-int(text[j]=='}');j+=1
        assert name not in result;result[name]=text[i:j];i=j
def normalized_instructions(body):
    body=body.split('{',1)[1];body=re.sub(r'//[^\n]*','',body)
    body=re.sub(r'\$L__BB\d+_(\d+)',r'$L__BB_FUNCTION_\1',body)
    body=re.sub(r'__local_depot\d+','__local_depot_FUNCTION',body)
    body=re.sub(r'\$L__func_(begin|end)\d+',r'$L__func_\1_FUNCTION',body)
    lines=[x.strip() for x in body.splitlines() if x.strip() and not x.strip().startswith(('.reg ','.local ','.shared '))]
    return re.sub(r'\s+',' ', '\n'.join(lines)).strip()
def opcodes(body):
    result=collections.Counter()
    for line in body.split('{',1)[1].splitlines():
        line=line.split('//',1)[0].strip()
        if not line or line[0] in '.{}' or line.endswith(':'):continue
        words=line.split();op=words[1] if words[0].startswith('@') and len(words)>1 else words[0]
        if re.match(r'^[a-z][a-z0-9_.]*$',op):result[op]+=1
    return dict(sorted(result.items()))
def publish(folder,names):
    for name in names:
        path=folder/name;key=folder.name+'/'+name;dest=h.ar.DASHBOARD/'evidence'/key;dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists():assert dest.read_bytes()==path.read_bytes()
        else:shutil.copyfile(path,dest)
        with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==path.read_bytes()
verify();O=H/'execution';O.mkdir(exist_ok=False)
publish(H,['protocol.json','repair-review.json','compile.py','resource.rs'])
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);item=next(x for x in status['experiments'] if x['id']=='D162')
    item.update(status='running',stage='Frozen original compiler control,then private CUDA13 codegen/resources',reason='Reused exact original12.9control;one13compile with explicit absolute builtins binding. Original failed D161 remains invalid. Same accepted source and default math. Then driver resource queries only;no application kernels,solver or performance samples.')
    item.setdefault('evidence',[]).append({'label':'Frozen compiler and resource protocol','url':'evidence/D162-private-dependency-repair/protocol.json'})
    status.update(updated_at=h.now(),active_experiment='D162',stage='CUDA13 compiler code and resource controls',activity='Verifying literal old compiler call first,then one private13target compile and no-kernel resource query. E080 current-RAM baseline10.4564s unchanged.')
    h.ar.atomic_json(h.ar.STATUS,status)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
    shutil.copyfile(H/'retained-baseline.ptx',O/'baseline.ptx');shutil.copyfile(H/'retained-baseline.compile.json',O/'baseline.compile.json')
    compile_records={'baseline':h.read(O/'baseline.compile.json')}
    for arm in ['candidate']:
        verify();command=[sys.executable,str(H/'compile.py'),P[arm+'_DLL'],str(H/'kernels.cu'),str(O/(arm+'.ptx')),json.dumps(P[arm+'_version'])]
        h.child(command,O,'compile-'+arm,600);verify();record=h.read(O/(arm+'.compile.json'));compile_records[arm]=record
        assert record['options']==P['expected_options'] and record['source_sha256']==h.sha(H/'kernels.cu') and record['GPU_context_or_kernel_calls']==0 and record['program_name'] is None and record['headers']==0
        if arm=='baseline':assert (O/'baseline.ptx').read_bytes()==(H/'reference-baseline.ptx').read_bytes(),'baseline adapter must match accepted before candidate'
    h.child(P['rustc_command'],O,'rustc-resource',600);verify()
    h.save(O/'resource-binary.json',{'sha256':h.sha(H/'resource.exe')})
    h.child([str(H/'resource.exe'),str(O)],O,'resource',600);verify()
lines=(O/'resource.stdout.log').read_text(encoding='utf-8').splitlines();markers=[json.loads(x.split('D161_RESOURCE ',1)[1]) for x in lines if x.startswith('D161_RESOURCE ')]
assert len(markers)==19 and markers[-1]['stage']=='complete' and markers[-1]['kernel_launches']==markers[-1]['NVRTC_compilations']==0
resources={(x['variant'],x['kernel']):x for x in markers[:-1]};assert len(resources)==18
tables={arm:entries(O/(arm+'.ptx')) for arm in ['baseline','candidate']};gates={};changes=[];details={};resource_changes={}
gates['nine_entry_inventory']=set(tables['baseline'])==set(tables['candidate'])==set(P['expected_entries'])
gates['baseline_whole_PTX_exact']=(O/'baseline.ptx').read_bytes()==(H/'reference-baseline.ptx').read_bytes()
gates['original_compute75_retained_exact']=h.sha(H/'retained-original-compute75.ptx')==P['fallback_PTX_sha256']
for name in P['expected_entries']:
    b=tables['baseline'][name];c=tables['candidate'][name]
    gates[name+':ABI_exact']=b.split('{',1)[0]==c.split('{',1)[0]
    bi=normalized_instructions(b);ci=normalized_instructions(c);changed=bi!=ci
    if changed:changes.append(name)
    details[name]={'changed_normalized_instructions':changed,'baseline_entry_sha256':hashlib.sha256(b.encode()).hexdigest(),'candidate_entry_sha256':hashlib.sha256(c.encode()).hexdigest(),'baseline_opcode_sites':opcodes(b),'candidate_opcode_sites':opcodes(c),'scope':'Static emitted instruction sites,not runtime counts,speed or exact mathematical equivalence.'}
    br=resources['baseline',name];cr=resources['candidate',name]
    gates[name+':local_not_increased']=cr['local_bytes_per_thread']<=br['local_bytes_per_thread']
    gates[name+':max_threads_not_reduced']=cr['max_threads']>=br['max_threads']>=128
    gates[name+':default_context_limits_exact']=all(cr[k]==br[k] for k in ['context_stack_before','context_stack_after','context_heap_before','context_heap_after']) and cr['context_stack_before']==cr['context_stack_after'] and cr['context_heap_before']==cr['context_heap_after']
    gates[name+':control_shapes_exact']=[(x['threads'],x['dynamic_shared_bytes']) for x in br['controls']]==[(x['threads'],x['dynamic_shared_bytes']) for x in cr['controls']]
    gates[name+':original_legal_controls_feasible']=all(not old['supported_by_original_source_limit'] or (new['supported_by_original_source_limit'] and new['fits_default_limits'] and new['occupancy'] is not None and new['occupancy']>0) for old,new in zip(br['controls'],cr['controls']))
    resource_changes[name]={key:{'baseline':br[key],'candidate':cr[key]} for key in ['registers','local_bytes_per_thread','static_shared_bytes','max_threads'] if br[key]!=cr[key]}
gates['real_instruction_body_change']=bool(changes)
passed=all(gates.values());D=ROOT/'comparisons/D162-private-dependency-repair';D.mkdir(exist_ok=False)
report={'id':'D162','at':h.now(),'original_D161_invalid_preserved':True,'baseline_compiler_output_reused_without_repeat':True,'candidate_builtin_absolute_binding_verified':True,'status':'admit_exact_raw_numerical_controls_only' if passed else 'declined_compiler_mechanism_or_resources','protocol_sha256':sys.argv[1],'gates':gates,'failed_gates':[k for k,v in gates.items() if not v],'changed_entries':changes,'resource_changes':resource_changes,'entry_code':details,'actual_compile_records':compile_records,'actual_resource_rows':markers[:-1],'original_target75_PTX_retained':True,'fallback_production_implementation_proven':False,'all_children_terminal':True,'source_main_live_PTX_custody_pass':True,'application_kernel_launches':0,'solver_executions':0,'performance_samples':0,'new_E093_or_production_source':False,'candidate_accepted':False,'scope':'Same accepted source/default flags,target-only new compiler. Literal baseline adapter matches retained accepted PTX from original successful control;no baseline compiler repeated. Original D161 failed private DLL setup is retained and not regraded. Compiler/codegen/ABI and read-only driver resource feasibility only. Static changes/warnings do not establish raw numerical identity,critical path or speed. Original failed extraction setup retained. No blanket toolchain upgrade or global/preflop effect. Passing admits only unchanged numerical/engine/resource qualification steps;failure closes exact form without source/flags/version/shape/sample rescue.'}
h.save(D/'report.json',report);verify();h.save(O/'complete.json',{'at':h.now(),'report_sha256':h.sha(D/'report.json'),'all_owned_children_terminal':True,'new_gain_accepted':False})
publish(D,['report.json'])
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);item=next(x for x in status['experiments'] if x['id']=='D162')
    item.update(status='measured',correctness='raw_numerical_not_started',stage='Admitted to exact raw numerical controls only' if passed else 'Declined compiler mechanism/resource prerequisite',reason='Original12.9control PTX byte-exact.13.0changed entries: '+','.join(changes)+'. Failed gates: '+(','.join(report['failed_gates']) or 'none')+'. No application kernels,solver or speed score;broader/material/qualification remain.')
    item.setdefault('evidence',[]).append({'label':'Actual compiler and resource outcome','url':'evidence/D162-private-dependency-repair/report.json'})
    status.update(updated_at=h.now(),active_experiment='D162',stage='CUDA13 compiler prerequisite measured',activity=('New compiler changes GPU code and passes hard ABI/resource prerequisites;next full raw exactness controls.' if passed else 'Compiler mechanism/resource gate declined;no numerical or speed samples.')+' E080 current-RAM10.4564s unchanged.')
    h.ar.atomic_json(h.ar.STATUS,status)
verify();print(json.dumps({k:report[k] for k in ['status','failed_gates','changed_entries','resource_changes']}),flush=True)
