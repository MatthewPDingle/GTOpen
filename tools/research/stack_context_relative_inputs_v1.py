"""Context-bound native observations with an explicit river-relative extension."""
import copy,hashlib
import numpy as np
from stack_context_inputs_v1 import Registry as BaseRegistry,SPEC as BASE_SPEC,encoded,digest
from stack_board_relative_features_v1 import NAMES,relative_features

SPEC=dict(id='stack-context-relative-inputs-v1',input_width=387,base=copy.deepcopy(BASE_SPEC),
    extension=dict(id='river-relative-board-v1',width=25,names=list(NAMES),
                   nonriver='All 25 columns are zero; existing phase inputs identify availability'),
    ordering='362 original context-bound inputs followed by 25 river-relative inputs',
    context_identity=BASE_SPEC['context_identity'])

class Registry(BaseRegistry):
    def __init__(self,entries):
        super().__init__(entries)
        self._manifest['registry_type']='stack-context-relative-registry-v1'
        self._manifest['representation']=copy.deepcopy(SPEC)
        self.sha256=hashlib.sha256(encoded(self._manifest)).hexdigest()

    def prepare(self,queries,*,context_sha256,purpose='inference'):
        prepared=super().prepare(queries,context_sha256=context_sha256,purpose=purpose)
        extra=np.zeros((len(queries['observations']),25),dtype=np.float32);cache={}
        for i,row in enumerate(queries['observations']):
            if row['phase']!=3:continue
            # BaseRegistry has checked key/features, context, public menu and own history.
            lo=int(row['lo']);cards=tuple((lo>>(6*j))&63 for j in range(7))
            if cards not in cache:cache[cards]=relative_features(cards[:2],cards[2:])
            extra[i]=cache[cards]
        x=np.concatenate((prepared['features'],extra),axis=1)
        if x.shape!=(len(extra),387) or not np.isfinite(x).all():raise ValueError('Invalid relative feature matrix')
        return dict(prepared,features=x)
