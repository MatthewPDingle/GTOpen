"""Correct only omitted cvta pointer propagation in E073's read-only audit."""
from pathlib import Path
import ast,hashlib,json,re,shutil,struct,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();H=R/'runs/D119-boundary-load-audit';assert not H.exists();H.mkdir()
E=R/'runs/E073-resource';P=old.read(E/'protocol.json');q=old.read(E/'report.json');original=R/'runs/E073-resource-execute.py'
for p,h in P['input_sha256'].items():old.pin(p,h)
expected=[a+':'+n for a in ['compute_120','compute_75']for n in ['baseline_two_boundary_parameters_loaded32','candidate_two_boundary_parameters_loaded16']]
assert q['status']=='rejected_compiled_prerequisite'and[k for k,v in q['gates'].items()if not v]==expected
assert q['all_owned_children_terminal']and q['application_kernel_launches']==q['solver_executions']==q['performance_measurements']==0
# Extract only the two pure decoder functions. No original main/probe executes.
tree=ast.parse(original.read_text(encoding='utf-8'));definitions=[x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name in ['entries','boundary_loads']];assert len(definitions)==2
ns={'re':re};exec(compile(ast.Module(body=definitions,type_ignores=[]),str(original),'exec'),ns);previous=ns['boundary_loads'];source=ast.get_source_segment(original.read_text(encoding='utf-8'),definitions[1]);before='(?:add|sub|mul|mad|shl|shr|mov|cvt)';after='(?:add|sub|mul|mad|shl|shr|mov|cvt|cvta)';assert source.count(before)==1;fixed=source.replace(before,after,1)
assert fixed.replace(after,before,1)==source;ns2={'re':re};exec(compile(fixed,str(H/'corrected-pointer-decoder.py'),'exec'),ns2);decode=ns2['boundary_loads'];(H/'corrected-pointer-decoder.py').write_text('import re\n'+fixed+'\n',encoding='utf-8',newline='\n')
fixtures={
 'direct':('ld.param.u64 %rd1, [up_show_param_12];\nld.global.nc.u32 %r1, [%rd1];',[([12],32)]),
 'cvta':('ld.param.u64 %rd1, [up_show_param_12];\ncvta.to.global.u64 %rd2, %rd1;\nld.global.nc.u16 %rs1, [%rd2];',[([12],16)]),
 'wide-address':('ld.param.u64 %rd1, [up_show_param_13];\ncvta.to.global.u64 %rd2, %rd1;\nmad.wide.u32 %rd3, %r2, 2, %rd2;\nld.global.nc.u16 %rs1, [%rd3];',[([13],16)]),
 'unrelated-pointer':('ld.param.u64 %rd1, [up_show_param_11];\ncvta.to.global.u64 %rd2, %rd1;\nld.global.nc.u16 %rs1, [%rd2];',[]),
 'loaded-value-is-not-pointer':('ld.param.u64 %rd1, [up_show_param_12];\ncvta.to.global.u64 %rd2, %rd1;\nld.global.nc.u32 %r1, [%rd2];\ncvta.to.global.u64 %rd3, %r1;\nld.global.nc.u16 %rs1, [%rd3];',[([12],32)])}
unit=[]
for name,(text,want)in fixtures.items():
 actual=[(x['parameters'],x['bits'])for x in decode(text)];assert actual==want,(name,actual,want);unit.append({'fixture':name,'expected':want,'actual':actual})
