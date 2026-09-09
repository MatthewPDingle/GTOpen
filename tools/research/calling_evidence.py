"""Export aggregate evidence counts, never raw hands or session identifiers."""
import collections, importlib.util, json
from pathlib import Path
spec=importlib.util.spec_from_file_location('calling_audit',Path(__file__).with_name('calling_audit.py'))
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
def run():
    manifest=a.verify_inputs();data=json.loads((a.PRIVATE/'observations.json').read_text());groups={}
    for s in data['sessions']:
        for z in s['records']:
            r=z['row'];key=tuple(map(int,[r[0],r[1],r[2],r[3]]))
            if key not in groups:groups[key]=dict(decisions=0,sessions=set(),hand_decisions=[0]*169,first_entry=collections.Counter())
            g=groups[key];g['decisions']+=1;g['sessions'].add(s['id']);g['hand_decisions'][int(r[7])]+=1;g['first_entry'][z['kind']]+=1
    records=[]
    for (n,role,entry,depth),g in sorted(groups.items()):records.append(dict(players=n,role=role,entry=['cold','called','raised'][entry],depth=3 if depth else 2,decisions=g['decisions'],sessions=len(g['sessions']),observed_classes=sum(n>0 for n in g['hand_decisions'])))
    result=dict(schema=1,coverage_complete=True,coverage_note='Every current source re-raise observation is included. An omitted exact supported schema key has zero observations in this source snapshot, not zero probability and not proof about all possible histories.',model_id='ignition-nl10-reraise-v1',source_scope='Ignition NL10 regular opponent known-card histories, 3-6 players, no ante. Existing v1 entry/depth schema; pooled over prices, stacks and prior action detail.',model_sha256=a.digest(a.ARTIFACT),generator_sha256=a.digest(__file__),observation_sha256=manifest['observations_sha256'],source_collection_manifest_sha256=a.digest(a.PRIVATE/'manifest.json'),decisions=sum(g['decisions'] for g in groups.values()),source_sessions=len(data['sessions']),validation='retrospective; source also used in fitting the installed model',support_definition='Historical decision counts at the same table size, position, ever-raised entry state, and raise depth. Counts pool prices, stack depths, first-entry action, opponent positions and raise sequences. They do not validate an individual predicted probability.',interpretation='Contextual estimate. Zero direct hand count means a modeled/pooled prediction, not an observed range; nonzero count is not confidence. Later independent observations are still needed.',contexts=records)
    a.write(a.OUT/'evidence-metadata.json',result);print(f'{len(records)} aggregate contexts, {result["decisions"]} decisions; model unchanged')
if __name__=='__main__':run()
