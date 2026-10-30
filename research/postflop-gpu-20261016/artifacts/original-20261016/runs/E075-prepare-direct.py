"""Freeze fresh full-array up_action controls using the same sealed LDU PTX."""
from pathlib import Path
import ast,json,shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3
RES=R/'runs/E075-resource';P0=old.read(RES/'protocol.json');q=old.read(RES/'report.json');assert q['status']=='pass_compiled_uniform_load_prerequisites'and all(q['gates'].values())and q['all_owned_children_terminal']and q['application_kernel_launches']==0
for p,h in P0['input_sha256'].items():old.pin(p,h)
for label in ['rustc','probe','baseline-capture','candidate-capture','baseline-sass-json','candidate-sass-json']:
 e=old.read(RES/'execution'/(label+'.exit.json'));assert e['returncode']==0 and e['error']is e['cleanup']is None
assert q['baseline']['registers']==62 and q['candidate']['registers']==56 and q['baseline']['local_bytes_per_thread']==q['candidate']['local_bytes_per_thread']==64
H=R/'runs/E075-kernel-control';prior=R/'runs/E054-kernel-control';S=R/'runs/E075-source';assert not H.exists();H.mkdir()
for arm in ['baseline','candidate']:
 p=RES/'execution'/(arm+'-compute_120.ptx');old.pin(p,q['ptx_sha256'][arm+'-compute_120']);shutil.copyfile(p,H/(arm+'.ptx'))
(H/'discounts.rs').write_bytes((prior/'discounts.rs').read_bytes())
probe=(prior/'probe.rs').read_text(encoding='utf-8').replace('E054','E075');(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
for name in ['execute.py','audit.py']:
 code=(prior/name).read_text(encoding='utf-8').replace('E054','E075').replace("HERE.parent/'accepted-E051'","HERE.parent/'accepted-E051-live-20261018'").replace('import common_e051 as old','import common_e051_live as old')
 if name=='execute.py':
  assert code.count("'pass_resource_feasibility_only'")==1;code=code.replace("'pass_resource_feasibility_only'","'pass_compiled_uniform_load_prerequisites'").replace('>=54*1024**3','>=66*1024**3')
 ast.parse(code);(H/name).write_text(code,encoding='utf-8',newline='\n')
corpus=old.read(prior/'corpus.json');assert len(corpus['cases'])==819
corpus.update(id='E075-up-action-corpus',at=old.now(),changed_path_cases=sum(c['count']>0 for c in corpus['cases']),source_corpus_sha256=old.sha(prior/'corpus.json'),adaptation='Only ID/time/changed-path metadata updated for new load scope. All819case descriptors/order/values/discount bits unchanged. No added/dropped cases or historical timing samples.')
assert corpus['changed_path_cases']==807;old.save(H/'corpus.json',corpus)
old.save(H/'source-review.json',{'id':'E075-direct-review','at':old.now(),'status':'source_and_full_raw_control_plan_review_pass','resource_report_sha256':old.sha(RES/'report.json'),'source_review_sha256':old.sha(S/'source-review.json'),'case_count':819,'kernel_launches':1638,'actually_changed_metadata_cases':807,'source_floating_recurrences_unchanged':True,'uniformity_contract':'Every transformed pointer is nodes+start+blockIdx or immutablearray+n. The node and every n-based address remain CTAconstant across hand-loop tails, thread widths1/32/64/128/256, allactor/lock/generic paths and independently scheduled threads. No per-hand/action-indexed value or mutable data loadedwithLDU.','corpus':'Exact E054/E051819case descriptors: bothplayers/DCFR/CFR+,own/locked/opponent,arities1/2/3/4/5/8/9/16/17,hands0..1326/tails,countzero/excessgrid,finite/signedzero/subnormal/quietNaN/infinity/finite-overflow profiles. Full3mutable outputs/12actual immutable buffers/guards and actual mutable-range/parent-child disjointness witnesses.','limits':'Bounded declared corpus, not universal NaNpayload/illegalalias/wide-address proof. Rootdecoder is not external independent audit. No performance/state/save/resume/capacity/material conclusion. All integrated/broad/performance gates remain required.'})
oldP=old.read(prior/'protocol.json');deps={p:h for p,h in oldP['input_sha256'].items()if Path(p).suffix in ['.rlib','.lib']}
for p,h in deps.items():old.pin(p,h)
paths=[Path(__file__),R/'runs/E075-run-direct.py',*[p for p in H.iterdir()if p.is_file()],*[p for p in S.iterdir()if p.is_file()],RES/'protocol.json',RES/'report.json',R/'runs/D121-uniform-node-reads/protocol.json',C/'common_e051_live.py',C/'protected-main.json',old.REPO/'crates/solver/src/cfr.rs',old.REPO/'crates/solver/src/gpu/plan.rs',old.REPO/'crates/solver/src/gpu/mod.rs',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md']
P={'id':'E075-kernel-control','at':old.now(),'status':'FROZEN_PRE_FIRST_NUMERICAL_LAUNCH','rustc_command':[x.replace(str(prior),str(H))for x in oldP['rustc_command']],'input_sha256':deps|{str(p):old.sha(p)for p in paths},'resource_report':str(RES/'report.json'),'raw_output':str(H/'evidence'),'expected_cases':819,'expected_launches':1638,'sealed_PTX_sha256':{arm:old.sha(H/(arm+'.ptx'))for arm in ['baseline','candidate']},'scope':'One Rustcompile, one819pair/1638launch native process using exact saved resourcePTX(noNVRTC). All819rawinput/state/guard cases retained. Then one separate raw decoder. No numerical retries/extensions/source/load/helper/width/placement/cache variants after failure, no performance samples.','candidate_accepted':False};old.save(H/'protocol.json',P)
def publish(p,key):
 dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==p.read_bytes()
 else:shutil.copyfile(p,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
 return {'url':'evidence/'+key,'sha256':old.sha(p)}
pub=[publish(p,H.name+'/'+p.name)for p in H.iterdir()if p.is_file()];pub.append(publish(Path(__file__),H.name+'/prepare.py'));old.save(H/'pre-execution-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'protocol.json'),'HTTP_byte_verified_artifacts':pub,'compiler_or_numerical_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E075');e.update(stage='819 full raw GPU case pairs',reason='Actual codegen changed and registers62to56,local64unchanged,128threadresidency8to9. Same sealed PTXnow enters fixed819pair full-array controls, including actual immutable metadata and guards. No speed result.');e['evidence'].append({'label':'Frozen complete raw action controls','url':'evidence/E075-kernel-control/protocol.json'});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E075',stage='E075 full raw numerical controls',activity='Exactly819fresh original/candidate action pairs,1638launches; full mutable/immutable input/output/guard byte equality and range witnesses. No NVRTC rerun or solver speed result. Accepted/live E051gain12.44%unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'cases':819,'launches':1638,'changed_metadata_cases':807,'numerical_executions':0}),flush=True)
