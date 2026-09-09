"""Frozen-model cross-stakes/format check. Never fits or installs a model.

Raw histories and session observations stay under --private-out. Only aggregate
validation results and the protocol are written to the public research folder.
"""
import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/transfer'
ARTIFACT=ROOT/'cache/contextual/ignition-nl10-reraise-v1.json'
SHA='d4951da8fadfd5f76da95df7e5f87a3965dc7bf042c1480854e14ef3d5883ae5'
GROUPS=[(5,False),(5,True),(25,False),(25,True)]
COLLECTOR_FILES=['tools/research/transfer_validation.py','tools/ignition/analyze.py','tools/coinpoker/analyze.py']
# Include the entire repository import chain, even helpers whose fitting
# functions remain unused. Frozen inference calls smoothing.closest through
# limps -> responses -> ignition.fit and imports CoinPoker fit/context there.
PREDICTOR_FILES=['tools/ignition/contextual_reraise.py','tools/ignition/smoothing.py',
    'tools/ignition/limps.py','tools/ignition/responses.py','tools/ignition/fit.py',
    'tools/coinpoker/fit.py','tools/coinpoker/context.py']
MANIFEST='collection_manifest.json'


class IntegrityError(ValueError):
    """Collection inputs do not match their validated provenance."""


def require(condition,message):
    if not condition:raise IntegrityError(message)


def sha256(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def group_name(stake,zone):return f'NL{stake}-'+('zone' if zone else 'regular')


def analysis_metadata(data,stake,zone):
    expected=dict(schema=4,site='Ignition',stake=f'NL{stake} {"Zone" if zone else "regular"}')
    require(all(data.get(k)==v for k,v in expected.items()),f'Analysis metadata mismatch for {group_name(stake,zone)}')
    require(isinstance(data.get('sessions'),list) and isinstance(data.get('audit'),dict),'Missing analysis sessions/audit')
    return {**expected,'validated_sessions':len(data['sessions']),'audit':data['audit']}


def source_snapshot(paths,source):
    """Private file/ID provenance, including rejected hands for overlap checks."""
    files=[];hand_ids=set()
    for path in paths:
        raw=path.read_bytes()
        hand_ids.update(re.findall(r'^Ignition Hand #(\d+)',raw.decode('utf-8-sig',errors='replace'),re.M))
        files.append(dict(path=str(path.relative_to(source)),sha256=hashlib.sha256(raw).hexdigest()))
    require(files and hand_ids,'Selected source contains no hand histories')
    return dict(files=files,hand_ids=sorted(hand_ids),unique_hand_ids=len(hand_ids))


def verify_disjoint(training,groups):
    def ids(snapshot):
        values=snapshot.get('hand_ids')
        require(isinstance(values,list) and all(isinstance(v,str) and v.isdecimal() for v in values),'Missing/invalid hand-ID provenance')
        require(len(set(values))==len(values)==snapshot.get('unique_hand_ids'),'Hand-ID provenance count mismatch')
        require(values and isinstance(snapshot.get('files'),list) and snapshot['files'],'Missing source-file provenance')
        return set(values)
    prior=ids(training);comparisons=[]
    for stake,zone in GROUPS:
        name=group_name(stake,zone);target=ids(groups[name])
        overlap=len(prior&target)
        require(overlap==0,f'Overlapping training/evaluation hand IDs in {name}')
        comparisons.append(dict(group=name,prior_unique_hand_ids=len(prior),target_unique_hand_ids=len(target),overlapping_hand_ids=overlap))
        prior.update(target)
    return dict(method='Exact hand-ID set intersection against NL10 regular and all earlier target groups, before validation exclusions.',comparisons=comparisons)


def verify_collection(private):
    """Validate all inputs before returning the same bytes that will be scored."""
    path=private/MANIFEST
    require(path.is_file(),'Missing collection manifest; run collect before evaluate')
    raw_manifest=path.read_bytes();manifest=json.loads(raw_manifest)
    require(manifest.get('schema')==1,'Unsupported collection manifest schema')
    require(manifest.get('protocol_sha256')==sha256(OUT/'protocol.json'),'Collection protocol hash mismatch')
    require(manifest.get('model_sha256')==SHA==sha256(ARTIFACT),'Collection model hash mismatch')
    require(manifest.get('collector_sha256')=={p:sha256(ROOT/p) for p in COLLECTOR_FILES},'Collector source changed; recollect inputs')
    require(manifest.get('predictor_sha256')=={p:sha256(ROOT/p) for p in PREDICTOR_FILES},'Predictor source or helper changed; recollect inputs')
    groups=manifest.get('groups',{})
    require(set(groups)=={group_name(stake,zone) for stake,zone in GROUPS},'Collection group set mismatch')
    overlap=verify_disjoint(manifest.get('training',{}),groups)
    require(manifest.get('overlap_check')==overlap,'Overlap-check provenance mismatch')
    inputs={}
    for stake,zone in GROUPS:
        name=group_name(stake,zone);record=groups[name]
        path=private/name/'analysis.json'
        require(path.is_file(),f'Missing analysis for {name}')
        raw=path.read_bytes();digest=hashlib.sha256(raw).hexdigest()
        require(record.get('analysis_sha256')==digest,f'Analysis hash mismatch for {name}')
        data=json.loads(raw)
        require(record.get('analysis_metadata')==analysis_metadata(data,stake,zone),f'Collection metadata mismatch for {name}')
        inputs[name]=(data,digest)
    return inputs,hashlib.sha256(raw_manifest).hexdigest()

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod)
    return mod

