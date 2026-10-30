import sys,shutil,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/E112-resource'
def schema(old,new):return len(old)==20 and len(new)==19 and old[17]in['.u64 .ptr .align 1','.u64']and old[:17]+old[18:]==new
if sys.argv[1]=='prepare':
 q=h.read(H/'report.json');assert [k for k,v in q['gates'].items()if not v]==['compute_75:up_action:declared_ABI_20_to_19'];h.custody();files=[Path(__file__),H/'protocol.json',H/'report.json',H/'probe.rs',H/'probe.exe',H/'candidate.cu',H/'execution/candidate-compute_120.ptx',H/'execution/candidate-compute_75.ptx',H/'execution/complete.json']
 h.save(H/'ABI-reader-plan-r2.json',{'id':'E112-ABI-reader-R2','at':h.now(),'status':'FROZEN_PRE_CPU_HEADER_REASSESSMENT','input_sha256':{str(p):h.sha(p)for p in files},'cause':'Both actual20to19argument schemas already equal exact drop of parameter17. Original reader additionally demanded SM120 pointer qualifiers on the compatibility75header. Actual75source-matched pointer is .u64 without optional .ptr/.align qualifiers.','correction':'Accept only the two actually observed64bit pointer schemas at removedordinal17; preserve exact full attributes/order for every remainingparameter and allothergates. Width/count negativefixtures. Header alone doesnotprove semanticidentity; frozen source projection/caller binding remains a separate prerequisite.','completed_compiler_module_or_native_cases_repeated':0})
 print(h.sha(H/'ABI-reader-plan-r2.json'),flush=True)
else:
 h.pin(H/'ABI-reader-plan-r2.json',sys.argv[2]);P=h.read(H/'ABI-reader-plan-r2.json')
 for p,d in P['input_sha256'].items():h.pin(p,d)
 q=h.read(H/'report.json');g=dict(q['gates'])
 for arch,table in q['entry_tables'].items():
  b,c=table['up_action']['old_parameter_attributes'],table['up_action']['new_parameter_attributes'];assert schema(b,c)
  wrongold=b[:];wrongold[17]='.u32';wrongnew=c[:];wrongnew[-1]='.u64';assert not schema(wrongold,c)and not schema(b,wrongnew)and not schema(b,c[:-1]);g[arch+':up_action:declared_ABI_20_to_19']=True
 assert all(g.values());h.custody();h.save(H/'report-r2.json',{**q,'at':h.now(),'status':'pass_scoped_constant_resources_ABI_operand_review_pending','gates':g,'original_report_sha256':h.sha(H/'report.json'),'reader_repair_plan_sha256':sys.argv[2],'negative_fixtures_caught_each_architecture':3,'original_other_gates_unchanged':all(v==q['gates'][k]for k,v in g.items()if k!='compute_75:up_action:declared_ABI_20_to_19'),'no_compiler_module_or_native_repeat':True,'constant_attribute_note':'Everyfunction reports12additionalconstantbytes because the module has one12byte symbol. Do not multiply this by9entries. Logical12bytes replace oldglobal12; actualdriverrounding/peak/capacity andquerycost remain unqualified.'})
 for name in ['ABI-reader-plan-r2.json','report-r2.json']:
  p=H/name;dst=h.ar.DASHBOARD/'evidence'/H.name/name;shutil.copyfile(p,dst)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+name,timeout=20)as z:assert z.read()==p.read_bytes()
 with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
  s=h.read(h.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E112');e.update(status='running',stage='Constant resources/ABI passed; operand/host controls pending',reason='Compatibility75ABI uses .u64 withoutSM120pointer qualifiers. Additive CPUreader verifies exact20to19schema andwidth/countnegativefixtures; same source/PTX/binary, no repeat. Action62to64regs,local64unchanged,shared0,stack/max1024,occupancy16/8/4same. One12byte moduleconstant, all costs pending.');e['evidence']+=[{'label':n,'url':'evidence/'+H.name+'/'+n}for n in ['ABI-reader-plan-r2.json','report-r2.json']];s.update(updated_at=h.now(),active_experiment='E112',stage=e['stage'],activity=e['reason']+' E080 remains live.');h.ar.atomic_json(h.ar.STATUS,s)
 print('E112 additive ABI and resource gate passed',flush=True)
