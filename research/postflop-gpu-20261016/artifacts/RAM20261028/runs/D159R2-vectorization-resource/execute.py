import sys,json,re,hashlib,shutil
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'))
import common as h
assert len(sys.argv)==2;P=h.read(H/'protocol.json')
def verify():
    h.pin(H/'protocol.json',sys.argv[1]);h.custody()
    for p,d in P['input_sha256'].items():h.pin(p,d)
def entries(path):
    t=path.read_text(encoding='utf-8');out={};i=0
    while True:
        i=t.find('.visible .entry ',i)
        if i<0:break
        n=t.index('(',i);name=t[i+len('.visible .entry '):n].strip();start=t.index('{',n);j=start+1;depth=1
        while depth:
            depth+=int(t[j]=='{')-int(t[j]=='}');j+=1
        assert name not in out;out[name]=t[i:j];i=j
    return out
def normalize(t):
    t=re.sub(r'\$L__BB\d+_(\d+)',r'$L__BB_FUNCTION_\1',t);t=re.sub(r'__local_depot\d+','__local_depot_FUNCTION',t);return re.sub(r'\$L__func_(begin|end)\d+',r'$L__func_\1_FUNCTION',t)
def vectors(t):
    ops=[]
    for line in t.splitlines():
        code=line.strip().split('//',1)[0].strip()
        if not code:continue
        op=code.split()[1] if code.startswith('@') and len(code.split())>1 else code.split()[0]
        if re.search(r'^(?:ld|st)\..*\.v(?:2|4)\.',op) or '.f32x2' in op:ops.append(op)
    return ops
verify();O=H/'execution';O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
    h.child(P['rustc_command'],O,'rustc',600);verify()
    h.save(O/'binary.json',{'at':h.now(),'sha256':h.sha(H/'probe.exe')})
    h.child([str(H/'probe.exe'),str(O)],O,'probe',600);verify()
lines=(O/'probe.stdout.log').read_text(encoding='utf-8').splitlines();markers=[json.loads(x.split('D159_RESOURCE ',1)[1]) for x in lines if x.startswith('D159_RESOURCE ')]
assert len(markers)==19 and markers[-1]['stage']=='complete' and markers[-1]['kernel_launches']==0 and markers[-1]['compilations']==3 and markers[-1]['retained_PTX_inputs']==1
rows={(x['variant'],x['kernel']):x for x in markers[:-1]};assert len(rows)==18
tables={(v,a):entries(O/f'{v}-{a}.ptx') for v in ['baseline','candidate'] for a in ['compute_120','compute_75']}
gates={};diffs={}
for arch in ['compute_120','compute_75']:
    b,c=tables['baseline',arch],tables['candidate',arch]
    gates[arch+':nine_entry_inventory']=set(b)==set(c)==set(P['expected_entries'])
    for name in b:gates[arch+':'+name+':ABI_exact']=b[name].split('{',1)[0]==c[name].split('{',1)[0]
gates['compute75_original_fallback_PTX_exact']=(O/'baseline-compute_75.ptx').read_bytes()==(O/'candidate-compute_75.ptx').read_bytes()
b,c=tables['baseline','compute_120'],tables['candidate','compute_120'];changed=[];bv=cv=0
for name in P['expected_entries']:
    same=normalize(b[name])==normalize(c[name]);bl,cl=vectors(b[name]),vectors(c[name]);bv+=len(bl);cv+=len(cl)
    if not same:changed.append(name)
    diffs[name]={'normalized_body_exact':same,'baseline_vector_sites':bl,'candidate_vector_sites':cl,'baseline_entry_sha256':hashlib.sha256(b[name].encode()).hexdigest(),'candidate_entry_sha256':hashlib.sha256(c[name].encode()).hexdigest()}
    br,cr=rows['baseline',name],rows['candidate',name]
    gates[name+':local_not_increased']=cr['local_bytes_per_thread']<=br['local_bytes_per_thread']
    gates[name+':max_threads_not_reduced']=cr['max_threads']>=br['max_threads']>=128
    gates[name+':stack_not_increased']=cr['context_stack_after']<=br['context_stack_after']
    gates[name+':matching_control_shapes']=[(x['threads'],x['dynamic_shared_bytes']) for x in br['controls']]==[(x['threads'],x['dynamic_shared_bytes']) for x in cr['controls']]
    gates[name+':all_original_legal_controls_feasible']=all((not old['supported_by_original_source_limit']) or (new['supported_by_original_source_limit'] and new['fits_default_limits'] and new['occupancy'] is not None and new['occupancy']>0) for old,new in zip(br['controls'],cr['controls']))
gates['intended_changed_body']=bool(changed);gates['intended_vector_instruction_increase']=cv>bv
old=h.read(H/'repair-review.json')['original_baseline_resource_rows']
for row in old:
    now=rows['baseline',row['kernel']]
    gates['retained_baseline:'+row['kernel']+':resource_requery_exact']=row==now
gates['retained_baseline:PTX_exact']=(O/'baseline-compute_120.ptx').read_bytes()==(H/'retained-baseline-compute_120.ptx').read_bytes()
passed=all(gates.values());D=ROOT/'comparisons/D159R2-vectorization-resource';D.mkdir(exist_ok=False)
report={'id':'D159R2','at':h.now(),'original_D159_probe_remains_failed_baseline_setup':True,'retained_baseline_PTX_reused':True,'total_main_compilations_across_R1_R2':4,'status':'admit_exact_numerical_controls_only' if passed else 'declined_compiler_mechanism_or_resources','protocol_sha256':sys.argv[1],'gates':gates,'failed_gates':[k for k,v in gates.items() if not v],'changed_compute120_entries':changed,'vector_instruction_sites':{'baseline':bv,'candidate':cv},'per_entry_codegen':diffs,'raw_resource_rows':markers,'PTX_sha256':{v+'-'+a:h.sha(O/f'{v}-{a}.ptx') for v in ['baseline','candidate'] for a in ['compute_120','compute_75']},'explicit_kernel_launches':0,'solver_executions':0,'performance_samples':0,'new_E093_or_production_source_created':False,'all_children_terminal':True,'source_main_live_PTX_custody_pass':True,'candidate_accepted':False,'scope':'One target-specific compiler option on accepted source. Normalized PTX mechanism/ABI,exact unmodified75fallback and actual target compiled resource feasibility only. Static instruction sites are not runtime utilization,time or exact numerical behavior. Resource/ABI/body/mechanism failure closes this fixed option form without alternatives;an admission requires all unchanged exact numerical/broad/material/performance qualification.'}
h.save(D/'report.json',report);h.save(O/'complete.json',{'at':h.now(),'report_sha256':h.sha(D/'report.json'),'all_owned_children_terminal':True,'kernel_launches':0});verify()
print(json.dumps({k:report[k] for k in ['status','failed_gates','changed_compute120_entries','vector_instruction_sites']}),flush=True)