def protocol():
    require(sha256(ARTIFACT)==SHA,'Frozen model changed')
    frozen=dict(schema=1,model='ignition-nl10-reraise-v1',model_sha256=SHA,
        sources=[dict(stake=stake,zone=zone) for stake,zone in GROUPS],
        target='Opponent re-raise decisions; exclude hero, validate cards/action order/money, deduplicate hand IDs.',
        comparator='Frozen NL10 pooled baseline probabilities embedded in the SAME artifact; no target-domain fitting.',
        metrics=['multinomial log loss','Brier score','observed and predicted call frequency'],
        subgroups=['all','cold','after_entry','after_entry_price_le_25pct','after_entry_weak_offsuit_price_le_25pct'],
        weak_hand_definition='Offsuit T-high or lower, matching the behavior sensitivity study.',
        uncertainty='Paired 2000-resample bootstrap by source file/session, seed 20260909. Exploratory per-comparison intervals, not simultaneous guarantees.',
        promotion=False,
        prior_exposure='Source existence, card visibility and broad counts were inspected before this protocol. These sources were not used to fit the frozen NL10 candidate. Cross-domain diagnostics, not a fresh NL10 temporal holdout.',
        interpretation='NL5 and NL25 source blinds are 0.4/1; source-format guards remain unchanged. Zone and regular tables stay separate. No result changes the candidate, library entries or source support.')
    OUT.mkdir(parents=True,exist_ok=True)
    path=OUT/'protocol.json'
    if path.exists(): require(json.loads(path.read_text())==frozen,'Protocol differs from existing frozen file')
    else: path.write_text(json.dumps(frozen,indent=2)+'\n',encoding='utf-8')
    return frozen

def collect(source,private):
    protocol()
    source=Path(source);private=Path(private);private.mkdir(parents=True,exist_ok=True)
    # A failed/interrupted recollection must not leave an older success marker.
    (private/MANIFEST).unlink(missing_ok=True)
    analyzer=module('ignition_transfer_analyzer',ROOT/'tools/ignition/analyze.py')
    manifest=dict(schema=1,protocol_sha256=sha256(OUT/'protocol.json'),model_sha256=SHA,
        collector_sha256={p:sha256(ROOT/p) for p in COLLECTOR_FILES},
        predictor_sha256={p:sha256(ROOT/p) for p in PREDICTOR_FILES},
        training=source_snapshot(analyzer.source_paths(source),source),groups={})
    # Snapshot all sources before parsing so the disjointness check precedes scoring.
    for stake,zone in GROUPS:
        name=group_name(stake,zone)
        manifest['groups'][name]=source_snapshot(analyzer.source_paths(source,stake,zone),source)
    manifest['overlap_check']=verify_disjoint(manifest['training'],manifest['groups'])
    for stake,zone in GROUPS:
        name=group_name(stake,zone);record=manifest['groups'][name]
        analyzer.run(source,private/name,stake,zone)
        require(source_snapshot(analyzer.source_paths(source,stake,zone),source)==record,f'Source changed during collection for {name}')
        path=private/name/'analysis.json';data=json.loads(path.read_bytes())
        record.update(analysis_sha256=sha256(path),analysis_metadata=analysis_metadata(data,stake,zone))
    require(source_snapshot(analyzer.source_paths(source),source)==manifest['training'],'NL10 source changed during collection')
    require(manifest['collector_sha256']=={p:sha256(ROOT/p) for p in COLLECTOR_FILES},'Collector changed during collection')
    require(manifest['predictor_sha256']=={p:sha256(ROOT/p) for p in PREDICTOR_FILES},'Predictor source or helper changed during collection')
    temp=private/(MANIFEST+'.tmp')
    temp.write_bytes((json.dumps(manifest,indent=2,allow_nan=False)+'\n').encode('utf-8'))
    temp.replace(private/MANIFEST)
    verify_collection(private)
    print('Validated four separate sources; no hand IDs overlap training or another target group.')

