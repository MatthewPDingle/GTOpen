"""Freeze the separate fresh16 confirmation before its first observation."""
from pathlib import Path
import ast,json,shutil,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3
PRIOR=R/'runs/E080-primary-plan';QP=R/'comparisons/E080-three-pair-comparison/report.json';QR=R/'comparisons/E080-root-crosscheck/report.json'
q=old.read(QP);cross=old.read(QR);assert q['decision']=='advance_to_separately_frozen_confirmation'and cross['status']=='pass_initial_timing_only'
assert q['performance']['primary_timing_pass']and q['exactness']=={'fixture_results':18,'convergence_records':138,'all_exact':True}
receipt=old.read(R/'runs/E080-primary-manager/primary.exit.json');assert receipt['returncode']==0 and receipt['error']is receipt['cleanup']is None
assert old.read(R/'runs/E080-primary-wrapper/complete.json')['all_children_terminal']
H=R/'runs/E080-confirmation-plan';assert not H.exists();H.mkdir();T=R/'runs/E051-confirmation-plan'
for name in['native.py','assess.py','root-check.py']:
    code=(T/name).read_text(encoding='utf-8').replace('E051','E080').replace('V051','V080').replace("HERE.parent/'small-gain-confirmation-plan'","HERE.parent/'accepted-E051-live-20261018'").replace("H.parent/'small-gain-confirmation-plan'","H.parent/'accepted-E051-live-20261018'").replace('import common as old','import common_e051_live as old').replace('old.exact_raw','old.historical.exact_raw')
    code=code.replace("P['gpu_control_report']","P['direct_control_report']").replace('gpu_control_report_sha256','direct_control_report_sha256')
    if name=='native.py':
        before="assert control['status']=='pass_scoped_up_action_raw_equivalence' and control['cases']==819 and control['full_raw_files_equal']"
        after="assert control['admit_one_integrated_trial'] and control['fixed_six_fresh_processes_complete'] and len(control['full_layout_raw_replays'])==18 and control['ability_lifecycle_controls']==12 and control['ability_predicate_controls']==15 and control['all_owned_children_terminal'] and control['source_main_live_PTX_custody_pass']"
        assert code.count(before)==1;code=code.replace(before,after).replace("[('84','0','4','0','0')]","[('86','0','4','0','0')]")
    assert 'small-gain-confirmation-plan'not in code and 'old.exact_raw'not in code
    ast.parse(code);(H/name).write_text(code,encoding='utf-8',newline='\n')
code=(R/'runs/E080-primary-plan/run.py').read_text(encoding='utf-8').replace('E080-primary-wrapper','E080-confirmation-wrapper').replace('E080-native-execution','E080-confirmation-execution').replace('E080-three-pair-comparison','E080-fresh16-confirmation').replace('E080-root-crosscheck','E080-fresh16-root-check').replace('fixed initial screen','fixed fresh16 confirmation');ast.parse(code);(H/'run.py').write_text(code,encoding='utf-8',newline='\n')
P=old.read(PRIOR/'protocol.json');pairs=[];order=[]
for i in range(16):
    b='B'+str(256+i);c='E080C'+str(i+1).zfill(2);which=['BC','CB','CB','BC'][i%4];pairs.append({'baseline':b,'candidate':c,'order':which});order.extend([b,c]if which=='BC'else[c,b])
P.update(id='E080-fresh16-confirmation',at=old.now(),status='FROZEN_PRE_FIRST_CONFIRMATION_OBSERVATION',control_ids=[],previously_terminal_unit_id='V080-unit',pairs=pairs,measurement_order=order,policy=old.read(T/'protocol.json')['policy'],scope='Separately frozen fresh16 warm-cache confirmation on RTX5090. Same source, binaries, quality, stopping rules, storage and fixtures. Initial timing samples are prerequisites only and are not scored or pooled. Aggregate >=1%, >=13 improving pairs, positive paired/block/order medians and no repeatable fixture slowdown. No exclusions, extensions, rescue samples or source variants.')
paths=[Path(__file__),R/'runs/E080-run-confirmation.py',*[H/n for n in['native.py','assess.py','root-check.py','run.py']],PRIOR/'protocol.json',QP,QR,R/'runs/E080-initial-closure/decision.json',R/'runs/E080-native-execution/complete.json',R/'runs/E080-native-execution/terminal.json',R/'runs/E080-primary-wrapper/complete.json',R/'runs/V080-unit/report.json',R/'runs/V080-unit/stdout.log']
P['input_sha256']=dict(P['input_sha256'])|{str(p):old.sha(p)for p in paths};st=old.read(old.ar.STATUS)
for identity in order:assert not(R/'runs'/identity).exists()and not any(x['id']==identity for x in st['experiments'])
for folder in['E080-confirmation-manager','E080-confirmation-wrapper','E080-confirmation-execution']:assert not(R/'runs'/folder).exists()
assert len(order)==len(set(order))==32 and sum(x['order']=='BC'for x in pairs)==8;old.save(H/'protocol.json',P)
published=[]
for src in[Path(__file__),R/'runs/E080-run-confirmation.py',*[p for p in H.iterdir()if p.is_file()]]:
    key=H.name+'/'+src.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(src,dst)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==src.read_bytes()
    published.append({'url':'evidence/'+key,'sha256':old.sha(src)})
old.save(H/'pre-native-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'protocol.json'),'HTTP_byte_verified_artifacts':published,'fresh_confirmation_samples':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E080')
    e.update(status='running',accepted=False,stage='Fresh 16-pair confirmation',reason='Initial three-pair gain is 2.483450%, with exact results and no fixture guard failure. The separate 16-pair protocol is frozen. Require at least 1% aggregate gain, 13 improving pairs, positive block/order medians and no repeatable fixture slowdown. Broader and material qualification still remain.')
    e['evidence'].append({'label':'Frozen fresh16 confirmation','url':'evidence/E080-confirmation-plan/protocol.json'})
    s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E080',stage='E080 fresh 16-pair confirmation',activity='Run exactly 32 fresh processes in balanced BC/CB order. Keep all observations; initial timings are not pooled. Accepted and live E051 remain unchanged at 12.44% cumulative gain.')
    old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'pairs':16,'fresh_processes':32,'initial_samples_pooled':0}),flush=True)
