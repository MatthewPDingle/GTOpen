"""Prospectively fixed A-baseline teacher binding; never fit or sample.

The actual loader requires the same-study successful 64-bank CUDA/reference
gate. This does not admit the separate prediction diagnostic or certify poker.
"""
import copy
import hashlib
import json
from pathlib import Path
import numpy as np
from stack_context_inputs_v1 import Registry,encoded
from stack_context_final_bank_v1 import reference
from stack_context_final_bank_v4 import load_documents
from stack_context_played_bank_v1 import PlayedBank
from stack_context_teacher_path_v1 import Binding
from stack_context_matched_learning_v1 import resources_for
import stack_context_pressure_provenance_v1 as pressure

ROOT=Path('T:/Dev/GTOpen');OUT=pressure.OUT
GATE=OUT/'stack-context-final-bank-throughput-v4-result.json'
GATE_REG=OUT/'stack-context-final-bank-throughput-v4-registration.json'
DESIGN=OUT/'STACK-CONTEXT-PREDICTION-DIAGNOSTIC-DESIGN.md'
DESIGN_SHA='101450338e93536f6663d524ea0a88b6cf541a972481316711c54627eba39e22'
ARM='A-baseline';TYPE='prospectively-fixed-a-baseline-teacher-v1'

def digest(document):return hashlib.sha256(encoded(document)).hexdigest()
def require(value,message):
 if not value:raise ValueError(message)

def selected_manifest(selection,*,selection_identity,gate_identity,training_identity,design_identity):
 """Pure binding of already-authenticated selection; fixtures can qualify it."""
 require(selection_identity==digest(selection) and training_identity==pressure.coordinator.REG_SHA
  and design_identity==DESIGN_SHA,'Detached selection, original registration or prospective design')
 require(type(gate_identity) is str and len(gate_identity)==64
  and all(c in '0123456789abcdef' for c in gate_identity),'Explicit resource-gate identity required')
 require(selection.get('format')==4 and selection.get('training_registration_sha256')==training_identity
  and selection.get('selection_uses_test_results') is False
  and selection.get('recognized_clean_pressure_stop_only') is True
  and selection.get('original_selection_and_weights_unchanged') is True
  and set(selection['arms'])==set(pressure.coordinator.COUNTS),'Original four-arm final selection required')
 chosen=selection['arms'][ARM]
 require(chosen['arm']==ARM and chosen['input_width']==362 and chosen['completed_cycles']==64
  and chosen['weights_by_player']==[list(range(1,65)) for _ in (0,1)]
  and len(chosen['played'])==64,'Only the fixed complete baseline played bank may teach')
 reference(chosen['checkpoint'],'jointcontextcheckpoint')
 for generation,item in enumerate(chosen['played']):reference(item,'fullstackmodel',generation)
 reference(chosen['excluded_unplayed'],'fullstackmodel',64)
 require(len({r['sha256'] for r in [*chosen['played'],chosen['excluded_unplayed']]})==65,'Repeated or substituted teacher model')
 result=dict(format=1,teacher_type=TYPE,arm=ARM,input_width=362,completed_cycles=64,
  checkpoint=copy.deepcopy(chosen['checkpoint']),registry_sha256=chosen['registry_sha256'],
  played=copy.deepcopy(chosen['played']),excluded_unplayed=copy.deepcopy(chosen['excluded_unplayed']),
  weights_by_player=copy.deepcopy(chosen['weights_by_player']),selection_sha256=selection_identity,
  actual_resource_gate_sha256=gate_identity,original_registration_sha256=training_identity,
  prospective_design_sha256=design_identity,selection_uses_test_results=False,
  conditioning='Original complete policy average with each generation own-action reach and every local override',
  diagnostic_scientifically_admitted=False,equilibrium_accuracy_qualified=False)
 result['sha256']=digest(result);return result

def actual_manifest(*,guard):
 guard()
 require(GATE.exists() and GATE_REG.exists(),'Actual complete-bank resource gate not yet available')
 require(not pressure.FAILURE.exists(),'Failed current training cannot supply a teacher')
 proof,registration=pressure.read(GATE),pressure.read(GATE_REG)
 require(proof.get('complete') is True and proof.get('passed') is True
  and proof.get('full_played_banks_64') is True and proof.get('cuda_passed') is True
  and proof.get('reference_agreement_passed') is True and proof.get('new_scientific_deals') is False
  and proof.get('scientific_fits') is False and proof['registration_sha256']==pressure.sha(GATE_REG),
  'Successful actual 64-bank CUDA/reference qualification required')
 pressure.continuation.legacy.verify(proof['inputs']);pressure.continuation.legacy.verify(registration['inputs'])
 selection=registration['selection']
 require(proof['bank_selection_sha256']==registration['selection_sha256']==digest(selection),
  'Resource gate refers to different played models')
 pressure.verify_pressure(pressure.read(pressure.RESULT))
 require(pressure.sha(DESIGN)==DESIGN_SHA,'Prospective teacher design changed')
 return selected_manifest(selection,selection_identity=digest(selection),gate_identity=pressure.sha(GATE),
  training_identity=pressure.coordinator.REG_SHA,design_identity=pressure.sha(DESIGN)),copy.deepcopy(selection['arms'][ARM])

class FixedTeacher:
 """A context-specific immutable average supplied only by the fixed manifest."""
 def __init__(self,*,context_sha256,device,guard):
  require(device in ('cpu','cuda'),'Explicit inference device required')
  manifest,selected=actual_manifest(guard=guard)
  prepared=pressure.read(OUT/'stack-context-population-v1-result.json')
  pressure.continuation.legacy.verify(prepared['artifacts'])
  entries=pressure.read(Path('S:/GTOpen-research/stack-context-population-v1/entries.json'))
  registry=Registry(entries)
  require(registry.sha256==manifest['registry_sha256'],'Fixed teacher registry changed')
  registry.source(context_sha256)
  resources,_,_=resources_for(registry,prepared,0)
  documents=load_documents(pressure.coordinator.STORE/ARM/'objects',selected,registry,resources,guard=guard)
  self._bank=PlayedBank(documents,registry,context_sha256=context_sha256,resources=resources,
   weights_by_player=manifest['weights_by_player'],completed_cycles=64,device=device,guard=guard)
  self._manifest=copy.deepcopy(manifest);self._context=context_sha256;self._source=registry.source(context_sha256)
 @property
 def manifest(self):return copy.deepcopy(self._manifest)
 def average(self,queries,*,guard):
  require(queries.get('context_source')==self._source,'Teacher query belongs to another context')
  Binding(queries)
  guard();return self._bank.average(queries,guard=guard)

def evaluate_plan(*,teacher,teacher_manifest,**arguments):
 """Prevent passing an unrelated manifest to the existing native label adapter."""
 require(isinstance(teacher,FixedTeacher) and teacher.manifest==teacher_manifest,
  'Exact actual fixed teacher/manifest pairing required')
 from stack_context_teacher_native_plan_v1 import evaluate_plan as native
 return native(teacher=teacher,teacher_manifest=teacher_manifest,**arguments)
