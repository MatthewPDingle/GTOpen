import difflib,hashlib,json,re,shutil,struct,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists();h.ar.refuse_active(h.ar.live_status())
D=ROOT/'runs/D181-ordered-card-phases';D.mkdir(exist_ok=False)
def body(src,name):
 m=re.search(r'void\s+'+name+r'\(',src)
 if not m:return None
 a=src.index('{',m.end());j=a+1;depth=1
 while depth:
  if src[j]=='{':depth+=1
  elif src[j]=='}':depth-=1
  j+=1
 return src[a:j]
unique={};matches=[];files=0
for root in [Path(r'S:\GTOpen-research\postflop-gpu-20261016\runs'),ROOT/'runs']:
 for p in root.rglob('*.cu'):
  src=p.read_text(encoding='utf-8-sig');b=body(src,'up_show')
  if b is None:continue
  files+=1;digest=hashlib.sha256(b.encode()).hexdigest();unique.setdefault(digest,str(p))
  if re.search(r'while\s*\([^\n]*(?:\blb\b|\bub\b|\bc1\b)|for\s*\(;\s*t\s*<\s*c1|lower_bound|upper_bound',b):matches.append(str(p))
assert not matches,matches
q=['git','log','--all','--oneline','-G',r'while.*(pos.*lb|pos.*ub)|for *\(; *t *< *c1','--','crates/solver/src/gpu/kernels.cu'];run=subprocess.run(q,cwd=h.REPO,text=True,capture_output=True);assert run.returncode==0 and not run.stderr and not run.stdout.strip()
h.save(D/'history.json',{'at':h.now(),'retained_up_show_files':files,'unique_bodies':unique,'segmented_position_walk_matches':matches,'git_query':q,'git_stdout':run.stdout,'classification':'No retained or all-local-ref matching phased card walk found. E089 only disables unrolling of the unchanged predicated walk; E084 reuses a card total; E020 caches position indices; E066 caches card offsets. This design changes the logical control algorithm using sorted card positions; it retains all ordered additions and composes none of those closed forms. Finite bounded semantic review, not remote exhaustive uniqueness.'})
def original(pos,lb,ub):
 out=[]
 for p in pos:
  out.append(('T',p))
  if p<lb:out.append(('L',p))
  elif p>=ub:out.append(('H',p))
 return out
def candidate(pos,lb,ub):
 out=[];t=0
 while t<len(pos) and pos[t]<lb:out.extend([('T',pos[t]),('L',pos[t])]);t+=1
 while t<len(pos) and pos[t]<ub:out.append(('T',pos[t]));t+=1
 while t<len(pos):out.extend([('T',pos[t]),('H',pos[t])]);t+=1
 return out
