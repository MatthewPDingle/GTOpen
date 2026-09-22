"""Immutable iteration-boundary checkpoints for the physical research trainer.

Played model generations 0..T-1 form the average bank; generation T is next.
Fresh-seeded full fits have no cross-iteration optimizer state to checkpoint.
This store never resumes an unfinished traversal or an unfinished optimizer fit.
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

SHAPES={'w0':17216,'b0':64,'w1':4096,'b1':64,'w2':256,'b2':4}


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


def validate_model(document):
    if document['format']!=1 or type(document['generation']) is not int or document['generation']<0:
        raise ValueError('Invalid model generation')
    nets=document['networks'];scales=document['advantage_scales']
    if len(nets)!=2 or len(scales)!=2 or not np.isfinite(scales).all() or min(scales)<=0:
        raise ValueError('Two finite models with positive scales required')
    for net in nets:
        if set(net)!=set(SHAPES):raise ValueError('Unknown network layout')
        for name,count in SHAPES.items():
            values=np.asarray(net[name],dtype=np.float32)
            if values.shape!=(count,) or not np.isfinite(values).all():
                raise ValueError('Invalid network parameters')
    if document['generation']==0 and nets!=uniform_networks():
        raise ValueError('Generation zero must be the initial uniform policy')


def write_model(directory, generation, networks, scales):
    document=dict(format=1,generation=generation,networks=networks,advantage_scales=scales)
    validate_model(document)
    reference=publish(directory,'model',encoded(document))
    return dict(**reference,generation=generation)


def model_document(directory, reference):
    document=json.loads(read_object(directory,reference));validate_model(document)
    if document['generation']!=reference['generation']:raise ValueError('Model generation mismatch')
    return document


def verify_bank(directory, completed, bank, current):
    if type(completed) is not int or completed<0 or len(bank)!=completed:
        raise ValueError('Played bank length must equal completed iterations')
    for generation,ref in enumerate([*bank,current]):
        if type(ref['generation']) is not int or ref['generation']!=generation:
            raise ValueError('Played bank or next-model ordering is inconsistent')
        model_document(directory,ref)


def save_checkpoint(directory, *, completed, context_source, config, sampler,
                    action_rng, reservoirs, bank, current):
    directory=Path(directory).resolve();verify_bank(directory,completed,bank,current)
    if sampler.context_sha256!=digest(context_source):raise ValueError('Sampler context mismatch')
    if len(reservoirs)!=2 or any(r.player!=p or r.context_sha256!=digest(context_source) for p,r in enumerate(reservoirs)):
        raise ValueError('Reservoir context or actor mismatch')
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
    document=dict(format=1,completed_iterations=completed,context_sha256=digest(context_source),
        config=config,config_sha256=hashlib.sha256(encoded(config)).hexdigest(),
        sampler=sampler.checkpoint(),action_rng=action_rng.bit_generator.state,
        reservoirs=references,played_bank=bank,next_model=current,
        averaging='ordinary-CFR equal weights; average bank contains only played generations',
        boundary='Both updater passes and both fresh-seeded fits completed; next iteration not started')
    return publish(directory,'checkpoint',encoded(document))


def restore_checkpoint(directory, reference, *, context_source, config, manifest_source=None):
    document=json.loads(read_object(directory,reference))
    if (document['format']!=1 or document['context_sha256']!=digest(context_source)
            or document['config_sha256']!=hashlib.sha256(encoded(config)).hexdigest()
            or encoded(document['config'])!=encoded(config)):
        raise ValueError('Checkpoint context or training configuration mismatch')
    completed=document['completed_iterations']
    verify_bank(directory,completed,document['played_bank'],document['next_model'])
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
    return dict(completed_iterations=completed,sampler=sampler,action_rng=action_rng,
                reservoirs=reservoirs,played_bank=document['played_bank'],
                next_model=document['next_model'],next_model_document=model_document(directory,document['next_model']))
