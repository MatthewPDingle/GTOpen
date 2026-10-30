import ast,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists();assert shutil.disk_usage(ROOT).free>=66*1024**3
R=ROOT/'runs/E108-resource';S=ROOT/'runs/E108-source';N=ROOT/'runs/D225-chunk-native-bypass';C=ROOT/'runs/D224-chunk-PTX-CFG-r3';parent=ROOT/'runs/E107-kernel-control';H=ROOT/'runs/E108-kernel-control'
resource=h.read(R/'report.json');assert all(resource['gates'].values())and h.read(C/'report.json')['all_values_exact']and h.read(N/'report.json')['status']=='pass_static_native_chunk_bypass';assert not H.exists();H.mkdir()
for n in ['baseline.cu','candidate.cu']:shutil.copyfile(S/n,H/n)
for arm in ['baseline','candidate']:
 p=R/('baseline-compute_120.ptx'if arm=='baseline'else'execution/candidate-compute_120.ptx');h.pin(p,resource['PTX_sha256'if 'PTX_sha256'in resource else'ptx_sha256'][arm+'-compute_120']);shutil.copyfile(p,H/(arm+'.ptx'))
for n in ['corpus.json','accepted-evaluator.rs']:shutil.copyfile(parent/n,H/n)
P0=h.read(parent/'protocol.json');h.pin(H/'corpus.json',P0['input_sha256'][str(parent/'corpus.json')]);corpus=h.read(H/'corpus.json');assert len(corpus['cases'])==764 and len(corpus['geometries'])==116
widths=[1,32,64,128,256,3,48,96,192,255]
for name in ['probe.rs','execute.py','audit.py']:
 t=(parent/name).read_bytes().decode('utf-8').replace('E107','E108').replace('earlier payout-load scheduling','guarded chunk integer division').replace('early_payout_raw_equivalence','chunk_division_raw_equivalence')
 # Replace old launch totals before pair totals so the new pair count is not
 # accidentally changed into the launch count.
 t=t.replace('7640','15280').replace('3823','7643').replace('3820','7640')
 t=t.replace('[1,32,64,128,256]','[1,32,64,128,256,3,48,96,192,255]').replace('[1u32,32,64,128,256]','[1u32,32,64,128,256,3,48,96,192,255]')
 if name=='probe.rs':
  for a,b in [('assert_eq!(active_words,2018600);','assert_eq!(active_words,4037200);'),('assert_eq!(guard_checks,16703320);','assert_eq!(guard_checks,33406640);'),('assert_eq!(input_checks,160440);','assert_eq!(input_checks,320880);')]:assert t.count(a)==1;t=t.replace(a,b,1)
 elif name=='execute.py':t=t.replace('pass_compiled_prerequisites_numerical_pending','pass_compiled_resource_prerequisites_semantics_pending')
 if name.endswith('.py'):ast.parse(t)
 (H/name).write_bytes(t.encode('utf-8'))
cmd=[x.replace(str(R),str(H))for x in h.read(R/'protocol.json')['rustc_command']]
files=[Path(__file__),R/'report.json',C/'protocol.json',C/'report.json',N/'report.json',N/'reader-plan.json',parent/'protocol.json',parent/'probe.rs',parent/'execute.py',parent/'audit.py',ROOT/'epoch/common.py']+[p for p in H.iterdir()if p.is_file()]+[p for p in S.iterdir()if p.is_file()]+[p for p in (ROOT/'reference/accepted-e080-deps').iterdir()if p.is_file()]
h.save(H/'protocol.json',{'id':'E108-kernel-control','at':h.now(),'status':'FROZEN_PRE_FIRST_APPLICATION_KERNEL','rustc_command':cmd,'input_sha256':{str(p):h.sha(p)for p in files},'resource_report':str(R/'report.json'),'PTX_CFG_report':str(C/'report.json'),'native_mechanism_report':str(N/'report.json'),'widths':widths,'base_cases':764,'geometries':116,'original_cases_retained_exact':764,'original_width_prefix':[1,32,64,128,256],'nonpower_fallback_widths':[3,48,96,192,255],'expected_pairs':7640,'expected_application_launches':15280,'expected_active_words':4037200,'expected_guard_word_checks':33406640,'sealed_PTX_sha256':{a:h.sha(H/(a+'.ptx'))for a in ['baseline','candidate']},'scope':'Retain entire original764case E107 showdown/payout corpus byte-exact. First original5widths unchanged, then5nonpower widths including3/48/96/192/255, same full case order. All21actual immutable input buffers, complete physicalCFV and unownedguards exact. One compiler/one fixed15280launch process then complete retained rawreader, no repeated native case or extensions. Direct arbitrary nonpower controls are tests of the existing fallback; production width128 unchanged. No NVRTC/sourceactivation/solve/performance. Any real mismatch closes exact frozen chunk-divide form without source/if/ternary/helper/width/flags/threshold/entrysubset/quality/sample rescue. Finite physical poker cases and NaN/Inf/payout controls, no universal/device-ISA proof.','candidate_accepted':False,'performance_measurement':False})
for folder,names in [(H,['protocol.json']),(N,['report.json'])]:
 for name in names:
  p=folder/name;dst=h.ar.DASHBOARD/'evidence'/folder.name/name;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():assert dst.read_bytes()==p.read_bytes()
  else:shutil.copyfile(p,dst)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+folder.name+'/'+name,timeout=20)as z:assert z.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);s['experiments'].append({'id':'D225','title':'Native chunk quotient bypass','kind':'diagnostic','status':'measured','accepted':False,'measurement_epoch':'RAM20261028','stage':'Static driver branch/shift/bypass witnesses passed','reason':'Current-driver width predicate and shift path jump over the integer divider lowering and join original chunk scan. Static mappings are inferences linked to exhaustive PTX, no hardware timing or device float proof.','evidence':[{'label':'Native control-flow witnesses and limits','url':'evidence/'+N.name+'/report.json'}]});e=next(x for x in s['experiments']if x['id']=='E108');e.update(stage='Frozen full-output power and nonpower GPU controls',correctness='CPU_PTX_native_mechanism_resource_prerequisites_pass',reason='7640fixed original/candidate pairs across10widths; includes all prior physical/exceptional controls and explicit nonpower fallback. No speed claim.');e['evidence']+=[{'label':'Native bypass witnesses','url':'evidence/'+N.name+'/report.json'},{'label':'Frozen direct GPU matrix','url':'evidence/'+H.name+'/protocol.json'}];s.update(updated_at=h.now(),active_experiment='E108',stage='Chunk division full raw GPU equivalence controls',activity='Static branch/resource prerequisites passed. Compare all outputs/inputs/guards at original and nonpower widths before full solver/ordinary timing. No new gain adopted; E080 stays live.');h.ar.atomic_json(h.ar.STATUS,s)
print(h.sha(H/'protocol.json'),flush=True)
