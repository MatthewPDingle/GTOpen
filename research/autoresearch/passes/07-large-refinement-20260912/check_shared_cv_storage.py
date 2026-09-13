"""Verify exact geometry arithmetic, immutable inventory inputs and test completion."""
import json
from run07 import HERE,RAW,digest
from check_joint import require
def verify():
    name='shared-cv-storage-exact-v2';r=json.loads((RAW/(name+'.json')).read_text())
    process=json.loads((RAW/(name+'-exit.json')).read_text())
    require(process['returncode']==0 and process['reason'] is None,'Inventory incomplete')
    for path,h in process['inputs'].items():require(digest(path)==h,'Inventory input changed')
    first=json.loads((RAW/'shared-cv-storage-exact-v1.json').read_text())
    require(r==first,'Final geometry differs from initial inventory')
    require(r['read_only'] is True and r['nodes']==1567754 and r['players']==8 and r['model']=='coupled_deck_v1','Wrong fixture')
    s=r['storage'];terms=r['multiway_terminals'];reach_blocks=r['nodes']+r['players']-1
    require(terms==602914 and s['live_learning_terminal_entries']==2362251,'Wrong terminal coverage')
    require(s['reference_reach_bytes']==reach_blocks*169*4 and s['reference_mass_bytes']==reach_blocks*4,'Wrong reference size')
    require(s['current_scratch_bytes']==terms*169*4 and s['full_payoff_bytes']==s['live_learning_terminal_entries']*169*4,'Wrong payoff size')
    require(s['offset_bytes']==terms*r['players']*4,'Wrong offset size')
    total=sum(s[k] for k in ('reference_reach_bytes','reference_mass_bytes','current_scratch_bytes','full_payoff_bytes','offset_bytes'))
    require(total==s['persistent_extra_bytes'] and total<=s['cap_bytes']==4*1024**3 and s['fits_four_gib'],'Memory cap violated')
    old=r['players']*(s['reference_reach_bytes']+s['reference_mass_bytes']+s['current_scratch_bytes'])+s['current_scratch_bytes']
    require(old==12196748616,'Old layout arithmetic differs')
    for name in ('shared-cv-numerical-v4','shared-cv-old-compat-v1','shared-cv-native-compat-v1','shared-cv-default-suite-v1'):
        run=json.loads((RAW/(name+'-exit.json')).read_text());require(run['returncode']==0 and run['reason'] is None,'Failed prerequisite '+name)
    return dict(evidence_verified=True,extra_bytes=total,previous_extra_bytes=old,bytes_saved=old-total,
        fraction_saved=1-total/old,large_gpu_allocation_tested=False,
        scope='Exact large geometry and small numerical GPU gates; no speed qualification')
if __name__=='__main__':print(json.dumps(verify(),indent=2))
