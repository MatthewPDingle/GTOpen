"""Version-3 visible-feature hybrid models/checkpoints; older readers must reject them.

Preflop tables are part of the policy, including its own-history reach. Never
strip the tables or present this format to a network-only average evaluator.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import uuid

import numpy as np

from sampled_physical_deals_v1 import PhysicalDeals, digest
from sampled_physical_reservoir_v1 import PhysicalReservoir
from sampled_physical_preflop_table_v1 import Table, build
from sampled_visible_poker_features_v1 import WIDTH, FEATURE_NAMES

POLICY_TYPE = "retained-preflop-means-visible-summaries-postflop-v1"
FEATURE_SPEC = dict(id="visible-poker-summaries-v1",base_width=269,input_width=269+WIDTH,feature_names=list(FEATURE_NAMES))

SHAPES={'w0':64*(269+WIDTH),'b0':64,'w1':4096,'b1':64,'w2':256,'b2':4}


def encoded(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()


def uniform_networks():
    return [{name:([1.]*count if name=='b2' else [0.]*count) for name,count in SHAPES.items()} for _ in (0,1)]


def publish(directory, kind, content, suffix='json'):
    directory=Path(directory).resolve();directory.mkdir(parents=True,exist_ok=True)
    h=hashlib.sha256(content).hexdigest();name=f'{kind}-{h}.{suffix}'
    destination=directory/name
    if destination.exists():
        if destination.read_bytes()!=content:raise ValueError('Conflicting immutable object')
    else:
        temporary=directory/('.partial-'+uuid.uuid4().hex)
        with temporary.open('xb') as f:f.write(content);f.flush();os.fsync(f.fileno())
        # Both paths are owned, nonrecursive files inside the checkpoint directory.
        assert temporary.resolve().parent==directory and destination.resolve().parent==directory
        os.replace(temporary,destination)
    return dict(file=name,sha256=h)


def read_object(directory, reference):
    directory=Path(directory).resolve();name=reference['file']
    if not isinstance(name,str) or not re.fullmatch(r'[a-z]+-[0-9a-f]{64}\.(json|npz)',name):
        raise ValueError('Invalid immutable-object path')
    path=directory/name
    if path.resolve().parent!=directory:raise ValueError('Object escapes checkpoint directory')
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=reference['sha256']:
        raise ValueError('Checkpoint object hash mismatch')
    return raw


def validate_network_pair(document):
    if type(document['generation']) is not int or document['generation']<0:
        raise ValueError('Nonnegative integer generation required')
    nets=document['networks'];scales=document['advantage_scales']
    if len(nets)!=2 or len(scales)!=2 or not np.isfinite(scales).all() or min(scales)<=0:
        raise ValueError('Two finite networks and positive scales required')
    for net in nets:
        if set(net)!=set(SHAPES):raise ValueError('Unknown visible network layout')
        for name,count in SHAPES.items():
            values=np.asarray(net[name],dtype=np.float32)
            if values.shape!=(count,) or not np.isfinite(values).all():
                raise ValueError('Invalid visible network parameters')
    if document['generation']==0 and nets!=uniform_networks():
        raise ValueError('Initial model must be uniform')


def validate_config(config):
    if config.get('architecture') != [269+WIDTH,64,64,4] or config.get('representation') != FEATURE_SPEC:
        raise ValueError('Explicit 302-input representation and architecture required')


def validate_model(document, context_source):
    if document['format'] != 3 or document.get('policy_type') != POLICY_TYPE:
        raise ValueError('Explicit hybrid model format required')
    if document['context_sha256'] != digest(context_source):
        raise ValueError('Hybrid model belongs to another game')
    if document.get('representation') != FEATURE_SPEC:
        raise ValueError('Visible representation metadata mismatch')
    validate_network_pair(document)
    tables = document['preflop_tables']
    if not isinstance(tables,list) or len(tables) != 2:
        raise ValueError('Two preflop table slots required')
    if document['generation'] == 0:
        if tables != [None,None]: raise ValueError('Initial uniform model cannot have learned tables')
    else:
        for player,table in enumerate(tables):
            if table is None or Table(table,context_source).player != player:
                raise ValueError('Hybrid model is missing a player table')
            summary = table['source_reservoir']
            if summary['player'] != player or summary['context_sha256'] != digest(context_source):
                raise ValueError('Table source context or actor mismatch')
            if sum(r['count'] for r in table['rows']) > summary['retained']:
                raise ValueError('Table counts exceed source reservoir')


def write_model(directory, generation, networks, scales, tables, *, context_source):
    document=dict(format=3,policy_type=POLICY_TYPE,representation=FEATURE_SPEC,context_sha256=digest(context_source),generation=generation,networks=networks,advantage_scales=scales,preflop_tables=tables)
    validate_model(document,context_source)
    reference=publish(directory,'visiblemodel',encoded(document))
    return dict(**reference,generation=generation)


def model_document(directory, reference, *, context_source):
    document=json.loads(read_object(directory,reference));validate_model(document,context_source)
    if document['generation']!=reference['generation']:raise ValueError('Model generation mismatch')
    return document


def verify_bank(directory, completed, bank, current, *, context_source):
    if type(completed) is not int or completed<0 or len(bank)!=completed:
        raise ValueError('Played bank length must equal completed iterations')
    for generation,ref in enumerate([*bank,current]):
        if type(ref['generation']) is not int or ref['generation']!=generation:
            raise ValueError('Played bank or next-model ordering is inconsistent')
        model_document(directory,ref,context_source=context_source)


def save_checkpoint(directory, *, completed, context_source, config, sampler,
                    action_rng, reservoirs, bank, current):
    validate_config(config)
    directory=Path(directory).resolve();verify_bank(directory,completed,bank,current,context_source=context_source)
    if sampler.context_sha256!=digest(context_source):raise ValueError('Sampler context mismatch')
    if len(reservoirs)!=2 or any(r.player!=p or r.context_sha256!=digest(context_source) for p,r in enumerate(reservoirs)):
        raise ValueError('Reservoir context or actor mismatch')
    current_document=model_document(directory,current,context_source=context_source)
    if completed:
        for player,table in enumerate(current_document['preflop_tables']):
            if table['source_reservoir']!=reservoirs[player].summary():
                raise ValueError('Current preflop table and checkpoint reservoir disagree')
            if encoded(table)!=encoded(build(reservoirs[player],context_source)):
                raise ValueError('Current table does not reproduce retained preflop targets')
    if action_rng.bit_generator.state['bit_generator']!='PCG64':raise ValueError('PCG64 action RNG required')
    if any(r.size and int(r.iterations[:r.size].max())>completed for r in reservoirs):
        raise ValueError('Unfinished iteration in reservoir')
    references=[]
    for r in reservoirs:
        temporary=directory/('.reservoir-'+uuid.uuid4().hex+'.npz')
        r.save(temporary)
        references.append(publish(directory,'reservoir',temporary.read_bytes(),'npz'))
        assert temporary.resolve().parent==directory
        temporary.unlink()
    document=dict(format=3,policy_type=POLICY_TYPE,representation=FEATURE_SPEC,completed_iterations=completed,context_sha256=digest(context_source),
        config=config,config_sha256=hashlib.sha256(encoded(config)).hexdigest(),
        sampler=sampler.checkpoint(),action_rng=action_rng.bit_generator.state,
        reservoirs=references,played_bank=bank,next_model=current,
        averaging='ordinary-CFR equal weights; average bank contains only played generations',
        boundary='Both updater passes and both fresh-seeded fits completed; next iteration not started')
    return publish(directory,'visiblecheckpoint',encoded(document))


def restore_checkpoint(directory, reference, *, context_source, config, manifest_source=None):
    validate_config(config)
    document=json.loads(read_object(directory,reference))
    if (document['format']!=3 or document.get('representation')!=FEATURE_SPEC or document.get('policy_type')!=POLICY_TYPE or document['context_sha256']!=digest(context_source)
            or document['config_sha256']!=hashlib.sha256(encoded(config)).hexdigest()
            or encoded(document['config'])!=encoded(config)):
        raise ValueError('Checkpoint context or training configuration mismatch')
    completed=document['completed_iterations']
    verify_bank(directory,completed,document['played_bank'],document['next_model'],context_source=context_source)
    sampler=PhysicalDeals.restore(document['sampler'],context_source,manifest_source)
    action_rng=np.random.Generator(np.random.PCG64(0))
    action_rng.bit_generator.state=document['action_rng']
    if len(document['reservoirs'])!=2:raise ValueError('Two saved reservoirs required')
    reservoirs=[]
    for player,ref in enumerate(document['reservoirs']):
        read_object(directory,ref)
        r=PhysicalReservoir.load(Path(directory)/ref['file'],context_source)
        if r.player!=player or (r.size and int(r.iterations[:r.size].max())>completed):
            raise ValueError('Invalid saved reservoir actor or iteration')
        reservoirs.append(r)
    current_document=model_document(directory,document['next_model'],context_source=context_source)
    if completed:
        for player,table in enumerate(current_document['preflop_tables']):
            if table['source_reservoir']!=reservoirs[player].summary():
                raise ValueError('Restored preflop table and reservoir disagree')
            if encoded(table)!=encoded(build(reservoirs[player],context_source)):
                raise ValueError('Restored table does not reproduce retained preflop targets')
    return dict(completed_iterations=completed,sampler=sampler,action_rng=action_rng,
                reservoirs=reservoirs,played_bank=document['played_bank'],
                next_model=document['next_model'],next_model_document=model_document(directory,document['next_model'],context_source=context_source))
