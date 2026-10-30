"""Bounded file-only grouping of frozen D067 planned-show maps; no native work."""
from pathlib import Path
from collections import Counter
import hashlib,json,struct
B=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
D=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
catalog_path=B/'runs/D067-execution/mapping-artifacts.json'
report_path=B/'comparisons/D067-planned-show-incidence/report.json'
audit_path=B/'comparisons/D067-independent-review/report.json'
assert sha(report_path)=='bc2abc4281d230d3e8348758bd12795c3ec5a8bf00d6a2c0ac074ba57f831c94'
assert sha(audit_path)=='1ecbdcd95211088d000e6ebbee566a1c3a0ab96c1e6e6ef6f69839950cc22cce'
catalog=json.loads(catalog_path.read_text());prior=json.loads(report_path.read_text())
assert prior['status']=='pass' and prior['mapping_validation_pass'] is True
refs={str(p):sha(p) for p in [catalog_path,report_path,audit_path,B/'runs/D062-fold-reuse-scout/report.json']}
rows=[]
def summarize(counter,total):
    assert sum(counter.values())==total
    return {'unique_keys':len(counter),'duplicate_groups':sum(v>1 for v in counter.values()),'ctas_in_duplicate_groups':sum(v for v in counter.values() if v>1),'additional_ctas_after_first_per_key':total-len(counter),'maximum_multiplicity':max(counter.values(),default=0)}
for fixture in prior['fixtures']:
    identity=fixture['fixture_id'];name=identity+'-planned-show-mapping.u32le'
    path=Path(catalog['mapping_directory'])/name;pin=catalog['files'][name]
    data=path.read_bytes();assert len(data)==pin['bytes'] and sha(path)==pin['sha256'];refs[str(path)]=pin['sha256']
    assert len(data)%36==0;total=len(data)//36
    assert total==fixture['show_ctas_per_traverser']
    for p in range(2):
        q=1-p;key_counts=Counter();payout_counts=Counter()
        for row in struct.iter_unpack('<9I',data):
            assert row[3]<fixture['num_slots'] and row[1+q]<fixture['reach_blocks'][q]
            key=(row[3],row[1+q]);key_counts[key]+=1
            payout_counts[key+row[4:7]]+=1
        item={'fixture_id':identity,'traverser':p,'opponent':q,'planned_show_ctas':total,'key':'(river_slot, opponent_physical_reach_slot)','owner_keys':summarize(key_counts,total),'key_with_payout_bits':'(river_slot, opponent_physical_reach_slot, win_bits, lose_bits, tie_bits)','payout_keys':summarize(payout_counts,total)}
        rows.append(item)
        del key_counts,payout_counts
    del data
all_unique=all(r['owner_keys']['unique_keys']==r['planned_show_ctas'] for r in rows)
result={'id':'D068','scope':'file-only planned structural reuse count from exact retained D067 mapping; no new construction, solve, snapshot or GPU work','status':'SOURCE_PLANNED_STRUCTURAL_COUNT_COMPLETE','rows':rows,'all_owner_keys_unique':all_unique,'recommendation':'Close this narrow same-river/same-opponent-row identity reuse idea for these three plans; no new census or implementation justified.' if all_unique else 'Repeated planned keys exist; any subsequent opportunity requires separately justified dependency/output/cost analysis.','limits':['Physical slot identity is not reach-vector content equality or a dynamic execution frequency measurement.','No runtime, output equivalence, timing, full-solve share or speed claim follows from this map grouping.','D067 maps are accepted-source reconstructed host metadata; D066 did not retain a show metadata device download.','This is distinct from D062 fold ownership proof and does not alter E036 scope or gates.','No cross-iteration, cross-player or cross-board reuse is inferred.'],'reference_sha256':refs,'native_or_gpu_executed':False,'production_modified':False,'performance_measurement':False,'candidate_accepted':False}
with (D/'report.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'rows':rows,'all_owner_keys_unique':all_unique},indent=2))
