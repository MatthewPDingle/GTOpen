"""History and integer ownership proof for two ordered chance accumulators."""
import hashlib,json,re,struct,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists();O=ROOT/'runs/D260-paired-chance-scout';O.mkdir(exist_ok=False);history=[];matches=[];hashes=set()
def bodies(data):
 text=data.decode('utf-8-sig');out=[]
 for m in re.finditer(r'\bvoid\s+(\w*up_chance\w*)\s*\([^{};]*\)\s*\{',text,re.S):
  start=m.end()-1;i=start+1;depth=1
  while depth:
   depth+=(text[i]=='{')-(text[i]=='}');i+=1
  out.append((m.group(1),text[start:i]))
 return out
def inspect(identity,data):
 findings=[]
 for name,body in bodies(data):
  acc=sorted(set(re.findall(r'\b(acc\w*)\s*\+=',body)));paired=bool(re.search(r'\+=\s*(?:2\s*\*[^;\n]*blockDim|blockDim[^;\n]*\*\s*2)',body));findings.append({'function':name,'additive_accumulators':acc,'explicit_two_block_hand_stride':paired,'body_sha256':hashlib.sha256(body.encode()).hexdigest()})
  if len(acc)>1 or paired:matches.append({'identity':identity,'function':name,'accumulators':acc,'paired_stride':paired})
 digest=hashlib.sha256(data).hexdigest();history.append({'identity':identity,'sha256':digest,'bytes':len(data),'chance_functions':findings});hashes.add(digest)
revisions=subprocess.check_output(['git','rev-list','--all','--','crates/solver/src/gpu/kernels.cu'],cwd=h.REPO,text=True).splitlines()
for revision in revisions:
 x=subprocess.run(['git','show',revision+':crates/solver/src/gpu/kernels.cu'],cwd=h.REPO,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 if x.returncode:history.append({'identity':'git:'+revision,'absent_path':True});continue
 inspect('git:'+revision,x.stdout)
files=[]
for root in [ROOT/'runs',Path(r'S:\GTOpen-research\postflop-gpu-20261016')/'runs',h.REPO/'research/autoresearch']:
 for name in subprocess.check_output(['rg','--files',str(root),'-g','*.cu'],text=True).splitlines():
  p=Path(name);assert p.drive.upper()in['X:','S:']and p.stat().st_size<=4*1024**2;files.append(p);inspect(str(p),p.read_bytes())
h.save(O/'history.json',{'at':h.now(),'local_ref_revisions':len(revisions),'retained_CUDA_files':len(files),'unique_CUDA_hashes':len(hashes),'matching_multiaccumulator_chance_forms':matches,'history':history,'scope':'Bounded retained-CUDA and local tracked path history only; not exhaustive remote or semantic novelty proof.'});assert not matches,matches
# Complete count/bounds algebra for every legal hand count and hardware width.
# Inverse map is unique: q=i//w, lane=i%w, batch=q//2, role=q%2.
# Candidate base=lane+2*w*batch; role1 is base+w, exactly recovering i.
records=0;edge_cases=0;hand_checks=0;digest=hashlib.sha256()
with(O/'ownership.bin').open('xb')as f:
 f.write(b'D260-HAND-MAP1\0\0')
 for width in range(1,1025):
  critical={0,1,1325,1326}
  for n in [width-1,width,width+1,2*width-1,2*width,2*width+1,3*width-1,3*width,3*width+1]:
   if 0<=n<=1326:critical.add(n)
  for nh in range(1327):
   cycles,tail=divmod(nh,2*width);first=cycles*width+min(tail,width);second=cycles*width+max(tail-width,0);assert first+second==nh and 0<=second<=first;last=nh-1
   if nh:
    q,lane=divmod(last,width);batch,role=divmod(q,2);base=lane+2*width*batch;assert base+role*width==last and base<nh and(role==0 or base+width<nh)
   data=struct.pack('<6I',nh,width,first,second,cycles,tail);f.write(data);digest.update(data);records+=1
   if nh in critical:
    got=[]
    for lane in range(width):
     for base in range(lane,nh,2*width):
      got.append(base)
      if base+width<nh:got.append(base+width)
    assert sorted(got)==list(range(nh));assert len(got)==len(set(got));edge_cases+=1;hand_checks+=nh
assert records==1358848
h.save(O/'report.json',{'id':'D260','at':h.now(),'status':'pass_source_history_and_integer_ownership_only','accepted_CUDA_sha256':h.sha(h.REPO/'crates/solver/src/gpu/kernels.cu'),'history_sha256':h.sha(O/'history.json'),'local_ref_revisions':len(revisions),'retained_CUDA_files':len(files),'unique_CUDA_hashes':len(hashes),'matching_multiaccumulator_chance_forms':matches,'all_count_width_records':records,'enumerated_boundary_shapes':edge_cases,'enumerated_hand_indices':hand_checks,'raw_ownership_sha256':h.sha(O/'ownership.bin'),'raw_ownership_bytes':(O/'ownership.bin').stat().st_size,'record_stream_sha256':digest.hexdigest(),'fixed_next_form':'Only up_chance: two striped hands i0 and i0+blockDim.x per thread, stride2*blockDim.x, one ascending original card loop with two independent positive-zero accumulators. Load immutable mask/permutation/childCFVbase once when either hand is live. Preserve per-hand original membership/perm index, ordered additions, final multiply and all stores; tail second hand has no loads/stores. Minimum independent pair, not an adjacent float2 vector instruction or shared table/barrier.','dependency_contract':'Production chance outputs are unique parent rows and read completed child rows at next depth. Pairing changes hand scheduling only; all logical per-hand indices/addresses and ordered card contributions remain. Actual per-level input/output ownership and full numerical/raw tests still mandatory.','closed_forms_declined':['Action sorting overlaps E056; alternative ordering key/scope is not admitted.','Chance child-to-slot translation overlaps E018/E039 and earlier explicit declines; not admitted.'],'closed_forms_not_composed':['E039 shared chance metadata','E046 interleaved chance record','E048/E086 membership rewrite','E099 adjacent-hand vector action memory','E102 downward parent fanout','E112 constant discounts','E113 writable qualifiers'],'risks':['Two accumulators may increase registers/spills or reduce residency.','Additional hand predicates may cost more than private metadata reuse saves.','Within-CFV parent/child disjointness must remain explicit; this proof does not establish GPU math or speed.'],'next_required':'Exact off-tree source, original ABI/resources and emitted same-card metadata reuse/two recurrence mechanism before application kernels. All original raw/ordinary/complete1%/strictfixture/fresh16/broad/material/holdout/cumulative/app gates remain. Fixed form closes without hand-count/width/tile/predicate/field/loop/helper/flags/source/sample rescue after genuine failure.','compilers':0,'application_kernels':0,'source_activated':False,'performance_samples':0,'goal_active':True,'all_new_bulk_X_S_read_only_no_T_access':True});h.custody();print(json.dumps({'records':records,'boundary_shapes':edge_cases,'enumerated_indices':hand_checks,'retained_CUDA':len(files),'status':'pass_integer_and_source_only'}),flush=True)
