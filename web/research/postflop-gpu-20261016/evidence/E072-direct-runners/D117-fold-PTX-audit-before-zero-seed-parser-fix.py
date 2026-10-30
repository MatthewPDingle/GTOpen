"""Read-only PTX/source audit of E072's static opcode-count rejection."""
from pathlib import Path
import ast,collections,hashlib,json,re,shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as c
c.custody();assert not(R/'gpu-run.lock').exists();H=R/'runs/E072-resource';D=R/'runs/D117-fold-PTX-audit';D.mkdir()
q=c.read(H/'report.json');assert q['status']=='rejected_compiled_prerequisite'and[k for k,v in q['gates'].items()if not v]==['compute_120:FP_opcode_counts_exact']
for name,h in q['ptx_sha256'].items():c.pin(H/'execution'/(name+'.ptx'),h)
source=R/'runs/D116-prepare.py';tree=ast.parse(source.read_text(encoding='utf-8'));literals={}
for node in tree.body:
 if isinstance(node,ast.Assign)and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
  try:literals[node.targets[0].id]=ast.literal_eval(node.value)
  except(ValueError,TypeError):pass
S=R/'runs/E072-source';base=(S/'baseline.cu').read_text(encoding='utf-8');candidate=(S/'candidate.cu').read_text(encoding='utf-8')
reverse=candidate.replace(literals['reuse'],'',1).replace(literals['newloop'],literals['oldloop'],1).replace(literals['staging'],'',1).replace(literals['storage'],literals['declaration'],1).replace('fold_scratch.total_parts[','total_parts[')
assert reverse==base
def entry(path):
 text=path.read_text(encoding='utf-8');i=text.index('.visible .entry up_fold(');start=text.index('{',i);j=start+1;depth=1
 while depth:
  if text[j]=='{':depth+=1
  elif text[j]=='}':depth-=1
  j+=1
 return text[i:j]
def analyze(text):
 adds=[{'destination':m[1],'accumulator_operand':m[2],'loaded_operand':m[3],'offset':m.start()}for m in re.finditer(r'\badd\.f32\s+(%f\d+),\s*(%f\d+),\s*(%f\d+);',text)]
 counts=collections.Counter(x['destination']for x in adds);repeated=[k for k,n in counts.items()if n>1];assert len(repeated)==1,repeated
 accumulator=repeated[0];bydest=collections.defaultdict(list)
 for index,item in enumerate(adds):bydest[item['destination']].append(index)
 sharedloads={m[1] for m in re.finditer(r'\bld\.shared\.f32\s+(%f\d+),\s*\[',text)}
 groups=[];covered=set()
 for root in bydest[accumulator]:
  chain=[];index=root
  while True:
   assert index not in covered;covered.add(index);chain.append(index);item=adds[index]
   assert item['loaded_operand']in sharedloads,'every card addition second operand is a shared-reach load'
   previous=item['accumulator_operand']
   if previous==accumulator:break
   assert len(bydest[previous])==1,'unambiguous left-fold producer';index=bydest[previous][0]
  chain.reverse();assert all(adds[chain[i]]['destination']==adds[chain[i+1]]['accumulator_operand']for i in range(len(chain)-1))
  groups.append({'length':len(chain),'instruction_offsets':[adds[i]['offset']for i in chain],'operations':[adds[i]for i in chain]})
 lengths=sorted((x['length']for x in groups),reverse=True);width=max(lengths);assert width&(width-1)==0
 assert sum(lengths)==2*width-1 and len(adds)-len(covered)==3
 fp=collections.Counter(re.findall(r'\b(?:add|sub|mul|fma|div|rcp|sqrt|abs|max|min|setp)(?:\.[A-Za-z0-9_]+)*\.f(?:32|64)\b',text))
 assert dict(fp)=={'add.f32':len(adds),'sub.f32':2,'mul.f32':1},dict(fp)
 return {'FP_opcode_counts':dict(fp),'card_accumulator':accumulator,'card_addition_sites':len(covered),'other_addition_sites':len(adds)-len(covered),'unrolled_card_accumulator_chain_lengths':lengths,'main_unroll_width':width,'every_card_chain_serially_left_associated':True,'every_card_add_uses_shared_reach_operand':True,'groups':groups,'limits':'Static PTX recurrence structure, not a complete CFG trip-count/address proof, SASS execution or GPU numerical equivalence.'}
analysis={}
for arch in ['compute_120','compute_75']:
 arms={v:analyze(entry(H/'execution'/f'{v}-{arch}.ptx'))for v in ['baseline','candidate']};b,v=arms['baseline'],arms['candidate']
 assert b['other_addition_sites']==v['other_addition_sites']==3
 assert b['FP_opcode_counts']['add.f32']-v['FP_opcode_counts']['add.f32']==b['card_addition_sites']-v['card_addition_sites']==2*(b['main_unroll_width']-v['main_unroll_width'])
 analysis[arch]=arms
