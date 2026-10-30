"""Genuine v2 board-admission checks with synthetic data and receipt plumbing.

No exporter, spawned worker, CUDA fit, production call, or scientific run is
allowed. A preserved two-hand native software template supplies topology and
cashflows; this script expands it to all 1081 private hands on a planned board,
with invented ranks. FrozenExpectedTargets.draw_record and pipeline.verify_board
are real. Only native receipt verification is replaced by explicit file-only
synthetic plumbing. This does not qualify actual execution or OS process proof.
All artifacts remain in the requested control directory, including failures.
"""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='-1', OPENBLAS_NUM_THREADS='1',
    OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', NUMEXPR_NUM_THREADS='1',
    PYTHONDONTWRITEBYTECODE='1')
import copy
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback
from unittest.mock import patch

import numpy as np
from threadpoolctl import threadpool_limits

STAGE = Path(__file__).resolve().parent
TOOLS = Path(r'T:\Dev\GTOpen\tools\research')
sys.path.append(str(TOOLS))
import preflop_expected_training_pipeline_v1 as pipeline
import preflop_expected_training_control_fixture_v1 as fixture
import preflop_expected_board_workers_v1 as worker
import preflop_expected_native_execution_v1 as execution
from preflop_expected_native_targets_v2 import FrozenExpectedTargets
from preflop_expected_native_targets_v1 import canonical_card_keys
import sampled_visible_hybrid_checkpoint_v1 as storage
from board_root_accumulator_v1 import digest

SCOPE = ('Synthetic software controls only: actual frozen v2 target construction '
    'and board admission, preserved native software topology, invented ranks, '
    'file-only mocked receipts. No native execution, OS process qualification, '
    'scientific simulation, CUDA fit or publication.')


def write(path, document):
    with Path(path).open('xb') as stream:
        stream.write((json.dumps(document, sort_keys=True, separators=(',', ':'),
            allow_nan=False)+'\n').encode('utf-8'))


def source_ids():
    result = fixture.inputs()
    for module in list(sys.modules.values()):
        path = getattr(module, '__file__', None)
        if path and Path(path).suffix == '.py' and Path(path).resolve().parent in (STAGE,TOOLS):
            result[str(Path(path).resolve())] = pipeline.sha(path)
    result[str(Path(__file__).resolve())] = pipeline.sha(__file__)
    return result