checks=0
for n in list(range(33))+[63,64,65,127,128,129,257,1081]:
 bounds=range(n+2) if n<=32 else sorted(set([0,1,n//2,n-1,n,n+1]))
 for pos in [list(range(n)),list(range(0,n,2)),list(range(1,n,3)),[]]:
  for lb in bounds:
   for ub in bounds:
    assert original(pos,lb,ub)==candidate(pos,lb,ub);checks+=1
assert original([2,0],1,2)!=candidate([2,0],1,2)
fields_needed={f'd_riv_card_{part}[{p}]' for part in ['off','pos'] for p in [0,1]};frames=[]
for row in h.read(ROOT/'runs/D179-shared-prefix-census/protocol.json')['input_frames']:
 path=Path(row['path']);assert path.stat().st_size==row['wholeframe_identity_from_prior_full_reader']['bytes'];fields={};ids={}
 with path.open('rb') as f:
  assert f.read(16)==b'D166-GPU-RAW1\0\0\0'
  while len(fields)<len(fields_needed):
   kind,length=struct.unpack('<II',f.read(8));assert kind in [0,2] and 0<length<512;name=f.read(length).decode();words,=struct.unpack('<Q',f.read(8));assert words<2**31
   if name in fields_needed:
    data=f.read(4 if kind==0 else words*4);assert len(data)==(4 if kind==0 else words*4);fields[name]=[0]*words if kind==0 else [x[0] for x in struct.iter_unpack('<I',data)];ids[name]={'words':words,'payload_sha256':hashlib.sha256(data).hexdigest()}
   else:f.seek(4 if kind==0 else words*4,1)
 lists=0
 for p in [0,1]:
  off=fields[f'd_riv_card_off[{p}]'];pos=fields[f'd_riv_card_pos[{p}]'];assert len(off)%53==0 and all(a<=b for a,b in zip(off,off[1:])) and off[-1]==len(pos)
  for slot in range(len(off)//53):
   for c in range(52):
    a,b=off[slot*53+c:slot*53+c+2];assert all(pos[k]<pos[k+1] for k in range(a,b-1));lists+=1
 frames.append({'fixture':row['fixture'],'all_strictly_sorted_card_lists':lists,'selected_fields':ids,'parent_wholeframe_identity':row['wholeframe_identity_from_prior_full_reader']})
h.save(D/'ordered-proof.json',{'at':h.now(),'abstract_ordered_addition_event_cases':checks,'includes_lb_gt_ub_empty_sparse_and_large_boundaries':True,'unsorted_counterexample_detected':True,'actual_retained_metadata_frames':frames,'source_precondition':'plan.rs appends pos from sorted.iter().enumerate() into by_card then concatenates each card list. Original d_riv_card_off/pos uploaded unchanged. Existing E089 direct oracle independently regenerates and verifies each of 36 geometries. Thus three walks use monotone positions; malformed unsorted tables are outside supported planner contract.','proof_scope':'Same ordered T/L/H addition events/operands for sorted integer positions only; no GPU/compiler/nonfinite/speed or universal memory safety proof. Requires real raw comparison before any timing.'})
S=ROOT/'runs/E097-source';S.mkdir(exist_ok=False);n='crates/solver/src/gpu/kernels.cu';b=(h.REPO/n).read_bytes();s=b.decode()
old='''            for (u32 t = c0; t < c1; t++) {
                u32 pos = card_pos_sh[t - card_base];
                float r = reach_sh[pos];
                tot_c += r;
                if (pos < lb) lower_c += r;
                else if (pos >= ub) higher_c += r;
            }'''
new='''            // Card positions are sorted. Keep every addition in its original
            // order, moving category tests to the two transition boundaries.
            u32 t = c0;
            for (; t < c1; t++) {
                u32 pos = card_pos_sh[t - card_base];
                if (pos >= lb) break;
                float r = reach_sh[pos];
                tot_c += r;
                lower_c += r;
            }
            for (; t < c1; t++) {
                u32 pos = card_pos_sh[t - card_base];
                if (pos >= ub) break;
                float r = reach_sh[pos];
                tot_c += r;
            }
            for (; t < c1; t++) {
                u32 pos = card_pos_sh[t - card_base];
                float r = reach_sh[pos];
                tot_c += r;
                higher_c += r;
            }'''
assert s.count(old)==1;s=s.replace(old,new);assert s.replace(new,old).encode()==b
(S/'baseline.cu').write_bytes(b);(S/'candidate.cu').write_bytes(s.encode());(S/'kernels.cu.patch').write_text(''.join(difflib.unified_diff(b.decode().splitlines(True),s.splitlines(True),fromfile='E080/kernels.cu',tofile='E097/kernels.cu')),encoding='utf-8')
h.save(S/'manifest.json',{'id':'E097','at':h.now(),'status':'STAGED_OFF_TREE_NOT_ACTIVATED','owned':{n:{'base':str(S/'baseline.cu'),'candidate':str(S/'candidate.cu'),'base_sha256':h.sha(S/'baseline.cu'),'candidate_sha256':h.sha(S/'candidate.cu')}},'accepted_source_sha256':h.custody(),'candidate_owned_sha256':{n:h.sha(S/'candidate.cu')},'tracked_owned_paths':[n],'new_owned_paths':[],'byte_exact_reverse':True})
h.save(S/'source-review.json',{'id':'E097','at':h.now(),'status':'source_only_pending_frozen_compiler_prerequisite','scope':'Only up_show card-correction inner walk becomes three monotone phases (lower/tied/higher). Same two cards, original positions and reach loads, total/lower/higher per-accumulator addition order and initial +0, all FP expressions, original cache/scan/barriers, ABI/host/worklist/launch/graph/allocation/quality/format retained. No pragma, cachehint, firstcardtotal, offsetcache or warp mapping changes.','hypothesis':'Avoid repeated lower/upper predicates within already classified sections. May add transition loads, extra loops, divergent control, register pressure or code size; no measured GPU branch cost/removable headroom or gain is claimed.','hard_prerequisites':'Other8entries alphaexact120/75; same27ABI and barriers; intended changed loop structure then independently inspect emitted branches/accumulator loops before real application kernels. D108 limits: no local/spill/dynamic increase, maxthreads nondecreasing, positive all shapes, defaults/stack. Disclose register/static/occupancy warning.','numeric_prerequisites':'Original1820pair sorted physical card/evaluator corpus including nonfinite/rounding witnesses, then entire physical canonical GPU/CPU and changing-root engine controls before samequality speed. Keep complete1%/strictfixture/fresh16/broad/material/holdout/freshoriginal/application gates.','closure':'Any genuine gate failure closes this phased walk without looplayout/phase/subset/threshold/source/flag/sample rescue. No gain accepted.'})
for folder,names in [(D,['history.json','ordered-proof.json']),(S,['manifest.json','source-review.json'])]:
 for name in names:
  p=folder/name;dst=h.ar.DASHBOARD/'evidence'/folder.name/name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+folder.name+'/'+name,timeout=20) as response:assert response.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=h.read(h.ar.STATUS);st['experiments'].append({'id':'D181','title':'Ordered card-correction source proof','kind':'diagnostic','status':'measured','accepted':False,'correctness':'finite_ordered_event_and_actual_metadata_proof_only','reason':str(checks)+' abstract ordered event cases plus all3 canonical metadata frames sorted; bounded sourcehistory no matching phased walk. No GPU/speed claim.','evidence':[{'label':'History and attribution','url':'evidence/'+D.name+'/history.json'},{'label':'Sorted metadata and ordered-event proof','url':'evidence/'+D.name+'/ordered-proof.json'}]});st['experiments'].append({'id':'E097','title':'Monotone card-correction phases','kind':'optimization','status':'running','accepted':False,'measurement_epoch':'RAM20261028','correctness':'pending_compiled_and_GPU_controls','stage':'Off-tree source staged; compiler gate next','reason':'Three sorted phases retain exact ordered additions. No speed result; may add divergent/control/resource cost.','evidence':[{'label':'Exact source scope and gates','url':'evidence/'+S.name+'/source-review.json'}]});st.update(updated_at=h.now(),active_experiment='E097',stage='Ordered card walk compiler preparation',activity='D180duplicateclosed; D181finiteorderproof/actualmetadata passed. E097offtreeonly; no new native. E080/16 remainsaccepted.');h.ar.atomic_json(h.ar.STATUS,st)
h.custody();print(json.dumps({'D181':'source_proof_pass','files':files,'unique_bodies':len(unique),'abstract_cases':checks,'metadata_lists':sum(x['all_strictly_sorted_card_lists'] for x in frames),'E097_source_sha256':h.sha(S/'candidate.cu')}),flush=True)
