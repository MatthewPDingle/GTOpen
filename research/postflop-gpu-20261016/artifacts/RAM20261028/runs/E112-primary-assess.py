"""Read fixed observations; no new native runs and no sample exclusions."""
import sys,json,statistics,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/E112-primary-plan';assert len(sys.argv)==2;P=h.read(H/'protocol.json');h.pin(H/'protocol.json',sys.argv[1]);h.custody()
for p,digest in P['input_sha256'].items():h.pin(p,digest)
O=ROOT/'runs/E112-primary-execution';done=h.read(O/'complete.json');assert done['all_owned_children_terminal']and done['protocol_sha256']==sys.argv[1]
anchor=h.read(h.EPOCH/'exact-anchor.json');reports={};pins={};end=None
for rec in P['sequence']:
 ident=rec['id'];receipt=h.read(O/(ident+'.exit.json'));inv=h.read(O/(ident+'.invocation.json'))
 assert receipt['returncode']==0 and receipt['error']is receipt['cleanup']is None
 begin=datetime.datetime.fromisoformat(receipt['started_at']);finish=datetime.datetime.fromisoformat(receipt['finished_at']);assert begin<=finish and(end is None or end<=begin);end=finish
 r=h.read(ROOT/'runs'/ident/'report.json');assert inv['cwd']==str(h.REPO)and inv['command'][inv['command'].index('--id')+1]==ident
 assert r['status']=='measured'and r['returncode']==0 and r['provenance']['source_sha256']==P['accepted_source_sha256']
 pins[str(ROOT/'runs'/ident/'report.json')]=h.sha(ROOT/'runs'/ident/'report.json')
 if not rec['unit']:assert h.exact(ident)==anchor;reports[ident]=r
fixtures=[];bs=0.;cs=0.;pairdata=[{'baseline':x['baseline'],'candidate':x['candidate'],'fixture_gain_pct':{}}for x in P['pairs']]
for fid in['rainbow','two-tone','river']:
 b=[next(x for x in reports[p['baseline']]['results']if x['fixture_id']==fid)['full_cycle_ms']for p in P['pairs']]
 c=[next(x for x in reports[p['candidate']]['results']if x['fixture_id']==fid)['full_cycle_ms']for p in P['pairs']]
 bm,cm=statistics.median(b),statistics.median(c);bs+=bm;cs+=cm;g=100*(bm-cm)/bm;pairg=[100*(x-y)/x for x,y in zip(b,c)]
 for i,p in enumerate(pairdata):p['fixture_gain_pct'][fid]=pairg[i]
 fixtures.append({'fixture_id':fid,'baseline_ms':b,'candidate_ms':c,'baseline_median_ms':bm,'candidate_median_ms':cm,'gain_pct':g,'paired_gain_pct':pairg,'guard_failed':g<0 and sum(v<0 for v in pairg)>=2})
gain=100*(bs-cs)/bs;passed=gain>=1 and not any(f['guard_failed']for f in fixtures)
for p in pairdata:
 b=sum(x['full_cycle_ms']for x in reports[p['baseline']]['results']);c=sum(x['full_cycle_ms']for x in reports[p['candidate']]['results']);p.update(baseline_suite_ms=b,candidate_suite_ms=c,gain_pct=100*(b-c)/b)
D=ROOT/'comparisons/E112-three-pair-comparison';D.mkdir(exist_ok=False)
report={'id':'E112-primary','at':h.now(),'measurement_epoch':'RAM20261028','protocol_sha256':sys.argv[1],'decision':'advance_to_separately_frozen_confirmation'if passed else'rejected','performance':{'aggregation':'Unrounded sum of per-fixture medians; three observations per arm','baseline_full_cycle_ms':bs,'candidate_full_cycle_ms':cs,'observed_gain_pct':gain,'required_gain_pct':1.,'primary_timing_pass':passed,'fixture_regression_guard':[{'fixture_id':f['fixture_id'],'median_slowdown_pct':-f['gain_pct'],'slower_pairs':sum(v<0 for v in f['paired_gain_pct']),'failed':f['guard_failed']}for f in fixtures],'statistical_significance_established':False},'fixtures':fixtures,'pairs':pairdata,'exactness':{'fixture_results':18,'convergence_records':138,'all_exact':True},'ordinary_units_passed':86,'ordinary_units_ignored':4,'preserved_reports_sha256':pins,'excluded_samples':[],'extension_runs':0,'historical_timing_samples_used':0,'RAM_baseline_samples_scored':0,'candidate_accepted':False,'adoption_requirements':P['adoption_requirements']}
h.save(D/'report.json',report);print(json.dumps({'decision':report['decision'],'performance':report['performance']},indent=2),flush=True)
