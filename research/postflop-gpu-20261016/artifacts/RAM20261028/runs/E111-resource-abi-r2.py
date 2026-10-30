"""Additive CPU header decoder repair; no compiler/module/kernel repetition."""
import re,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
R=ROOT/'runs/E111-resource'
def header(t,name):
 a=t.index('.visible .entry '+name+'(');b=t.index('{',a);return t[a:b]
def params(t,name):
 lines=[x.strip().rstrip(',')for x in t.splitlines()if x.strip().startswith('.param ')]
 assert len(lines)==27
 expected32={1,2,24,25,26}
 for i,line in enumerate(lines):
  expected=f'.param .u32 {name}_param_{i}'if i in expected32 else f'.param .u64 .ptr .align 1 {name}_param_{i}'
  assert line==expected,(i,line)
 return [x.replace(name+'_param_','FUNCTION_param_')for x in lines]
if sys.argv[1]=='prepare':
 q=h.read(R/'report.json');assert [k for k,v in q['gates'].items()if not v]==['cluster:original27paramABI'];h.custody()
 files=[Path(__file__),R/'protocol.json',R/'report.json',R/'execution/candidate-compute_120.ptx',R/'execution/candidate-compute_75.ptx',R/'probe.rs',R/'probe.exe',R/'candidate.cu']
 h.save(R/'abi-reader-plan-r2.json',{'id':'E111-ABI-reader-R2','at':h.now(),'status':'FROZEN_PRE_CORRECTED_CPU_HEADER_READER','input_sha256':{str(p):h.sha(p)for p in files},'cause':'Original regex required type immediately followed by name, omitting .ptr .align 1 qualifiers on22pointer parameters. It read the same5scalar parameters onboth sides then incorrectlyrequired27. Actualcompilerheaders retained; no candidate source/ABI mismatch observed.','correction':'Read all27 completeparameterlines includingexacttype,pointer/alignmentqualifiers,ordinal/width; normalize onlyfunctionname. Negativefixtures:wrongwidth,droppedparam,wrongpointeralignment. Preserveallotheroriginalresourcegates unchanged.','no_compiler_module_kernel_solver_or_speed_repeat':True})
 print(h.sha(R/'abi-reader-plan-r2.json'),flush=True)
else:
 h.pin(R/'abi-reader-plan-r2.json',sys.argv[2]);P=h.read(R/'abi-reader-plan-r2.json')
 for p,d in P['input_sha256'].items():h.pin(p,d)
 t=(R/'execution/candidate-compute_120.ptx').read_text();b=header(t,'up_show');c=header(t,'up_show_cluster');bp=params(b,'up_show');cp=params(c,'up_show_cluster');assert bp==cp
 for tag,mut in [('wrong_width',c.replace('.param .u32 up_show_cluster_param_24','.param .u64 up_show_cluster_param_24')),('dropped_param',c.replace('\t.param .u32 up_show_cluster_param_26','')),('wrong_pointer_alignment',c.replace('.ptr .align 1 up_show_cluster_param_0','.ptr .align 8 up_show_cluster_param_0'))]:
  assert mut!=c
  try:params(mut,'up_show_cluster')
  except AssertionError:pass
  else:raise AssertionError('missed negative '+tag)
 q=h.read(R/'report.json');g=dict(q['gates']);g['cluster:original27paramABI']=bp==cp;assert all(g.values());h.custody()
 h.save(R/'report-r2.json',{**q,'at':h.now(),'status':'pass_scoped_cluster_resources_ABI_mechanism_pending','gates':g,'original_report_sha256':h.sha(R/'report.json'),'additive_reader_plan_sha256':sys.argv[2],'parameter_schema':bp,'three_negative_fixtures_caught':True,'original_other_gates_unchanged':all(v==q['gates'][k]for k,v in g.items()if k!='cluster:original27paramABI'),'no_compiler_module_kernel_or_scientific_case_repeated':True})
 for name in ['abi-reader-plan-r2.json','report-r2.json']:
  p=R/name;dst=h.ar.DASHBOARD/'evidence'/R.name/name;assert not dst.exists();shutil.copyfile(p,dst)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+R.name+'/'+name,timeout=20)as z:assert z.read()==p.read_bytes()
 with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
  s=h.read(h.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E111');e.update(status='running',stage='Compiled resources and complete ABI pass; operand/host controls pending',reason='Original ABI regex skipped22pointerqualifiers; additive CPUreader compares all27complete parameters andcatches3negativefixtures. Same source/PTX/binary/resources, no compiler/native repeats. Cluster40regs/local0/static1040/dynamic26520/stack1024/max1024,activeclusters170. No candidatekernel orspeedrun.');e['evidence']+=[{'label':n,'url':'evidence/'+R.name+'/'+n}for n in ['abi-reader-plan-r2.json','report-r2.json']];s.update(updated_at=h.now(),active_experiment='E111',stage=e['stage'],activity=e['reason']+' E080 remains live.');h.ar.atomic_json(h.ar.STATUS,s)
 print('E111 corrected ABI/resource gate passed',flush=True)