def score(y,old,new,sessions):
    total=int(y.sum())
    if not total:return None
    weights=y.sum(1)
    losses=[-(y*np.log(np.maximum(p,1e-12))).sum(1) for p in [old,new]]
    # For a grouped multinomial row, average sum_a(p_a-onehot_a)^2.
    brier=[(weights*(p*p).sum(1)-2*(y*p).sum(1)+weights).sum()/total for p in [old,new]]
    units=np.array([[weights[sessions==s].sum(),(losses[0]-losses[1])[sessions==s].sum()] for s in np.unique(sessions)])
    rng=np.random.default_rng(20260909)
    draws=[]
    for _ in range(2000):
        sampled=units[rng.integers(len(units),size=len(units))].sum(0)
        draws.append(sampled[1]/sampled[0])
    return dict(decisions=total,sessions=len(units),baseline_log_loss=float(losses[0].sum()/total),
        contextual_log_loss=float(losses[1].sum()/total),
        log_loss_gain_95_interval=np.quantile(draws,[.025,.975]).tolist() if len(units)>=2 else None,
        interval_note='Paired session bootstrap; sparse groups remain exploratory.' if len(units)>=2 else 'Not estimable from fewer than two independent session groups.',
        baseline_brier=float(brier[0]),contextual_brier=float(brier[1]),
        observed_call=float(y[:,1].sum()/total),baseline_call=float((weights*old[:,1]).sum()/total),
        contextual_call=float((weights*new[:,1]).sum()/total))

def evaluate(private):
    frozen=protocol()
    inputs,manifest_digest=verify_collection(Path(private))
    predictor=module('ignition_transfer_predictor',ROOT/'tools/ignition/contextual_reraise.py')
    artifact=json.loads(ARTIFACT.read_text(encoding='utf-8'))
    models={bucket:{(r['players'],r['role']):np.array(r['probabilities']) for r in rows} for bucket,rows in artifact['baseline'].items()}
    source_files=COLLECTOR_FILES+PREDICTOR_FILES
    result=dict(schema=1,protocol_sha256=hashlib.sha256((OUT/'protocol.json').read_bytes()).hexdigest(),
        model_sha256=SHA,collection_manifest_sha256=manifest_digest,production_changed=False,groups={},
        source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in source_files})
    for stake,zone in GROUPS:
        name=group_name(stake,zone)
        data,analysis_digest=inputs[name]
        rows,y,sessions=predictor.observations(data['sessions'])
        metrics={}
        if len(rows):
            x,names=predictor.features(rows,'hand_price');assert names==artifact['features']
            old=predictor.base_probs(models,rows)
            new=predictor.predict(x,old,np.array(artifact['weights']))
            h=rows[:,7].astype(int)
            weak=(h//13<h%13)&(h%13<9)
            entered=rows[:,2]!=0;cheap=rows[:,4]<=.25
            masks={'all':np.ones(len(rows),bool),'cold':~entered,'after_entry':entered,
                'after_entry_price_le_25pct':entered&cheap,'after_entry_weak_offsuit_price_le_25pct':entered&cheap&weak}
            metrics={key:score(y[mask],old[mask],new[mask],sessions[mask]) for key,mask in masks.items()}
        result['groups'][name]=dict(audit=data['audit'],validated_sessions=len(data['sessions']),
            private_analysis_sha256=analysis_digest,
            date_from=min((s['first'] for s in data['sessions']),default=None),
            date_to=max((s['last'] for s in data['sessions']),default=None),metrics=metrics)
    (OUT/'evaluation.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mode',choices=['prepare','collect','evaluate'])
    ap.add_argument('--source',type=Path,default=Path('T:/Dev/Poker Data/Ignition'))
    ap.add_argument('--private-out',type=Path,default=ROOT/'output/ignition-transfer-v1')
    args=ap.parse_args()
    if args.mode=='prepare':protocol()
    elif args.mode=='collect':collect(args.source,args.private_out)
    else:evaluate(args.private_out)