assert analysis['compute_120']['baseline']['main_unroll_width']==16 and analysis['compute_120']['candidate']['main_unroll_width']==8
assert analysis['compute_75']['baseline']['main_unroll_width']==analysis['compute_75']['candidate']['main_unroll_width']==4
amended={k:v for k,v in q['gates'].items()if not k.endswith(':FP_opcode_counts_exact')}
amended.update(source_computational_statements_reverse_exact=True,static_FP_count_difference_fully_explained_by_card_chain_sites=True,each_unrolled_card_chain_keeps_serial_left_association=True,noncard_FP_operation_counts_unchanged=True)
assert all(amended.values())
report={'id':'D117','at':c.now(),'status':'pass_static_count_false_positive_audit_admit_raw_numerical_controls','original_resource_outcome':q['status'],'original_report_sha256':c.sha(H/'report.json'),'original_failed_gate_preserved':'compute_120:FP_opcode_counts_exact','source_candidate_sha256':c.sha(S/'candidate.cu'),'source_candidate_unchanged':True,'source_reverse_equals_accepted':True,'analysis':analysis,'amended_prerequisite_gates':amended,'assessment_correction':'Static FP opcode count equality is not an accuracy condition: the same serial card accumulator is emitted with16wide versus8wide unrolling oncompute120. All16static ADDsite differences are in that card loop; both other ADDsites3,SUBsites2,MULsite1 remain unchanged. Compute75retains4wide in both arms. Replace the invalid raw-count-equality proxy by source reversal and explicit left-associated card-chain structural checks. Do not call this a numerical pass.','scientific_limits':'No GPU arithmetic, full CFG/address proof, compiler/SASS correctness, dynamic transaction count, resource-cost or speed conclusion follows from this static audit. The frozen E072source must pass separately registered full raw GPU outputs/input/guard controls including nonfinite cases before any integrated speed trial. No count threshold, accuracy tolerance or performance cutoff is relaxed.','authority_and_boundary':'Correcting an agent-authored assessment proxy within the user-authorized research, before any E072numerical/performance outcome. Original source, resource command, run and failed assessment remain immutable. No recompile/resource rerun/source/cache-size/threshold variant and no failed numerical/speed family reopening.','source_policy_relation':'Original no-variant/no-retry rule is retained: the original CUDAbytes and sole resource execution are reused without another execution. This additive assessment correction does not erase or relabel the original failed gate.','new_compiler_CUDA_resource_or_application_kernel_executions':0,'new_solver_or_performance_executions':0,'root_analysis_not_external_audit':True,'accepted_and_live_source':'E051','input_sha256':{str(p):c.sha(p)for p in [Path(__file__),source,H/'report.json',H/'protocol.json',S/'candidate.cu',S/'baseline.cu',*[H/'execution'/f'{v}-{a}.ptx'for v in ['baseline','candidate']for a in ['compute_120','compute_75']]]}}
c.save(D/'report.json',report)
def publish(src,key):
 dst=c.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(src,dst)
 with urllib.request.urlopen(c.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==src.read_bytes()
 return {'url':'evidence/'+key,'sha256':c.sha(src)}
published=[publish(D/'report.json',D.name+'/report.json'),publish(Path(__file__),D.name+'/audit.py')]
with c.ar.exclusive_lock(c.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=c.read(c.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E072');e.update(status='running',stage='Compiler count proxy corrected; direct GPU controls next',correctness='Source/address/resource prerequisites pass; GPU numerical result untested',reason='The original static-opcode-count gate failed and is preserved. PTX audit identifies16wide versus8wide card-loop unrolling, with all count differences in the same serial card recurrence. That proxy is corrected before any numerical or timing result; source and resource execution are unchanged. Full raw GPU controls still mandatory.',updated_at=c.now());e['evidence'].append({'label':'Preserved static-count failure and recurrence audit','url':'evidence/'+D.name+'/report.json'});s.update(updated_at=c.now(),state='running',goal_status='active',active_experiment='E072',stage='Preparing E072 direct GPU controls',activity='The static floating-opcode checker produced a false positive from different loop unrolling. The original failure is retained; the CUDA candidate is unchanged. Resource limits pass, but GPU numerical equivalence is still untested. Freeze full raw-output controls before any timing. E051 remains deployed.');c.ar.atomic_json(c.ar.STATUS,s)
c.save(D/'publication.json',{'at':c.now(),'http_byte_verified_artifacts':published,'source_main_live_PTX_custody_pass':True,'new_application_kernel_launches':0})
c.custody();print({'status':report['status'],'compute120_unroll':[16,8],'compute75_unroll':[4,4],'original_report_preserved':True,'candidate_unchanged':True,'no_GPU_numerical_or_timing_executions':True},flush=True)
