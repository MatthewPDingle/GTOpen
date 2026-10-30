"""Fixed compiler/raw/component gates for one readonly serial AVX2 prototype."""
import functools,json,math,operator,re,shutil,statistics,struct,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
assert len(sys.argv)==2;old.pin(H/'protocol-r2.json',sys.argv[1]);P=old.read(H/'protocol-r2.json');B=Path(P['output_dir']);E=H/'execution-r2'
def verify():
 old.pin(H/'protocol-r2.json',sys.argv[1])
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.custody()
verify();assert B.exists() and not E.exists();E.mkdir()
with old.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>=54*1024**3
 old.pin(B/'probe.exe',P['compiled_binary_sha256']);assert old.read(B/'rustc.exit.json')['returncode']==0;verify()
 assembly=list(B.glob('*.s'));alltext='\n'.join(p.read_text() for p in assembly);helpers={}
 aliases={m.group(1):m.group(2) for m in re.finditer(r'^\s*\.set\s+(\S+),\s*(\S+)',alltext,re.M)}
 labels={m.group(1):m.start() for m in re.finditer(r'^(\S*(?:portable_i16|portable_u16|wide_i16|wide_u16)\S*):$',alltext,re.M)}
 for name in ['portable_i16','portable_u16','wide_i16','wide_u16']:
  candidates=[n for n in sorted(set(labels)|set(aliases)) if name in n]
  coalesced=False
  if not candidates and name.endswith('_u16'):
   canonical=name.replace('_u16','_i16');candidates=[n for n in labels if canonical in n];coalesced=True
   assert len(re.findall(r'^\s*callq\s+\S*'+canonical+r'\S*$',alltext,re.M))==6
  assert candidates,(name,'missing retained typed path')
  symbol=candidates[0];resolved=symbol
  while resolved in aliases:resolved=aliases[resolved]
  assert resolved in labels,(name,resolved)
  text=alltext[labels[resolved]:];match=re.search(r'^\s*\.(?:section|def|globl)\b',text,re.M);body=text[:match.start()] if match else text
  assert 'retq' in body and (('%ymm' in body and 'vpor' in body) if name.startswith('wide') else ('%xmm' in body and 'por' in body and '%ymm' not in body)),(name,'unexpected vector code')
  path=H/(name+'.asm.txt')
  if path.exists():assert path.read_text(encoding='utf-8')==body
  else:path.write_text(body,encoding='utf-8',newline='\n')
  helpers[name]={'symbol':symbol,'resolved_symbol':resolved,'alias':symbol!=resolved,'compiler_coalesced_typed_path':coalesced,'assembly_sha256':old.sha(H/(name+'.asm.txt')),'uses_256bit':('%ymm' in body)}
 old.save(H/'compiler-gate.json',{'at':old.now(),'status':'pass_final_helper_codegen','helpers':helpers,'binary_sha256':old.sha(B/'probe.exe'),'native_executions':0,'assembly_sha256':{str(p):old.sha(p) for p in assembly}})
 old.child([str(B/'probe.exe'),'control',str(E/'control.bin')],E,'control',old.env(),120);verify()
 raw=(E/'control.bin').read_bytes();assert raw[:16]==b'D090-OR-RAW-v1\0\0';at=16;cases=0;words=0;checks=0
 def req(v,label):
  global checks
  assert v,label;checks+=1
 lengths=[0,1,7,8,15,16,17,31,32,33,63,64,65,127,128,129,257,513,4097]
 expected_descriptors=[(1,1,0,i) for i in range(65536)]+[(n,off,pattern,None) for n in lengths for off in range(4) for pattern in range(1,5)]
 for expected in expected_descriptors:
  header=struct.unpack_from('<9I',raw,at);at+=36;identity,n,off,pattern,result,*outputs=header;req(identity==cases and (n,off,pattern)==expected[:3],'case descriptor')
  arrays=[]
  for _ in range(3):
   count,=struct.unpack_from('<Q',raw,at);at+=8;req(count==off+n+3 and at+2*count<=len(raw),'complete raw array bounds');values=struct.unpack_from('<'+str(count)+'H',raw,at);at+=2*count;arrays.append(values);words+=count
  before,after_unsigned,after_signed=arrays;req(before==after_unsigned==after_signed,'all actual readonly input/guard words unchanged');req(all(v==0xb1a5 for v in before[:off]+before[off+n:]),'prefix and suffix guards')
  if pattern==0:req(before[off]==expected[3],'all65536singleword values')
  else:
   values=[0 if pattern==1 else ((1<<((i+off)%16)) if i==n//2 else 0) if pattern==2 else (0x8000 if i+1==n else 0) if pattern==3 else (i*1337+i//7+off*79)%65536 for i in range(n)]
   req(tuple(values)==before[off:off+n],'full deterministic vector inputs')
  oracle=functools.reduce(operator.or_,before[off:off+n],0);req(result==oracle and outputs==[oracle]*4,'all4actual OR outputs exact');cases+=1
 req(at==len(raw) and cases==P['expected_control_cases']==65840,'complete raw endpoint and case inventory')
 marker=[json.loads(x.split('D090 ',1)[1]) for x in (E/'control.stdout.log').read_text().splitlines() if x.startswith('D090 ')];req(len(marker)==1 and marker[0]['cases']==cases and marker[0]['all_result_bits_exact'],'native control inventory')
 old.save(H/'control-report.json',{'at':old.now(),'status':'pass_raw_integer_OR_equivalence','cases':cases,'raw_checks':checks,'full_input_post_and_guard_words':words,'raw_sha256':old.sha(E/'control.bin'),'compiler_gate_sha256':old.sha(H/'compiler-gate.json'),'performance_measured':False,'gpu_executions':0,'optimization_accepted':False})
 results={};shape=None
 for identity in P['order']:
  verify();old.ar.refuse_active(old.ar.live_status());arm='baseline' if identity.startswith('D090B') else 'avx2';old.child([str(B/'probe.exe'),arm],E,identity,old.env(),120);verify()
  rows=[json.loads(x.split('D090 ',1)[1]) for x in (E/(identity+'.stdout.log')).read_text().splitlines() if x.startswith('D090 ')];req(len(rows)==1,'one complete component result');r=rows[0];req(r['stage']=='benchmark' and r['arm']==arm and r['fresh_results']==r['pretouched_results']==[0,0,0,0] and r['nodes']==1346813 and r['cpu_arena_bytes']==1386321040 and r['avx2_detected'],'exact fresh solver shape/results')
  req(all(math.isfinite(r[k]) and r[k]>0 for k in ['fresh_ms','pretouched_ms']),'valid native clocks')
  if shape is None:shape=r['shapes']
  req(r['shapes']==shape,'same actual fourstore geometry');results[identity]=r;print('D090 completed',identity,flush=True)
 b=[results[p['baseline']]['fresh_ms'] for p in P['pairs']];a=[results[p['avx2']]['fresh_ms'] for p in P['pairs']];bm,am=statistics.median(b),statistics.median(a);gains=[100*(x-y)/x for x,y in zip(b,a)]
 gain=100*(bm-am)/bm;blocks=[statistics.median(gains[i:i+4]) for i in range(0,16,4)];orders={o:statistics.median(g for p,g in zip(P['pairs'],gains) if p['order']==o) for o in ['BA','AB']};warm_b=statistics.median(results[p['baseline']]['pretouched_ms'] for p in P['pairs']);warm_a=statistics.median(results[p['avx2']]['pretouched_ms'] for p in P['pairs'])
 gates={'baseline_fresh_representative':0.75*P['baseline_representative_reference_ms']<=bm<=1.25*P['baseline_representative_reference_ms'],'fresh_gain_at_least25pct':gain>=P['fresh_minimum_gain_pct'],'at_least13positive_pairs':sum(g>0 for g in gains)>=P['minimum_positive_pairs'],'positive_paired_median':statistics.median(gains)>0,'all4blocks_positive':all(g>0 for g in blocks),'both_orders_positive':all(g>0 for g in orders.values()),'pretouched_median_not_slower':warm_a<=warm_b}
 report={'at':old.now(),'status':'admit_further_candidate_investigation' if all(gates.values()) else 'closed_component_gate_failed','protocol_sha256':sys.argv[1],'fresh_baseline_median_ms':bm,'fresh_avx2_median_ms':am,'fresh_gain_pct':gain,'paired_gains_pct':gains,'positive_pairs':sum(g>0 for g in gains),'paired_median_gain_pct':statistics.median(gains),'block_median_gains_pct':blocks,'order_median_gains_pct':orders,'pretouched_baseline_median_ms':warm_b,'pretouched_avx2_median_ms':warm_a,'gates':gates,'results':results,'all32native_processes_retained':True,'control_report_sha256':old.sha(H/'control-report.json'),'excluded_samples':[],'extension_runs':0,'historical_timing_samples_used':0,'gpu_executions':0,'solver_source_activated':False,'optimization_accepted':False,'limits':'Isolated four q+scale scans only; no GPU, snapshot guards, whole constructor, solve or no-tradeoff/capacity qualification. A component pass only admits source review. No complete-cycle saving inferred from percentages.'}
 old.save(H/'report.json',report);old.save(E/'complete.json',{'at':old.now(),'all_children_terminal':True,'all32benchmark_processes_retained':True,'report_sha256':old.sha(H/'report.json'),'accepted_source_main_live_ptx_unchanged':True});verify()
print(json.dumps({k:report[k] for k in ['status','fresh_baseline_median_ms','fresh_avx2_median_ms','fresh_gain_pct','positive_pairs','gates']}),flush=True)
