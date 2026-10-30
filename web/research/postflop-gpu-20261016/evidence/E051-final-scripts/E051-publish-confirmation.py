"""Publish the complete fresh16 cohort; retain E020 until all adoption gates pass."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/E051-confirmation-plan';P=old.read(H/'protocol.json');O=ROOT/'comparisons/E051-fresh16-confirmation';C=ROOT/'comparisons/E051-fresh16-root-check';Q=old.read(O/'report.json');R=old.read(C/'report.json');E=ROOT/'runs/E051-confirmation-execution';v=Q['performance'];passed=v['fresh_confirmation_pass']
assert Q['status']==('pass_fresh16_timing_only' if passed else 'rejected')
assert R['status']==('pass_timing_only' if passed else 'pass_rejected')
T=old.read(E/'terminal.json');assert T['returncode']==0 and T['complete_sha256']==old.sha(E/'complete.json')
published={}
for directory in [H,E,O,C]+[ROOT/'runs'/n for n in P['measurement_order']]:
 for src in directory.rglob('*'):
  if not src.is_file() or '__pycache__' in src.parts:continue
  key=directory.name+'/'+src.relative_to(directory).as_posix();dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes()
  if dst.exists():assert dst.read_bytes()==data
  else:dst.write_bytes(data)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==data
  published[key]=old.sha(src)
old.save(H/'confirmation-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'decision':Q['decision'],'candidate_accepted':False})
failed=[k for k,x in Q['gates'].items() if not x]
gain=v['observed_gain_pct'];reason=f'Fresh16pair aggregate {gain:.6f}%, {v["positive_pairs"]}/16positive pairs.'
reason+=(' Timing confirmation passes; broader F32/state/menu/resume/continuation, fixed holdout, fresh-original cumulative and material resource/capacity/compatibility qualification required.' if passed else ' Failed fixed gates: '+', '.join(failed)+'. Rejected without extra samples, retuning or new confirmation.')
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='E051');e.update(status='preparing' if passed else 'rejected',stage='Fresh16 timing passed; broader qualification pending' if passed else 'Closed after fresh16confirmation',correctness='pass',baseline_full_cycle_ms=v['baseline_full_cycle_ms'],full_cycle_ms=v['candidate_full_cycle_ms'],observed_gain_pct=gain,reason=reason+' All96fullresults/736checkpoints exact. E020 retained; no new accepted gain.');e['evidence'].extend([{'label':'E051 complete fresh16 confirmation','url':'evidence/E051-fresh16-confirmation/report.json'},{'label':'E051 fresh16 root raw arithmetic replay','url':'evidence/E051-fresh16-root-check/report.json'}]);st.update(state='running',stage='E051 broader qualification preparation' if passed else 'Next GPU hotspot investigation',activity='E051 fresh16 timing passes; adoption gates remain.' if passed else 'E051 rejected after fixed confirmation; E020 retained.',updated_at=ar.now());ar.atomic_json(ar.STATUS,st)
fixtures='; '.join(f"{x['fixture_id']} gain{x['gain_pct']:.10f}%,{x['slower_pairs']}/16slower,guardfailed={x['fixture_guard_failed']}" for x in Q['fixtures'])
text=f'''

### E051 fresh16pair confirmation

After the initial1.8437102311%screen, separate protocol {old.sha(H/'protocol.json')} froze exactly16freshpairs/32processes with B152-B167 and E051C01-C16. Each4pairblock uses BC/CB/CB/BC, totaling8pairs perorder. Initial/historical timing observations never enter this score. Source/binaries/settings/stops/evaluator remained fixed; no controls were rerun. All96complete non-timing results and736checkpoints match accepted E020C1.

Sum of fixture medians {v['baseline_full_cycle_ms']:.10f} to {v['candidate_full_cycle_ms']:.10f}ms gives {gain:.10f}% observed gain; positivepairs {v['positive_pairs']}/16, paired median {v['pair_median_gain_pct']:.10f}%, fourblock medians {v['block_median_gains_pct']}, order medians {v['order_strata_median_gains_pct']}. Fixtures: {fixtures}. {reason} No statistical-significance or universal speed/no-cost claim is made. E051 is not adopted at this checkpoint.

Assessment {old.sha(O/'report.json')} and root stdlib/raw-log replay {old.sha(C/'report.json')} ({R['checks']}checks) preserve the exact fixed decision. Root replay is not external independent review. Every sample and execution/source/publication record is retained and HTTP byte-verified; no exclusions, extensions or historical pooling occurred. All162accepted source/main/HEAD/live/protected PTX remain unchanged. Accepted E020 retains its previously qualified10.3798454492%cumulative suite result. Last actual fresh baselineB167; goal active.
'''
ledger=ar.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### E051 fresh16pair confirmation' not in raw;nl=b'\r\n' if b'\r\n' in raw else b'\n';ledger.write_bytes(raw+text.encode('utf-8').replace(b'\n',nl))
print(json.dumps({'decision':Q['decision'],'gain_pct':gain,'positive_pairs':v['positive_pairs'],'failed_gates':failed,'published':len(published),'publication_sha256':old.sha(H/'confirmation-publication.json')}),flush=True)