def observation(hi, lo, actor, phase, arity):
    cards = [(lo >> (6*i)) & 63 for i in range(7)]
    active = []
    for i, card in enumerate(cards):
        active.extend((19*i+(13 if card == 63 else card//4),
            19*i+14+(4 if card == 63 else card % 4)))
    history = []; history_key = (int(hi) & ((1 << 63)-1)) >> 4
    while history_key > 1:
        history.append(history_key & 7); history_key >>= 3
    history.reverse()
    active.extend((133+actor,135+phase,139+(int(hi)&15)))
    active.extend(155+6*i+(history[i] if i < len(history) else 0) for i in range(19))
    return dict(hi=hi,lo=str(lo),actor=actor,phase=phase,n=arity,active_features=active)


def synthetic_tree(template, request):
    tree = copy.deepcopy(template)
    tree['board'] = request['board'].copy(); tree['hands'] = copy.deepcopy(request['hands'])
    hands = np.asarray(request['hands'][0],dtype=np.int64)
    ranks = (hands.sum(1)*7+(hands[:,1]-hands[:,0]) % 5).tolist()
    tree['ranks'] = [ranks,ranks.copy()]
    keys = {}; count = 0
    for branch in tree['branches']:
        for node in branch['nodes']:
            if node['kind'] != 0: continue
            actor,phase = node['actor'],node['street']+1; key = actor,phase
            if key not in keys:
                keys[key] = canonical_card_keys(hands,request['board'],actor,phase)
            hi = node['observations'][0]['hi']
            node['observations'] = [observation(hi,int(lo),actor,phase,len(node['children']))
                for lo in keys[key]]
            count += len(node['observations'])
    return tree,count


class SyntheticReceiptPlumbing:
    """Explicit no-process substitute for the exporter receipt boundary only."""
    def __init__(self): self.calls = 0

    def verify(self, result, *, executable, arguments, expected_identities):
        self.calls += 1
        if set(result) != execution.RESULT_FIELDS:
            raise ValueError('Incomplete synthetic receipt plumbing result')
        r = result['receipt']
        if (r['method'] != 'synthetic-file-only-no-process'
                or r['argv'] != [str(Path(executable).resolve()),*arguments]
                or r['expected_identities'] != expected_identities):
            raise ValueError('Changed synthetic receipt command or source identities')
        if any(pipeline.sha(path) != identity for path,identity in expected_identities.items()):
            raise ValueError('Changed synthetic receipt input source')
        if (pipeline.sha(result['receipt_path']) != result['receipt_sha256']
                or json.loads(Path(result['receipt_path']).read_bytes()) != r):
            raise ValueError('Changed synthetic terminal receipt artifact')
        for name in ('stdout','stderr'):
            if (pipeline.sha(result[name+'_path']) != result[name+'_sha256']
                    or r[name] != dict(path=result[name+'_path'],sha256=result[name+'_sha256'],
                        bytes=Path(result[name+'_path']).stat().st_size)):
                raise ValueError('Changed synthetic native raw-output artifact')
        return r


class AdmissionControls:
    def __init__(self, root):
        self.root = Path(root).resolve(); self.root.mkdir(parents=True,exist_ok=False)
        self.began = time.monotonic(); self.cases = []; self.rejections = []
        self.objects = self.root/'synthetic-objects'
        self.registry,self.resources,self.config,self.previous = fixture.fixture(362,directory=self.objects)
        self.key = next(row['context_sha256'] for row in self.registry.manifest['contexts']
            if row['split']=='fit' and row['starting_stack']==20)
        self.state = self.previous['contexts'][self.key]['preflop_state']
        source = storage.read_object(self.objects,self.previous['next_model']).decode('utf-8')
        self.provider = FrozenExpectedTargets(state=self.state,model_source=source,
            registry=self.registry,resources=self.resources)
        self.plan = self.state.plan(); self.board = self.plan['boards'][0]
        self.original_document = self.state.document()
        self.original_locals = {key:pipeline.checkpoint.local_fit_identity(value)
            for key,value in self.previous['contexts'].items()}
        self.original_model = copy.deepcopy(self.previous['next_model'])
        self.context_path = self.root/'context.json'
        self.context_path.write_bytes(self.registry.source(self.key).encode('utf-8'))
        self.executable = self.root/'do-not-execute.synthetic'
        self.executable.write_bytes(b'Synthetic placeholder: must never be executed')
        self.native_ids = {str(path):pipeline.sha(path) for path in (self.context_path,self.executable)}
        self.limits = worker._limits(dict(max_worker_seconds=300,native_timeout_seconds=120))
        self.plumbing = SyntheticReceiptPlumbing()
        self.baseline = self.make_baseline()
        self.config['source_identities'].update(source_ids())
        self.config['source_identities'].update(self.native_ids)
        pipeline.verify_sources(self.config)

    def make_baseline(self):
        request,_ = self.provider.request(self.board)
        self.request_path = self.root/'request.json'; write(self.request_path,request)
        template_path = STAGE/'preflop-native-software-template-stack-20-tree.json'
        proof_path = STAGE/'preflop-native-software-template-stack-20-result.json'
        proof = json.loads(proof_path.read_bytes())
        if (pipeline.sha(template_path)!=proof['tree_sha256'] or proof['context_sha256']!=self.key
                or proof['exit_code']!=0 or proof['scientific_attempt'] is not False):
            raise ValueError('Preserved software template provenance changed')
        self.template_inputs = {str(path):pipeline.sha(path) for path in (template_path,proof_path)}
        tree,self.observation_count = synthetic_tree(json.loads(template_path.read_bytes()),request)
        self.tree_path = self.root/'synthetic-tree.json'; write(self.tree_path,tree)
        del tree
        self.tree_sha = pipeline.sha(self.tree_path)
        record = self.provider.draw_record(self.tree_path.read_bytes(),
            expected_tree_sha256=self.tree_sha,draw_index=0)
        self.stderr_path = self.root/'synthetic.stderr'; self.stderr_path.write_bytes(b'')
        invocation_ids = {**self.native_ids,str(self.request_path):pipeline.sha(self.request_path)}
        # Fixed invented timestamps/PIDs are explicitly synthetic receipt inputs.
        receipt = dict(method='synthetic-file-only-no-process',
            argv=[str(self.executable),str(self.context_path),str(self.request_path)],
            expected_identities=invocation_ids,caller=dict(pid=424242,creation_time=100.),
            started_unix=103.,terminal_unix=104.,timeout_seconds=self.limits['native_timeout_seconds'],
            max_output_bytes=self.limits['max_output_bytes'],
            stdout=dict(path=str(self.tree_path),sha256=self.tree_sha,bytes=self.tree_path.stat().st_size),
            stderr=dict(path=str(self.stderr_path),sha256=pipeline.sha(self.stderr_path),bytes=0))
        receipt_path = self.root/'synthetic-receipt.json'; write(receipt_path,receipt)
        invocation = dict(receipt_path=str(receipt_path),receipt_sha256=pipeline.sha(receipt_path),
            stdout_path=str(self.tree_path),stdout_sha256=self.tree_sha,
            stderr_path=str(self.stderr_path),stderr_sha256=pipeline.sha(self.stderr_path),receipt=receipt)
        sources = {str(Path(sys.modules[name].__file__).resolve()):pipeline.sha(sys.modules[name].__file__)
            for name in ('preflop_expected_board_workers_v1','preflop_expected_native_execution_v1',
                'preflop_expected_native_targets_v2','preflop_expected_native_targets_v1','preflop_expected_policy_v1')}
        return dict(format=1,method=worker.METHOD,record=record,draw_index=0,board=self.board.copy(),
            generation=self.provider.recipe['generation'],context_sha256=self.key,
            registry_sha256=self.registry.sha256,model_sha256=self.provider.recipe['model_sha256'],
            recipe=self.provider.recipe,recipe_sha256=digest(self.provider.recipe),
            plan_sha256=digest(self.plan),parent_state_sha256=self.plan['parent_state_sha256'],
            native_identities=self.native_ids,invocation_identities=invocation_ids,
            worker_source_identities=sources,request_artifact=str(self.request_path),
            request_sha256=pipeline.sha(self.request_path),request_document_sha256=digest(request),
            tree_artifact=str(self.tree_path),tree_sha256=self.tree_sha,native_invocation=invocation,
            runtime_limits=self.limits,initialized_unix=101.,started_unix=102.,terminal_unix=105.,
            seconds=3.,worker_seconds=4.,pid=424242,creation_time=100.,rss_bytes=0,
            cuda_visible_devices='-1',threadpool_limit=1)

    def unchanged(self):
        assert self.state.document()==self.original_document
        assert {key:pipeline.checkpoint.local_fit_identity(value)
            for key,value in self.previous['contexts'].items()}==self.original_locals
        assert self.previous['next_model']==self.original_model
        assert self.previous['played_bank']==[] and self.previous['completed_cycles']==0
        assert not list(self.objects.glob('expectedcontextcheckpoint*'))

    def check(self, label, *, change=lambda result,part:None, config_change=lambda config:None,
              expected_error=None, replay_calls=0, index=0, board=None, admitted=False):
        part=self.root/label; part.mkdir()
        result=copy.deepcopy(self.baseline); change(result,part)
        config=copy.deepcopy(self.config); config_change(config)
        rp=part/'worker-result.json'; write(rp,result)
        wrapped=dict(result=result,path=str(rp),sha256=pipeline.sha(rp))
        before=self.plumbing.calls
        with patch.object(pipeline,'verify_native',side_effect=self.plumbing.verify), \
                patch.object(pipeline,'run_native',side_effect=AssertionError('Native execution forbidden')), \
                patch.object(execution,'run_native',side_effect=AssertionError('Native execution forbidden')), \
                patch.object(pipeline.checkpoint,'complete_cycle',
                    side_effect=AssertionError('State publication forbidden in board admission controls')), \
                patch.object(self.provider,'draw_record',wraps=self.provider.draw_record) as replay:
            try:
                actual=pipeline.verify_board(wrapped,folder=self.root,index=index,
                    board=self.board if board is None else board,provider=self.provider,
                    native_ids=self.native_ids,context_path=self.context_path,executable=self.executable,
                    limits=self.limits,config=config)
            except (ValueError,KeyError,TypeError,IndexError) as exc:
                if admitted: raise
                if expected_error and expected_error not in str(exc):
                    raise AssertionError('Unexpected refusal '+label+': '+str(exc)) from exc
                self.rejections.append(label)
                disposition=dict(admitted=False,error_type=type(exc).__name__,message=str(exc))
            else:
                if not admitted: raise AssertionError('Accepted invalid board '+label)
                assert actual==self.baseline['record']
                disposition=dict(admitted=True)
            if replay.call_count!=replay_calls:
                raise AssertionError(f'{label}: expected {replay_calls} real replays, got {replay.call_count}')
        self.unchanged()
        evidence=dict(label=label,scope=SCOPE,worker_result_sha256=pipeline.sha(rp),
            genuine_v2_draw_replays=replay_calls,synthetic_receipt_checks=self.plumbing.calls-before,
            state_and_model_unchanged=True,**disposition)
        write(part/'admission-control.json',evidence); self.cases.append(evidence)

    def run(self):
        self.check('valid-complete-frozen-board',admitted=True,replay_calls=1)
        def alter_values(result,part):
            node=next(i for i in self.state.nodes if np.any(self.state.post_slots[i]))
            actor=self.state.specs[node]['actor']; cls=int(np.flatnonzero(self.state.mass[actor]>0)[0])
            action=int(np.flatnonzero(self.state.post_slots[node])[0])
            result['record']['values'][str(node)][cls][action] += .375
            result['record']['values_sha256']=digest(result['record']['values'])
            assert result['record']['values_sha256']==digest(result['record']['values'])
        self.check('altered-finite-values-rehashed',change=alter_values,replay_calls=1,
            expected_error='authenticated native-tree replay')
        sources=list(self.baseline['worker_source_identities'])
        for number,path in enumerate(sources):
            self.check(f'missing-source-{number}',change=lambda r,p,path=path:r['worker_source_identities'].pop(path),
                expected_error='pinned runner')
            self.check(f'changed-source-{number}',change=lambda r,p,path=path:r['worker_source_identities'].update({path:'0'*64}),
                expected_error='pinned runner')
            self.check(f'unpinned-source-{number}',config_change=lambda c,path=path:c['source_identities'].pop(path),
                expected_error='pinned runner')
        simple=[
            ('changed-context','context_sha256','0'*64),('changed-model','model_sha256','0'*64),
            ('changed-registry','registry_sha256','0'*64),('changed-generation','generation',1),
            ('changed-recipe-hash','recipe_sha256','0'*64),('changed-plan-hash','plan_sha256','0'*64),
            ('changed-parent-state','parent_state_sha256','0'*64),
            ('changed-request-document','request_document_sha256','0'*64),
            ('changed-request-bytes-hash','request_sha256','0'*64),
            ('changed-tree-hash','tree_sha256','0'*64),
            ('changed-draw-order','draw_index',1),('changed-worker-pid','pid',424243),
            ('changed-worker-creation','creation_time',99.),('changed-worker-cuda','cuda_visible_devices','0'),
            ('changed-thread-limit','threadpool_limit',2),
            ('timing-initialization-before-creation','initialized_unix',99.),
            ('timing-start-before-initialization','started_unix',100.),
            ('timing-worker-end-before-native-end','terminal_unix',103.),
            ('timing-worker-lifetime-exceeded','worker_seconds',301.),
            ('timing-board-exceeds-worker-lifetime','seconds',5.),
            ('timing-negative-duration','seconds',-1.)]
        for label,key,value in simple:
            self.check(label,change=lambda r,p,key=key,value=value:r.update({key:value}))
        self.check('changed-recipe-document',change=lambda r,p:r['recipe'].update(generation=1))
        self.check('changed-native-source-id',change=lambda r,p:r['native_identities'].update({str(self.executable):'0'*64}))
        self.check('changed-invocation-source-id',change=lambda r,p:r['invocation_identities'].update({str(self.request_path):'0'*64}))
        self.check('changed-runtime-limit',change=lambda r,p:r['runtime_limits'].update(native_timeout_seconds=60))
        self.check('unnormalized-runtime-limits',change=lambda r,p:r['runtime_limits'].pop('max_output_bytes'))
        self.check('changed-record-order',change=lambda r,p:r['record'].update(draw_index=1))
        self.check('wrong-record-board',change=lambda r,p:r['record'].update(board=self.plan['boards'][1]))
        self.check('changed-board-order',change=lambda r,p:r.update(board=list(reversed(self.board))))
        self.check('changed-record-recipe-hash',change=lambda r,p:r['record'].update(policy_recipe_sha256='0'*64))
        self.check('changed-record-tree-hash',change=lambda r,p:r['record'].update(tree_sha256='0'*64))
        self.check('changed-record-model-hash',change=lambda r,p:r['record'].update(model_sha256='0'*64),replay_calls=1)
        self.check('called-with-reordered-board',board=self.plan['boards'][1])
        self.check('called-with-reordered-index',index=1)
        def incomplete_request(result,part):
            req=json.loads(self.request_path.read_bytes());req['hands'][1].pop()
            path=part/'changed-request.json';write(path,req)
            result.update(request_artifact=str(path),request_sha256=pipeline.sha(path),request_document_sha256=digest(req))
        self.check('incomplete-hands-with-recomputed-request-hashes',change=incomplete_request,
            expected_error='complete private domain')
        def reordered_request(result,part):
            req=json.loads(self.request_path.read_bytes());req['hands'][0].reverse();req['hands'][1].reverse()
            path=part/'changed-request.json';write(path,req)
            result.update(request_artifact=str(path),request_sha256=pipeline.sha(path),request_document_sha256=digest(req))
        self.check('reordered-hands-with-recomputed-request-hashes',change=reordered_request,
            expected_error='complete private domain')
        self.unchanged()
        return dict(passed=True,scope=SCOPE,cases=self.cases,refused=self.rejections,
            positive_cases=1,refused_cases=len(self.rejections),complete_private_hands_per_actor=1081,
            genuine_v2_draw_replays=sum(case['genuine_v2_draw_replays'] for case in self.cases),
            expanded_observation_rows=self.observation_count,synthetic_tree_sha256=self.tree_sha,
            synthetic_tree_bytes=self.tree_path.stat().st_size,template_inputs=self.template_inputs,
            input_identities=source_ids(),implementation_sha256=pipeline.sha(pipeline.__file__),
            original_state_sha256=self.original_document['state_sha256'],seconds=time.monotonic()-self.began)


def main(root):
    with threadpool_limits(limits=1):
        controls=AdmissionControls(root)
        result=controls.run()
    write(Path(root)/'result.json',result)
    print(json.dumps({key:result[key] for key in ('passed','positive_cases','refused_cases',
        'genuine_v2_draw_replays','synthetic_tree_bytes','seconds')},sort_keys=True))


if __name__=='__main__':
    output=Path(sys.argv[1]).resolve()
    try: main(output)
    except BaseException as exc:
        if output.is_dir() and not (output/'failure.json').exists():
            write(output/'failure.json',dict(passed=False,scope=SCOPE,error_type=type(exc).__name__,
                message=str(exc),traceback=traceback.format_exc(),input_identities=source_ids()))
        raise
