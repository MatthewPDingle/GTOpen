"""Bounded history/source-only review; stage one exact form without activation."""
import sys,json,re,shutil,difflib,subprocess,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists();H=ROOT/'runs/D143-zero-reach-source';H.mkdir(exist_ok=False)
history=Path(r'S:\GTOpen-research\postflop-gpu-20261016\runs\D140-serial-card-loop\history.json');old=h.read(history);catalog=old['retained_up_show_sources'];assert len(catalog)==400
def body(code,marker):
 at=code.index(marker);start=code.index('{',at);level=0
 for i in range(start,len(code)):
  if code[i]=='{':level+=1
  elif code[i]=='}':
   level-=1
   if level==0:return code[at:i+1]
 raise AssertionError('unterminated function')
inventory=[];hits=[]
for item in catalog:
 p=Path(item['path']);h.pin(p,item['sha256']);code=p.read_text(encoding='utf-8-sig')
 marker='void down_action_impl('if'void down_action_impl('in code else'void down_action('
 t=body(code,marker);patterns=re.findall(r'(?:pr\s*(?:==|!=)\s*0(?:\.f?)?|isfinite\s*\(\s*(?:pr|sum)\s*\)|__all_sync)',t)
 inventory.append({'path':str(p),'sha256':item['sha256'],'function':marker,'matches':patterns})
 if patterns:hits.append(inventory[-1])
commands=[]
for cmd in[['git','log','--all','--format=%h %s','-G',r'pr[[:space:]]*==[[:space:]]*0|parent_reach.*==|isfinite\(sum\)','--','crates/solver/src/gpu/kernels.cu'],['rg','-n','-i',r'zero.{0,45}reach|reach.{0,45}zero|early.{0,30}reach|pr\s*==\s*0|zero-reach|dead.hand','research/postflop-gpu-20261016/experiments.md']]:
 d=h.ar.read_command(cmd,60);assert d.get('returncode')in[0,1];commands.append(d)
assert not hits,'Existing matching zero-reach body requires review before staging'
n='crates/solver/src/gpu/kernels.cu';base=(h.REPO/n).read_bytes();txt=base.decode('utf-8');nl='\r\n'if b'\r\n'in base else'\n';normal=txt.replace('\r\n','\n')
before='''        float pr = parent_reach[i];
        float uni = pr / (float)na;'''
after='''        float pr = parent_reach[i];
        // Keep the signed zero while avoiding per-action normalization.
        // Nonfinite positive-regret sums retain the original path.
        if (pr == 0.f && isfinite(sum)) {
            for (int a = 0; a < na; a++) {
                u32 child = children[cs + a];
                reach_a[(u64)(actor == 0 ? rsrc0[child] : rsrc1[child]) * nh_a + i] = pr;
            }
            continue;
        }
        float uni = pr / (float)na;'''
assert normal.count(before)==1;candidate=normal.replace(before,after);assert candidate.replace(after,before)==normal
S=ROOT/'runs/E091-source';S.mkdir(exist_ok=False);(S/'baseline.cu').write_bytes(base);(S/'candidate.cu').write_bytes(candidate.replace('\n',nl).encode())
(S/'kernels.cu.patch').write_text(''.join(difflib.unified_diff(normal.splitlines(True),candidate.splitlines(True),fromfile='accepted-E080/kernels.cu',tofile='E091/kernels.cu')),encoding='utf-8',newline='\n')
proof={
 'mechanism':'Unlocked down_action only: after the unchanged ordered positive-regret sum and parent reach load, signed-zero reach plus finite sum writes that same signed zero in unchanged action order, then continues. All other inputs retain the original implementation.',
 'finite_sum_positive_case':'When sum>1e-12 and finite, every selected positive regret is finite and no greater than the accumulated nonnegative sum. The existing division returns a finite nonnegative value including positive zero. Multiplication by either signed zero returns that same signed zero. NaN/negative regrets select positive zero. This is source case analysis, not a device numerical result.',
 'finite_sum_fallback_case':'When the original sum comparison is false and sum finite, the existing uniform path divides signed zero by the positive action count, preserving its sign. The staged path stores the original pr bits. Ordered sum and all address calculations are retained.',
 'nonfinite_sum_case':'The isfinite guard is false for a nonfinite sum; all original operations execute. Infinity-producing sums are not silently short-circuited.',
 'locked_case':'Locked branch, sigma multiplication and return precede the edited region and are byte unchanged. Arbitrary signed/nonfinite lock inputs are not short-circuited.',
 'scope_unchanged':['up/evaluation kernels','all regret sums and their ordering','learning arrays and strategy updates','node IDs, pitches, allocation and budget','host/ABI/launch shape/graph schedule','precision and quality thresholds','save/load/continuation behavior'],
 'distinction_from_closed_forms':'E035 and E036 inspect whole terminal opponent-reach CTAs with reductions/guards; this is per-hand own reach in down_action after the existing sum. No terminal early-return, quotient/reciprocal rewrite, scratch-stride hunk or E090 rescue is composed.',
 'required_next':'Finite CUDA raw comparisons must include signed-zero, small/subnormal/large and nonfinite regrets, overflow sums, both actor orientations, locked inputs, generic and common action counts, tails and full input/output guards. Fresh production incidence and compiled resource checks should precede a complete-cycle speed screen. No numerical, resource or speed pass is inferred from source analysis.'}
