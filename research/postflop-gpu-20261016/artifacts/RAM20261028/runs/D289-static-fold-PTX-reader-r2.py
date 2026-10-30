import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D289-static-fold-PTX';R=ROOT/'runs/E119-resource'
def inspect(t):
 m=re.search(r'mov\.u32\s+(%r\d+), %ntid\.x;\s+setp\.eq\.s32\s+(%p\d+), \1, 128;\s+@\2 bra\s+(\$L__BB\d+_\d+);',t);assert m
 fast=m[3];a=t.index(fast+':');end=re.search(r'\n(\$L__BB\d+_\d+):\s+ld\.shared\.f32\s+%f\d+, \[_ZZ7up_foldE11total_parts\];',t[a:]);assert end;join=end[1];region=t[a:a+end.start()]
 own=re.search(r'mul\.wide\.u32\s+(%rd\d+), (%r\d+), 4;\s+mov\.u64\s+(%rd\d+), _ZZ7up_foldE11total_parts;\s+add\.s64\s+(%rd\d+), \3, \1;\s+st\.shared\.f32',t);assert own;tid=own[2];base=own[4]
 assert re.search(r'mov\.u32\s+'+re.escape(tid)+r', %tid\.x;',t[:own.start()])
 barriers=list(re.finditer(r'bar\.sync\s+0;',region));assert len(barriers)==7 and region.count('add.f32')==7 and region.count('ld.shared.f32')==14 and region.count('st.shared.f32')==7 and 'shr.'not in region
 prior=0;phases=[]
 for step,bar in zip([64,32,16,8,4,2,1],barriers):
  part=region[prior:bar.end()];prior=bar.end()
  guard=(r'setp\.gt\.u32\s+(%p\d+), '+re.escape(tid)+', '+str(step-1)+r';'if step>1 else r'setp\.ne\.s32\s+(%p\d+), '+re.escape(tid)+r', 0;')
  g=re.search(guard,part);assert g and re.search('@'+re.escape(g[1])+r' bra\s+(\$L__BB\d+_\d+);',part)
  pointer=re.escape(base)+(r'\+'+str(step*4)if step>1 else '')
  if step>1:loads=re.search(r'ld\.shared\.f32\s+(%f\d+), \['+pointer+r'\];\s+ld\.shared\.f32\s+(%f\d+), \['+re.escape(base)+r'\];\s+add\.f32\s+(%f\d+), \1, \2;\s+st\.shared\.f32\s+\['+re.escape(base)+r'\], \3;',part)
  else:loads=re.search(r'ld\.shared\.f32\s+(%f\d+), \[_ZZ7up_foldE11total_parts\+4\];\s+ld\.shared\.f32\s+(%f\d+), \[_ZZ7up_foldE11total_parts\];\s+add\.f32\s+(%f\d+), \1, \2;\s+st\.shared\.f32\s+\[_ZZ7up_foldE11total_parts\], \3;',part)
  assert loads;phases.append({'step':step,'byte_offset':4*step,'same_thread_guard_and_two_ordered_loads_ADD_store_then_CTAbarrier':True})
 generic=t[m.end():a];assert generic.count('bar.sync')==1 and generic.count('add.f32')==1 and generic.count('shr.u32')==1 and re.search(r'bra\.uni\s+'+re.escape(join)+r';',generic)
 assert not any(x in region for x in ['shfl.','ld.global','st.global','mul.f32','sub.f32','fma.'])
 return{'uniform_default128_branch':m.group(),'generic_fallback_region':generic,'fast_steps':phases,'fast_barriers':7,'fast_shared_FP_adds':7,'shared_own_pointer':base,'thread_register':tid,'common_join':join,'limits':'Scoped exactPTXpattern/operand/control witness, not arbitrary CFG/interpreter/native/IEEE or performance proof. Originalgenericbody/source and CPU256width dependency model remain mandatory; direct actualGPU originalcorpus next.'}
if len(sys.argv)==1:
 h.custody();H.mkdir(exist_ok=False);q=h.read(R/'report.json');assert all(q['gates'].values());files=[Path(__file__),R/'report.json',ROOT/'runs/E119-source/manifest.json',ROOT/'runs/D288-static-fold-scout/dependency-model.json',R/'execution/candidate-compute_120-up_fold.ptx.txt',R/'execution/baseline-compute_120-up_fold.ptx.txt']
 h.save(H/'reader-protocol-r2.json',{'id':'D289','at':h.now(),'status':'FROZEN_PRE_STATIC_PTX_READER','input_sha256':{str(p):h.sha(p)for p in files},'requirements':'Actualntid==128 selection,7fixed64..1same-pairsharedADD/store phases andall7CTAbarriers,unchangedgenericshrloopandcommonpayoutjoin. No shuffle/globalmemory/extraFPoperations infastladder. Wrongstep/missingbarrier/defaultwidth/mismatchedADDnegativefixtures. No applicationkernel/speed/sourcevariant.'});print(h.sha(H/'reader-protocol-r2.json'),flush=True);sys.exit(0)
assert len(sys.argv)==2;h.pin(H/'reader-protocol-r2.json',sys.argv[1]);P=h.read(H/'reader-protocol-r2.json');h.custody()
for p,d in P['input_sha256'].items():h.pin(p,d)
t=(R/'execution/candidate-compute_120-up_fold.ptx.txt').read_text(encoding='utf-8');w=inspect(t);negative=[]
for name,old,new in [('wrong_offset','+256]','+252]'),('wrong_defaultwidth',', 128;',', 64;'),('missing_barrier','$L__BB3_34:\n\tbar.sync \t0;','$L__BB3_34:\n\t//removedbarrier;'),('wrong_ADD_operand','%f95, %f93, %f94','%f95, %f93, %f93')]:
 assert old in t;bad=t.replace(old,new,1)
 try:inspect(bad)
 except AssertionError:negative.append(name)
 else:raise AssertionError('negativefixtureaccepted '+name)
h.save(H/'report.json',{'id':'D289','at':h.now(),'status':'pass_scoped_default128_static7phase_PTX_ladder','protocol_sha256':sys.argv[1],'witness':w,'negative_reader_fixtures':negative,'new_compiler_GPU_kernel_solver_or_speed_samples':0,'candidate_accepted':False});h.custody();print('D289 scoped128branch/7originalsharedADD+barriers/genericfallback pass.',flush=True)
