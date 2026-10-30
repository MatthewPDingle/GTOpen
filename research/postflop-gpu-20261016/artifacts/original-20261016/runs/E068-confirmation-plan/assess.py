import datetime,json,math,statistics,sys
from pathlib import Path
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'accepted-E051'));import common_e051 as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
old.custody();assert not (old.ROOT/'gpu-run.lock').exists()
E=old.ROOT/'runs/E068-confirmation-execution';done=old.read(E/'complete.json');terminal=old.read(E/'terminal.json')
assert terminal['returncode']==0 and terminal['complete_sha256']==old.sha(E/'complete.json')
assert done['protocol_sha256']==sys.argv[1] and done['measurement_order']==P['measurement_order']
assert done['fixture_results']==96 and done['convergence_records']==736
anchor=old.historical.exact_raw('E020C1');runs={};pins={};last=None;environment=None;gpu=None
for identity in P['measurement_order']:
 receipt=old.read(E/(identity+'.exit.json'));assert receipt['returncode']==0 and receipt['error'] is receipt['cleanup'] is None
 start=datetime.datetime.fromisoformat(receipt['started_at']);end=datetime.datetime.fromisoformat(receipt['finished_at']);assert start<=end and (last is None or last<=start);last=end
 r=old.read(old.ROOT/'runs'/identity/'report.json');assert r['returncode']==0 and r['status']=='measured'
 assert r['provenance']['source_sha256']==old.BASE
 ns=datetime.datetime.fromisoformat(r['started_at'].replace('Z','+00:00'));ne=datetime.datetime.fromisoformat(r['finished_at'].replace('Z','+00:00'));assert start.replace(microsecond=0)<=ns<=ne<=end
 old.compare.validate_run(r,pins);assert old.historical.exact_raw(identity)==anchor
 if environment is None:environment=r['environment'];gpu=old.compare.gpu_identity(r)
 assert r['environment']==environment and old.compare.gpu_identity(r)==gpu
 runs[identity]=r
 for path in [old.ROOT/'runs'/identity/'report.json',old.ROOT/'runs'/identity/'stdout.log',E/(identity+'.exit.json')]:pins[str(path)]=old.sha(path)
fixtures=[]
for i,name in enumerate(['rainbow','two-tone','river']):
 b=[runs[p['baseline']]['results'][i]['full_cycle_ms'] for p in P['pairs']];c=[runs[p['candidate']]['results'][i]['full_cycle_ms'] for p in P['pairs']]
 assert len(b)==len(c)==16
 bm,cm=statistics.median(b),statistics.median(c);slower=sum(y>x for x,y in zip(b,c));fail=cm>bm and slower>=9
 fixtures.append({'fixture_id':name,'baseline_ms':b,'candidate_ms':c,'baseline_median_ms':bm,'candidate_median_ms':cm,'gain_pct':100*(bm-cm)/bm,'paired_slowdown_pct':[100*(y-x)/x for x,y in zip(b,c)],'slower_pairs':slower,'fixture_guard_failed':fail})
bs=math.fsum(f['baseline_median_ms'] for f in fixtures);cs=math.fsum(f['candidate_median_ms'] for f in fixtures);gain=100*(bs-cs)/bs
pairs=[]
for i,p in enumerate(P['pairs']):
 b=math.fsum(x['full_cycle_ms'] for x in runs[p['baseline']]['results']);c=math.fsum(x['full_cycle_ms'] for x in runs[p['candidate']]['results'])
 pairs.append({'pair':i+1,'baseline':p['baseline'],'candidate':p['candidate'],'order':p['order'],'baseline_sum_ms':b,'candidate_sum_ms':c,'gain_pct':100*(b-c)/b})
positive=sum(x['gain_pct']>0 for x in pairs);median=statistics.median(x['gain_pct'] for x in pairs)
blocks=[statistics.median(x['gain_pct'] for x in pairs[i:i+4]) for i in range(0,16,4)]
strata={order:statistics.median(x['gain_pct'] for x in pairs if x['order']==order) for order in ['BC','CB']}
gates={'aggregate_at_least1pct':gain>=1,'at_least13_positive_pairs':positive>=13,'positive_pair_median':median>0,'all4block_medians_positive':all(x>0 for x in blocks),'both_order_strata_positive':all(x>0 for x in strata.values()),'no_fixture_regression':not any(x['fixture_guard_failed'] for x in fixtures),'all96results_736checkpoints_exact':True}
passed=all(gates.values());O=old.ROOT/'comparisons/E068-fresh16-confirmation';O.mkdir()
report={'id':'E068-fresh16-confirmation','at':old.now(),'protocol_sha256':sys.argv[1],'status':'pass_fresh16_timing_only' if passed else 'rejected','decision':'advance_to_broader_qualification_only' if passed else 'rejected','candidate_accepted':False,'performance':{'baseline_full_cycle_ms':bs,'candidate_full_cycle_ms':cs,'observed_gain_pct':gain,'required_gain_pct':1,'positive_pairs':positive,'required_positive_pairs':13,'pair_median_gain_pct':median,'block_median_gains_pct':blocks,'order_strata_median_gains_pct':strata,'fresh_confirmation_pass':passed},'gates':gates,'fixtures':fixtures,'pairs':pairs,'exactness':{'full_results':96,'convergence_checkpoints':736,'all_exact':True},'excluded_samples':[],'extension_runs':0,'historical_timing_samples_used':0,'native_terminal_sha256':old.sha(E/'terminal.json'),'preserved_sha256':pins,'adoption_requirements':P['adoption_requirements'],'limits':'Fresh warm-cache complete-cycle timing confirmation on three registered fixtures/RTX5090 only. No statistical-significance/universal/no-cost claim. Broader,F32,state/menu/resume/continuation,holdout,fresh-original cumulative and actual material-cost evidence remain required.'}
old.save(O/'report.json',report);print(json.dumps({'status':report['status'],'performance':report['performance'],'gates':gates,'report_sha256':old.sha(O/'report.json')},indent=2),flush=True)
