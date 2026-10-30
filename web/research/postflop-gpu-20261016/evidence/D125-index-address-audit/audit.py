"""Read-only semantic decode audit of the four immutable E077 PTX files."""
from pathlib import Path
import collections,json,re,shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not (R/'gpu-run.lock').exists();H=R/'runs/D125-index-address-audit';assert not H.exists();H.mkdir()
E=R/'runs/E077-resource';Q=old.read(E/'report.json');P0=old.read(E/'protocol.json')
for p,h in P0['input_sha256'].items():old.pin(p,h)
for key,h in Q['ptx_sha256'].items():old.pin(E/'execution'/(key+'.ptx'),h)
failed=[k for k,v in Q['gates'].items()if not v];assert failed==['compute_120:low31bit_decode_masks_emitted','compute_75:low31bit_decode_masks_emitted']
paths=[Path(__file__),E/'protocol.json',E/'report.json',E/'execute.py',R/'runs/E077-resource-manager/closure.json',R/'runs/E077-source/manifest.json',R/'runs/E077-source/source-review.json',R/'runs/D124-prefix-liveness/protocol.json',R/'runs/D124-prefix-liveness/report.json',C/'common_e051_live.py',C/'protected-main.json',*[E/'execution'/(key+'.ptx')for key in Q['ptx_sha256']]]
P={'id':'D125','at':old.now(),'scope':'Read-only audit of exact existing E077 sources, four PTX files and resource rows; zero compiler/native/CUDA/GPU/solver/timing executions, no source/binary/flag/mask/width changes.','input_sha256':{str(p):old.sha(p)for p in paths},'original_failure':'The authored prerequisite counted >=2 literal32bit low31 masks. Actual compiler combines a low31 hand-index mask with multiplication by4 into a64bit byte-offset mask. The original literal-count rejection/report is immutable.','prospective_replacement_before_first_numerical_or_speed_run':'Replace the invalid static spelling/count proxy with source-parameter/address dataflow proving that every memory address derived from p_idx/o_idx clears bit31, recognizes only exact low31word or low33byte-offset masks after a zero-extended shift2, and has no unmasked or multiply-defined tagged-index path. Require both input parameters11/16 to reach masked address consumers, plus bitwise identity checks and all original ABI/other-entry/resource gates. This is validation repair, not a new source form or outcome-dependent timing rescue.','limits':'The dataflow verifier is deliberately restricted to this PTX integer subset and single-definition tagged-value slice. It proves tag stripping/address use, not full numerical semantics, active-store counts, dynamic traffic, universal compiler behavior or speed. Full compiled host tagging/GPU raw controls and all later gates remain.'};old.save(H/'protocol.json',P)
def publish(p,key):
 dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==p.read_bytes(),key
 else:shutil.copyfile(p,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
 return {'url':'evidence/'+key,'sha256':old.sha(p)}
pub=[publish(H/'protocol.json',H.name+'/protocol.json'),publish(Path(__file__),H.name+'/audit.py')]
checks=0
def ck(v,label):
 global checks
 assert v,label;checks+=1
def show(path):
 t=path.read_text(encoding='utf-8');a=t.index('.visible .entry up_show(');start=t.index('{',a);at=start+1;depth=1
 while depth:
  if t[at]=='{':depth+=1
  elif t[at]=='}':depth-=1
  at+=1
 return t[a:at]
def audit(text):
 ptr={};value={};definitions=collections.Counter();sources=[];sinks=[];masks=[];unmasked=[];unknown=[];touched=set()
 for line_no,raw in enumerate(text.splitlines(),1):
  t=raw.strip().split('//',1)[0].strip();t=re.sub(r'^@!?%\w+\s+','',t)
  ins=re.fullmatch(r'([A-Za-z][\w.]*)\s+(.*);',t)
  if not ins:continue
  op,args=ins.groups();parts=[a.strip()for a in args.split(',')];regs=re.findall(r'%\w+',args)
  if op.startswith('st.')or op.startswith('ld.'):
   address=re.search(r'\[(%\w+)(?:\+\d+)?\]',args)
   if address and value.get(address[1]):
    v=value[address[1]];record={'line':line_no,'instruction':t,'parameters':sorted(v['origins']),'decoded':v['decoded']}
    sinks.append(record)
    if not v['decoded']:unmasked.append(record)
  if op.startswith('st.')or op.startswith(('setp.','bra','bar.','ret','exit')):continue
  if not parts or not re.fullmatch(r'%\w+',parts[0]):continue
  dst=parts[0];definitions[dst]+=1
  pm=re.fullmatch(r'ld\.param\.u64\s+%\w+,\s*\[up_show_param_(\d+)\];',t)
  if pm:ptr[dst]={int(pm[1])};value.pop(dst,None);continue
  if op.startswith('ld.'):
   address=re.search(r'\[(%\w+)(?:\+\d+)?\]',args);origin=ptr.get(address[1],set())if address else set()
   if op.startswith('ld.global')and origin in [{11},{16}]:
    v={'origins':set(origin),'decoded':False,'scale':0,'width':32};value[dst]=v;sources.append({'line':line_no,'register':dst,'parameter':next(iter(origin)),'instruction':t});touched.add(dst)
   else:value.pop(dst,None)
   ptr.pop(dst,None);continue
  operands=re.findall(r'%\w+',','.join(parts[1:]));taints=[value[r]for r in operands if r in value];pointer=set().union(*(ptr.get(r,set())for r in operands));ptr[dst]=pointer
  if not taints:value.pop(dst,None);continue
  v={'origins':set().union(*(v['origins']for v in taints)),'decoded':all(v['decoded']for v in taints),'scale':None,'width':64 if op.endswith('64') else 32}
  one=taints[0]if len(taints)==1 else None
  if op.startswith(('cvt.u64.u32','mov.u32','mov.u64'))and one:v['scale']=one['scale']
  elif op.startswith('shl.b64')and one and len(parts)==3 and parts[2]=='2':v['scale']=None if one['scale']is None else one['scale']+2
  elif op in ['and.b32','and.b64']and one:
   constants=[int(x,0)for x in parts[1:]if re.fullmatch(r'(?:0x[0-9a-fA-F]+|\d+)',x)]
   word=op=='and.b32'and constants==[2147483647]and one['scale']==0 and one['width']==32
   byte=op=='and.b64'and constants==[8589934588]and one['scale']==2 and one['width']==64
   if word or byte:v['decoded']=True;v['scale']=0 if word else 2;masks.append({'line':line_no,'instruction':t,'parameters':sorted(v['origins']),'form':'low31word'if word else'low33byte_offset'})
   else:v['decoded']=False;unknown.append({'line':line_no,'instruction':t,'reason':'Unrecognized index mask'})
  elif op.startswith(('add.','sub.','mul.','mad.','shl.','shr.','cvta.','cvt.','mov.')):pass
  else:v['decoded']=False;unknown.append({'line':line_no,'instruction':t,'reason':'Unsupported tagged-value arithmetic'})
  value[dst]=v;touched.add(dst)
 multiple={r:definitions[r]for r in touched if definitions[r]!=1}
 return {'sources':sources,'address_sinks':sinks,'mask_witnesses':masks,'unmasked_address_sinks':unmasked,'unsupported_index_operations':unknown,'multiply_defined_index_slice_registers':multiple,'source_parameters':sorted({x['parameter']for x in sources}),'sink_parameters':sorted({p for x in sinks for p in x['parameters']}),'mask_parameters':sorted({p for x in masks for p in x['parameters']})}
# Parser tests are fixed before the retained PTX is assessed.
fixture='''ld.param.u64 %rd1, [up_show_param_16];
cvta.to.global.u64 %rd2, %rd1;
ld.global.nc.u32 %r1, [%rd2];
cvt.u64.u32 %rd3, %r1;
shl.b64 %rd4, %rd3, 2;
and.b64 %rd5, %rd4, 8589934588;
mov.u64 %rd6, shraw;
add.s64 %rd7, %rd6, %rd5;
ld.shared.f32 %f1, [%rd7];'''
f=audit(fixture);ck(not f['unmasked_address_sinks']and f['mask_parameters']==[16],'byte-mask fixture accepted')
for bad in [fixture.replace('8589934588','8589934584'),fixture.replace('shl.b64 %rd4, %rd3, 2','shl.b64 %rd4, %rd3, 3'),fixture.replace('and.b64 %rd5, %rd4, 8589934588','mov.u64 %rd5, %rd4')]:ck(bool(audit(bad)['unmasked_address_sinks']),'wrong/missing/shifted masks rejected')
word='''ld.param.u64 %rd1, [up_show_param_11];
ld.global.nc.u32 %r1, [%rd1];
and.b32 %r2, %r1, 2147483647;
cvt.u64.u32 %rd2, %r2;
mov.u64 %rd3, shraw;
add.s64 %rd4, %rd3, %rd2;
ld.shared.f32 %f1, [%rd4];'''
ck(not audit(word)['unmasked_address_sinks']and audit(word)['mask_parameters']==[11],'word-mask fixture accepted')
ck(bool(audit(word.replace('2147483647','4294967295'))['unmasked_address_sinks']),'nonclearing word mask rejected')
# Shift/AND distribute over OR. Equality for every input bit proves the
# identity for every32bit word; legal physical IDs are additionally replayed.
for x in [0,*[1<<b for b in range(32)],0xffffffff,0x7fffffff,0x80000000]:ck(((x<<2)&8589934588)==((x&2147483647)<<2),'all-bit algebra identity')
for i in range(1326):
 for bit in [0,1<<31]:ck((((i|bit)<<2)&8589934588)==i*4 and((i|bit)&2147483647)==i,'all legal physical hand IDs decode both tag states')
analyses={};gates={k:v for k,v in Q['gates'].items()if k not in failed}
for arch in ['compute_120','compute_75']:
 a=audit(show(E/'execution'/('candidate-'+arch+'.ptx')));analyses[arch]=a
 gates[arch+':every_tagged_index_address_is_decoded']=not a['unmasked_address_sinks']and not a['unsupported_index_operations']and not a['multiply_defined_index_slice_registers']
 gates[arch+':both_index_parameters_have_masked_address_consumers']=a['source_parameters']==a['sink_parameters']==a['mask_parameters']==[11,16]
 ck(gates[arch+':every_tagged_index_address_is_decoded'],arch+' complete tagged-index address audit')
 ck(gates[arch+':both_index_parameters_have_masked_address_consumers'],arch+' both physical index inputs covered')
old.custody();ck(all(gates.values()),'all original semantic/ABI/resource and replacement address gates pass')
report={'id':'D125','at':old.now(),'status':'pass_original_tag_decode_semantics_with_byte_offset_masks','protocol_sha256':old.sha(H/'protocol.json'),'original_resource_report_sha256':old.sha(E/'report.json'),'original_report_and_failed_literal_proxy_preserved':True,'original_failed_literal_count_gates':failed,'effective_gates':gates,'address_analyses':analyses,'checks':checks,'compiled_source_PTX_and_resource_rows_unchanged':True,'compiler_native_GPU_solver_or_timing_executions':0,'admit_compiled_host_and_full_raw_GPU_controls':True,'source_main_live_PTX_custody_pass':True,'candidate_accepted':False,'limits':P['limits']+' No new performance or accuracy observation and no source/timing rescue. Literal32bit mask count was an invalid spelling proxy; exact byte-offset mask is verified against both original input-parameter/address slices and legal hand domain.'};old.save(H/'report.json',report)
for p in H.iterdir():
 if p.is_file()and p.suffix=='.json':pub.append(publish(p,H.name+'/'+p.name))
old.save(H/'publication.json',{'at':old.now(),'HTTP_byte_verified_artifacts':pub,'new_native_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E077');e.update(status='running',stage='Compiled host-tag and full raw GPU controls next',correctness='Retained demand and compiled address-tag semantics pass',reason='Original literal32bit-mask-count proxy failed because NVRTC folded a mask into64bit byte-offset arithmetic. Immutable original rejection retained. Read-only D125 proves both index parameters feed only decoded memory addresses; all original ABI/other-entry/resource gates remain passed. No source/compiler/numerical/timing rerun; host/GPU raw controls still pending.');e['evidence'].append({'label':'Read-only byte-offset/address semantic audit','url':'evidence/D125-index-address-audit/report.json'});s['experiments'].append({'id':'D125','at':old.now(),'title':'Verify compiler-folded hand-index byte-offset masks','kind':'diagnostic','status':'measured','correctness':'Both PTX address slices and all legal hand IDs pass','stage':'Read-only prerequisite repair','reason':'Original literal-count report preserved. Semantic masks survive in widened byte offsets; same source/four PTX/resource rows, zero new native executions. No GPU accuracy or speed result.','accepted':False,'evidence':[{'label':'Frozen read-only protocol','url':'evidence/D125-index-address-audit/protocol.json'},{'label':'Address and mask proof','url':'evidence/D125-index-address-audit/report.json'}]});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E077',stage='Preparing E077 exact host/GPU controls',activity='D125 verified the original E077 decode mechanism in immutable widened PTX address masks; initial literal proxy failure preserved. Resources fit unchanged allocation quantum. No new kernel/source/compiler/timing. Exact host tag maps and full raw GPU controls next; E051 accepted/live gain12.44% unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### D125 read-only widened index-mask address audit'not in raw
entry=f'''

### D125 read-only widened index-mask address audit

E077's original sole resource run returned a rejection only because an authored proxy required >=2 literal and.b32 low31 masks. All ABI27/other8 source-matched PTX/resource gates passed, registers38to39 within the same allocation quantum/driver occupancy, local0/static1040/dynamic unchanged, no warnings. Actual saved PTX has one word mask and two equivalent64bit byte-offset masks8589934588 = (2^31-1)<<2. The original report/protocol/failed literal-count outcome remain immutable. This is not an actual numerical, quality, timing or resource failure; no such runs exist.

Before any first numerical/timing run, D125 freezes {old.sha(H/'protocol.json')} to replace the invalid spelling/count proxy with stricter dataflow semantics on those same4PTX/source/resource artifacts. Track original parameters11(p_idx)/16(o_idx) through pointer origins, raw tagged loads, zero-extends, shifts, exact recognized low31word/low33byte masks and every derived memory-address sink. Require both parameters to have decoded address consumers, no unmasked/unsupported or multiply-defined tagged register slice, every other original prerequisite unchanged. Fixed positive/negative parser fixtures reject missing/wrong/shifted masks. Shift/AND's per-input-bit identity plus all1326physical IDs with both tag states verify byte-index equality. This is the declared PTX integer subset/address slice, not a general compiler or numerical proof.

Both compute120/75 address analyses pass, {checks} checks, resource rows/source/PTX unchanged. Report SHA {old.sha(H/'report.json')}; analyses retain every source, mask and address-sink instruction. No native compiler/resource/kernel/solver/performance/source execution or variant. Original failed report is linked, not overwritten or relabeled; the effective semantic prerequisite is a separate attributed validation repair, like prior invalid static proxy corrections, before any GPU numerical or speed result. Root audit is not external independence.

E077 may now proceed only with its exact frozen source through compiled12-case host tagging and full raw GPU controls; full-cycle1%/strictfixture/fresh16/broad/material/holdout/cumulative remain. Published protocol/source/report HTTP byte verified, accepted162/main163/live/protected2PTX exact, all old handles terminal and no GPU lock. E051 accepted/deployed12.4372274192% and last primary B243 unchanged; goal active.
''';nl=b'\r\n'if b'\r\n'in raw else b'\n';ledger.write_bytes(raw+entry.encode().replace(b'\n',nl));old.custody();subprocess.run(['git','commit','--only','-m','research: verify widened index decode from immutable PTX addresses','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True);old.custody();print(json.dumps({'status':report['status'],'checks':checks,'new_native_executions':0,'source_and_original_report_unchanged':True}),flush=True)