assert previous(fixtures['cvta'][0])==[]and decode(fixtures['cvta'][0])!=[]
pins=[Path(__file__),original,E/'protocol.json',E/'report.json',H/'corrected-pointer-decoder.py',R/'runs/E073-source/manifest.json',R/'runs/E073-source/source-review.json',R/'runs/D118-river-boundaries/report.json',*[E/'execution'/f'{v}-{a}.ptx'for v in ['baseline','candidate']for a in ['compute_120','compute_75']]]
old.save(H/'protocol.json',{'id':'D119','at':old.now(),'input_sha256':{str(p):old.sha(p)for p in pins},'scope':'Read-only decoder correction and re-evaluation of the same4sealed PTXfiles. No source/compiler/resource/GPU/kernel/numerical/timing rerun.','change':'Only propagate address origin through cvta.to.global.u64 as through existing mov/cvt/arithmetic. Same original32to16load criterion, not a criterion amendment.','parser_fixtures':unit,'original_failure_immutable':True,'candidate_accepted':False})
gates=dict(q['gates']);proof={}
for arch in ['compute_120','compute_75']:
 proof[arch]={}
 for variant,bits in [('baseline',32),('candidate',16)]:
  p=E/'execution'/f'{variant}-{arch}.ptx';old.pin(p,q['ptx_sha256'][variant+'-'+arch]);t=ns['entries'](p)['up_show'];original_result=previous(t);result=decode(t);assert original_result==[]
  assert len(result)==2 and sorted(x['parameters']for x in result)==[[12],[13]]and all(x['bits']==bits for x in result),(arch,variant,result)
  key=arch+':'+('baseline_two_boundary_parameters_loaded32'if variant=='baseline'else'candidate_two_boundary_parameters_loaded16');gates[key]=True
  proof[arch][variant]={'old_decoder_results':original_result,'corrected_decoder_results':result,'ptx_sha256':old.sha(p),'exact_cvta_chain_lines':[x.strip()for x in t.splitlines()if re.search(r'cvta\.to\.global\.u64\s+%\w+,\s*%rd(?:36|37|\d+);',x)]}
assert all(gates.values());old.custody()
report={'id':'D119','at':old.now(),'status':'pass_corrected_same_narrow_load_prerequisite','original_resource_status':q['status'],'original_resource_report_sha256':old.sha(E/'report.json'),'original_protocol_sha256':old.sha(E/'protocol.json'),'original_failure_preserved':True,'parser_correction_only':True,'criterion_unchanged':True,'gates':gates,'pointer_load_proof':proof,'parser_fixtures':unit,'resource_rows_unchanged':q['rows'],'resource_warnings':q['resource_warnings'],'all_owned_children_terminal':True,'source_main_live_PTX_unchanged':True,'new_compilers':0,'new_resource_probes':0,'application_kernel_launches':0,'solver_executions':0,'numerical_or_performance_samples':0,'source_changed':False,'candidate_accepted':False,'limits':'Linear PTX address-origin decoding and original resource feasibility only; not full control-flow/SASS/cache traffic, numerical equivalence or speed. Same original pointer-width requirement now correctly traced through emitted cvta. All raw numerical/complete-solve/broad/material/capacity/holdout/cumulative gates unchanged.'};old.save(H/'report.json',report)
def publish(src,key):
 dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==src.read_bytes()
 else:shutil.copyfile(src,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==src.read_bytes()
 return {'url':'evidence/'+key,'sha256':old.sha(src)}
pub=[publish(p,H.name+'/'+p.name)for p in H.iterdir()if p.is_file()];pub.append(publish(Path(__file__),H.name+'/audit.py'));old.save(H/'publication.json',{'at':old.now(),'HTTP_byte_verified_artifacts':pub})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E073');e.update(status='running',stage='Direct showdown numerical controls next',reason='D119corrects a read-only pointer decoder that omitted cvta. Same saved PTXnow proves both original32bit and candidate16bit boundary loads; original resource failure preserved. No criterion/source change or hardware rerun. Registers38/shared/local/occupancy unchanged. No numerical or speed claim.');e['evidence'].append({'label':'Original pointer-check failure and read-only correction','url':'evidence/D119-boundary-load-audit/report.json'});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E073',stage='Preparing E073 full raw GPU controls',activity='E073resource query unchanged. D119pure parser correction traces emitted cvta through the original narrow-load criterion. No GPU numerical/speed trial yet; E051accepted/deployed gain12.44%unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
print(json.dumps({'status':report['status'],'same4PTXfiles_replayed':True,'criterion_unchanged':True,'new_compilers_or_GPUprocesses':0,'all_gates_pass':True,'report_sha256':old.sha(H/'report.json')}),flush=True)
