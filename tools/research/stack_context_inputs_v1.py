"""Versioned context-bound visible inputs; public prices do not replace identity."""
import copy
import hashlib
import json
import numpy as np
from sampled_visible_features_bulk_v1 import features as visible_features
from sampled_public_economics_features_v1 import encode_document, SPEC as PUBLIC_SPEC
from sampled_visible_hybrid_checkpoint_v1 import FEATURE_SPEC as VISIBLE_SPEC
from sampled_physical_bank_v1 import histories

SPEC=dict(id='stack-context-visible-inputs-v1',input_width=362,
          visible=VISIBLE_SPEC,public=PUBLIC_SPEC,
          ordering='302 original visible inputs followed by 60 public-economics inputs',
          context_identity='SHA256 of exact context source; used for routing, never a numeric network input')

def encoded(value):return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def digest(source):return hashlib.sha256(source.encode()).hexdigest()


class Registry:
    def __init__(self,entries):
        self._contexts={};records=[];names=set()
        for supplied in entries:
            entry=copy.deepcopy(supplied)
            if set(entry)!={'name','split','context_source','public_document'}:
                raise ValueError('Explicit context source, public ledger and split required')
            name=entry['name'];split=entry['split'];source=entry['context_source']
            if not isinstance(name,str) or not name or name in names or split not in ('fit','heldout'):
                raise ValueError('Unique named fit/heldout context required')
            if not isinstance(source,str) or not source:raise ValueError('Exact context source required')
            context=json.loads(source);key=digest(source);ledger=entry['public_document']
            if key in self._contexts or ledger['context_source']!=source:
                raise ValueError('Duplicate or mismatched context')
            if context.get('schema')!='hu-context-v1' or context['positions']!=['BB','BTN']:
                raise ValueError('This prototype supports equal-stack BB/BTN contexts only')
            prices=encode_document(ledger,expected_context_sha256=key)
            if not len(prices):raise ValueError('Complete nonempty public ledger required')
            lookup={}
            for i,row in enumerate(ledger['public_states']):
                hi=row['hi']
                if not isinstance(hi,str) or str(int(hi))!=hi or not 0<int(hi)<2**64:
                    raise ValueError('Canonical public key required')
                if hi in lookup:raise ValueError('Duplicate public key')
                lookup[hi]=(row,prices[i])
            self._contexts[key]=dict(source=source,context=context,lookup=lookup,split=split,name=name)
            names.add(name)
            records.append(dict(name=name,split=split,context_sha256=key,
                public_document_sha256=hashlib.sha256(encoded(ledger)).hexdigest(),
                starting_stack=context['config']['stack'],public_states=len(lookup)))
        if not records or not any(r['split']=='fit' for r in records):raise ValueError('Training contexts required')
        self._manifest=dict(format=1,registry_type='stack-context-registry-v1',representation=SPEC,
                            contexts=sorted(records,key=lambda r:r['context_sha256']))
        self.sha256=hashlib.sha256(encoded(self._manifest)).hexdigest()

    @property
    def manifest(self):return copy.deepcopy(self._manifest)

    @property
    def fit_contexts(self):return tuple(sorted(k for k,v in self._contexts.items() if v['split']=='fit'))

    def source(self,key):return self._get(key)['source']

    def _get(self,key):
        if key not in self._contexts:raise ValueError('Unregistered context; no nearest-context fallback')
        return self._contexts[key]

    def prepare(self,queries,*,context_sha256,purpose='inference'):
        if purpose not in ('inference','fit'):raise ValueError('Explicit operation required')
        entry=self._get(context_sha256)
        if queries.get('context_source')!=entry['source']:
            raise ValueError('Query belongs to a different game')
        if purpose=='fit' and entry['split']!='fit':raise ValueError('Held-out context cannot enter fitting')
        observations=queries['observations']
        if not observations:raise ValueError('Nonempty visible query batch required')
        base=visible_features(observations);public=[];keys=[]
        for o,x in zip(observations,base):
            hi=o['hi'];lo=o['lo']
            if not isinstance(hi,str) or not isinstance(lo,str) or str(int(hi))!=hi or str(int(lo))!=lo:
                raise ValueError('Canonical serialized observation keys required')
            if hi not in entry['lookup']:raise ValueError('Unknown public state in this context')
            row,price=entry['lookup'][hi]
            if (type(o['actor']) is not int or type(o['phase']) is not int or type(o['n']) is not int
                    or (o['actor'],o['phase'],o['n'])!=(row['actor'],row['phase'],len(row['actions']))):
                raise ValueError('Observation actor, street or legal menu disagrees with public ledger')
            # Reconstruct BOTH key halves from the checked original one-hot row.
            # Hidden batch text and the opponent's cards are never inspected.
            cards=[]
            for i in range(7):
                rank=int(np.argmax(x[19*i:19*i+14]));suit=int(np.argmax(x[19*i+14:19*i+19]))
                cards.append(63 if rank==13 else 4*rank+suit)
            actor=int(np.argmax(x[133:135]));phase=int(np.argmax(x[135:139]));node=int(np.argmax(x[139:155]))
            history=[int(np.argmax(x[155+6*i:161+6*i])) for i in range(19)]
            history=history[:next((i for i,a in enumerate(history) if a==0),19)]
            key_lo=(actor<<42)|sum(c<<(6*i) for i,c in enumerate(cards))
            if phase==0:
                if history:raise ValueError('Preflop key cannot contain postflop history')
                key_hi=node+1
            else:
                if history.count(5)!=phase-1:raise ValueError('Visible street/history mismatch')
                h=1
                for token in history:h=(h<<3)|token
                if h>=2**59:raise ValueError('Public history overflow')
                key_hi=(1<<63)|(h<<4)|node
            if (key_hi,key_lo,actor,phase)!=(int(hi),int(lo),o['actor'],o['phase']):
                raise ValueError('Observation keys and visible features disagree')
            public.append(price);keys.append((context_sha256,hi,lo))
        own=histories(observations)
        result=np.concatenate((base,np.asarray(public,dtype=np.float32)),axis=1)
        if result.shape!=(len(observations),362) or not np.isfinite(result).all():
            raise ValueError('Invalid stack-aware visible input')
        return dict(features=result,keys=keys,own_history=own,context_sha256=context_sha256,
                    starting_stack=entry['context']['config']['stack'])
