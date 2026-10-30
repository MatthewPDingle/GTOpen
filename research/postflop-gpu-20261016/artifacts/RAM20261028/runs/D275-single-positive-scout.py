"""Bounded history and arithmetic contract for an unimplemented lead."""
import hashlib,json,re,shutil,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
H=ROOT/'runs/D275-single-positive-scout';H.mkdir(exist_ok=False);cuda=h.REPO/'crates/solver/src/gpu/kernels.cu';pattern=re.compile(r'one.?hot|positive_count|single.{0,35}positive|num_positive|\bnpos\b|npositive|one_positive',re.I)
path='crates/solver/src/gpu/kernels.cu';revisions=subprocess.check_output(['git','rev-list','--all','--',path],cwd=h.REPO,text=True).splitlines();history=[];retained=[];hits=[];unique=set()
def inspect(identity,data):
    digest=hashlib.sha256(data).hexdigest();text=data.decode('utf-8-sig',errors='replace');found=[{'line':i+1,'text':s.strip()}for i,s in enumerate(text.splitlines())if pattern.search(s)];row={'identity':identity,'sha256':digest,'literal_hits':found}
    if found:hits.append(row)
    return row
for revision in revisions:
    proc=subprocess.run(['git','show',revision+':'+path],cwd=h.REPO,stdout=subprocess.PIPE,stderr=subprocess.PIPE);assert proc.returncode==0;history.append(inspect('git:'+revision+':'+path,proc.stdout))
for directory in[ROOT/'runs',Path(r'S:\GTOpen-research\postflop-gpu-20261016\runs')]:
    for name in subprocess.check_output(['rg','--files',str(directory),'-g','*.cu'],text=True).splitlines():
        p=Path(name);assert p.stat().st_size<8*1024**2;data=p.read_bytes();unique.add(hashlib.sha256(data).hexdigest());retained.append(inspect(str(p),data))
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md';evidence=[]
for i,line in enumerate(ledger.read_text(encoding='utf-8').splitlines()):
    if re.search(r'D038|E028|E055|E091|D199|E019|E075|E099|E105',line):evidence.append({'line':i+1,'text':line})
ptx=ROOT/'runs/D207-resident-resource/baseline-compute_120.ptx';h.pin(ptx,'4457a101f35369c5d1d9893409e4bc8a9dc027fc4234e325b72c621f73017c12');text=ptx.read_text(encoding='utf-8')
entries={}
matches=list(re.finditer(r'\.visible \.entry\s+(\w+)\(',text))
for i,m in enumerate(matches):
    body=text[m.start():matches[i+1].start()if i+1<len(matches)else len(text)]
    if m.group(1)in['down_action','up_action']:entries[m.group(1)]={'div_rn_f32_instruction_count':len(re.findall(r'\bdiv\.rn\.f32\b',body)),'source_PTХ_sha256':h.sha(ptx)}
assert set(entries)=={'down_action','up_action'}and all(x['div_rn_f32_instruction_count']>0 for x in entries.values())
report={'id':'D275','at':h.now(),'status':'source_contract_only_not_an_admitted_candidate','previous_progress':'D274 original9fullSpot pairs/24error pairs exact;4.4857ms overlap effort proxy below100.521554ms constant, so tree/river overlap declined before prototype. E115 already closed; E080 remains live.',
 'bounded_history':{'local_CUDA_revisions':len(revisions),'history':history,'retained_CUDA_files':len(retained),'retained_unique_hashes':len(unique),'retained':retained,'literal_hits_for_manual_review':hits,'pattern':pattern.pattern,'limits':'Local refs and retained X/S CUDA only. Literal absence is not exhaustive semantic or remote novelty proof.'},
 'current_cuda_sha256':h.sha(cuda),'accepted_PTX':entries,
 'proposed_mathematical_case':'For one unlocked hand, exactly one regret is positive, original ascending f32 clamp-and-sum is finite and greater than1e-12. All other clamped terms are positive zero; the ordered sum is exactly the positive regret. Correctly rounded finite r/r is +1 and +0/r is +0. Existing parent-reach multiplication, sigma-times-child products, ordered expectations, strategy FMA and regret updates must all still execute in original order. No skip-zero-output or multiplication omission is justified, including NaN/infinite own reach/child values. Preserve original normal/zero/nonfinite-sum fallback and lock path.',
 'scope_not_yet_selected':'Potential normalization division bypass inside original down_action and training up_action helpers only. Must not add persistent sigma cache, new payload/entry/host flag/launch/graph/cadence/arity/quality change. No source form exists yet. Extra predicate/count/branch/register cost may erase any gain or regress mixed strategies.',
 'closed_families_not_retried':['E019 fold warp-tail/barrier reduction; identified prior exact mechanism and declined before code.','E028 actor1 persistent probability cache and cross-sweep reuse; this lead proposes no retained cache or lifetime change.','E091 zero-own-reach output shortcut; this lead uses regret distribution and retains every original multiplication/output arithmetic, including zero reach.','D199 fmax clamp spelling already emits the same maximum; this lead does not change clamp spelling.','E105 evaluation arity specialization, E099 paired hands, E075 uniform metadata loads and E055 discount scheduling remain closed; no hunk composed.'],
 'ledger_counterevidence':evidence,
 'next_required_before_source':'Classify all literal hits. Freeze read-only census of every canonical retained baseline converged/continued/locked/resumed state, all active unlocked node-hand regrets and exact finite-sum/threshold conditions. These endpoint snapshots are not per-iteration incidence, executed division counts, measured time or headroom. Then freeze one source/resource/raw-IEEE oracle form only if justified. Actual CUDA exceptional values/NaN payload/signed-zero/subnormal/overflow/menu/locks/tails, original full engine/canonical exactness and full ordinary complete1%/strictfixture/fresh16/broad/material/holdout/cumulative/application gates remain mandatory.',
 'new_compilers_GPU_CFR_solver_or_speed_samples':0,'source_candidate_created':False,'accepted_main_live_protected_PTX_unchanged':True,'goal_active':True,'last_primary_baseline':'B362','next_unused_baseline':'B363'}
h.save(H/'report.json',report);h.custody();print(json.dumps({'revisions':len(revisions),'retained':len(retained),'unique':len(unique),'literal_hit_files':len(hits),'PTX':entries,'source_candidate_created':False}),flush=True)
