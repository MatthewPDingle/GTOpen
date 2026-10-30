import json, shutil, sys
from pathlib import Path
sys.path.insert(0,r'X:\Dev\GTOpen-gpu-research-20261016\tools')
import postflop_autoresearch as ar
folder=ar.RESEARCH/'runs/D037-showdown-cache-design'
assert ar.sha256(folder/'README.md')=='37c28a9b14ab49a3f7e7d78621ed3d845a890dc7ed3bac52515c623eb3c35fc2'
assert ar.sha256(folder/'manifest.json')=='82075db7cd76f5b37b3db17ab081bb5b018bebd51d6f6db2a22da747a7340158'
for name in ['README.md','manifest.json','census-summary.json']:
    target=ar.DASHBOARD/'evidence'/folder.name/name
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():assert ar.sha256(target)==ar.sha256(folder/name)
    else:shutil.copyfile(folder/name,target)
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
    s=json.loads(ar.STATUS.read_text(encoding='utf-8'))
    assert not any(r['id']=='D037' for r in s['experiments'])
    s['experiments'].append({'id':'D037','at':ar.now(),'title':'Showdown card-index shared-cache feasibility','kind':'diagnostic','status':'planned','correctness':'pending','stage':'Source and compiler-probe preparation',
      'reason':'Source-only design: cache immutable integer card positions while retaining all arithmetic order. Both training/evaluation shared reservations must increase. Host lookup counts are descriptive; no GPU resource, numerical or performance result yet.',
      'evidence':[{'label':'Sealed source design','url':'evidence/'+folder.name+'/README.md'},
                  {'label':'Unweighted host-only lookup census','url':'evidence/'+folder.name+'/census-summary.json'},
                  {'label':'Design evidence hashes','url':'evidence/'+folder.name+'/manifest.json'}]})
    s.update(updated_at=ar.now(),stage='Preparing showdown cache resource probe',active_experiment='D037',
      activity='E019 rejected and audited; accepted E015 source restored. Preparing a no-launch compiler/resource probe for a distinct showdown card-index cache. Accepted complete-solve improvement remains 9.62%.')
    ar.atomic_json(ar.STATUS,s)
print('Published D037 source-only plan; accepted result unchanged.')