h.save(H/'history.json',{'at':h.now(),'catalog_path':str(history),'catalog_sha256':h.sha(history),'retained_sources':inventory,'matching_bodies':hits,'local_history_and_ledger':commands,'scope':'400 cataloged retained down_action bodies and current all-local-ref/ledger. Read-only S archive; new artifacts X. Bounded textual novelty only, not exhaustive semantic/remote history.'})
h.save(S/'source-review.json',{'id':'E091','at':h.now(),'status':'staged_source_only','source_case_analysis':proof,'old_E090_remains_closed':True,'production_source_activated':False,'GPU_or_compiler_children':0,'numerical_equivalence_established':False,'speed_gain_established':False,'history_sha256':h.sha(H/'history.json')})
h.save(S/'manifest.json',{'id':'E091','at':h.now(),'accepted_source_sha256':h.custody(),'owned':{n:{'base':str(S/'baseline.cu'),'candidate':str(S/'candidate.cu')}},'candidate_owned_sha256':{n:h.sha(S/'candidate.cu')},'source_review_sha256':h.sha(S/'source-review.json'),'patch_sha256':h.sha(S/'kernels.cu.patch'),'script_sha256':h.sha(__file__),'source_reversal_exact':True,'all_output_physical_X':True,'candidate_accepted':False})
pub=[]
for folder in[H,S]:
 for p in folder.iterdir():
  key=folder.name+'/'+p.name;dst=h.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
  pub.append(key)
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS)
 for ident in['D143','E091']:assert not any(x['id']==ident for x in s['experiments'])
 s['experiments'].extend([{'id':'D143','title':'Zero-reach action-path source and history review','kind':'diagnostic','status':'measured','accepted':False,'stage':'Bounded source review complete','correctness':'source_only','reason':'No matching shortcut found in 400 retained down-action bodies or the bounded local history. A source case analysis supports one staged form; device correctness and speed remain unproven.','measurement_epoch':'RAM20261028','evidence':[{'label':'Bounded history review','url':'evidence/D143-zero-reach-source/history.json'}]},{'id':'E091','title':'Skip normalization for signed-zero own reach','kind':'candidate','status':'staged','accepted':False,'correctness':'not_run','stage':'Raw GPU controls pending','measurement_epoch':'RAM20261028','reason':'One unlocked down-action shortcut is staged. The original ordered sum still runs; nonfinite sums and locked policies retain their original path. No source activation, device controls, compiled resource result or speed measurements yet.','evidence':[{'label':'Staged source and exact scope','url':'evidence/E091-source/source-review.json'},{'label':'One-form source manifest','url':'evidence/E091-source/manifest.json'}]}])
 s.update(updated_at=h.now(),active_experiment='E091',stage='E091 raw-control preparation',activity='E080 remains live with the fresh 10.4564 s baseline. E090 was rejected. Fresh profiling and a 400-source history review led to a staged zero-reach action shortcut; GPU correctness and speed are unproven.');h.ar.atomic_json(h.ar.STATUS,s)
h.save(H/'publication.json',{'at':h.now(),'HTTP_verified_artifacts':pub,'owned_native_children':0,'accepted_source_main_live_PTX_custody_pass':True})
h.custody();print(json.dumps({'source_only':True,'historical_bodies':len(inventory),'matching_bodies':len(hits),'candidate_sha256':h.sha(S/'candidate.cu'),'GPU_or_compiler_children':0}),flush=True)
