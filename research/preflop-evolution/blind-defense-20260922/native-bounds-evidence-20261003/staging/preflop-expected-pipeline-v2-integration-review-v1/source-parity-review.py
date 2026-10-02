"""AST-only inverse proof of the prospective pipeline integration changes.

No pipeline module is imported and no model/collection/fit/native call occurs.
The inverse removes only independently checked transport/provenance changes.
"""
import ast
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STAGE = ROOT.parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tree(name):
    return ast.parse((STAGE / name).read_text())


def assignment(module, name):
    found = [node for node in ast.walk(module) if isinstance(node, ast.Assign)
             and any(isinstance(target, ast.Name) and target.id == name for target in node.targets)]
    assert len(found) == 1, (name, len(found))
    return found[0]


def function(module, name):
    return next(n for n in module.body if isinstance(n, ast.FunctionDef) and n.name == name)


def expressions_equal(a, source):
    assert ast.dump(a) == ast.dump(ast.parse(source, mode='eval').body), ast.unparse(a)


def run():
    previous = STAGE / 'preflop_expected_training_pipeline_v1.py'
    current = STAGE / 'preflop_expected_training_pipeline_v2.py'
    assert sha(current) == '499a828901ed2a12b26680b1accfea73f4ca6eee527088ac9fb86a266ac3536d'
    original, new = tree(previous.name), tree(current.name)
    board = tree('preflop_expected_board_workers_v2.py')
    river = tree('preflop_expected_river_workers_v2.py')
    execution = tree('preflop_expected_native_execution_v2.py')
    result_fields = ast.literal_eval(assignment(new, 'BOARD_RESULT_FIELDS').value)
    produced = assignment(function(board, 'complete'), 'result').value
    assert len(result_fields) == 33 and result_fields == {k.arg for k in produced.keywords}
    verify_signature = function(execution, 'verify_native').args
    required = [arg.arg for arg, default in zip(verify_signature.kwonlyargs, verify_signature.kw_defaults) if default is None]
    assert required == ['executable', 'arguments', 'expected_identities', 'timeout', 'max_output_bytes']
    assert ast.literal_eval(assignment(river, 'MAX_NATIVE_OUTPUT_BYTES').value) == 64_000_000
    collection = function(new, 'collect')
    arguments = assignment(collection, 'query_arguments')
    outputs = assignment(collection, 'query_outputs')
    expressions_equal(arguments.value,
        "['queries',str(context_path),str(bp),'-',str(qp),'--output-byte-limit='+str(river_workers_api.MAX_NATIVE_OUTPUT_BYTES)]")
    expressions_equal(outputs.value, '[dict(path=str(qp),argument_index=5)]')
    run_call = next(n for n in ast.walk(collection) if isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Name) and n.func.id == 'run_native')
    verify_call = next(n for n in ast.walk(collection) if isinstance(n, ast.Call)
                       and isinstance(n.func, ast.Name) and n.func.id == 'verify_native')
    assert ast.unparse(run_call.args[1]) == 'query_arguments'
    run_kwargs = {k.arg: k.value for k in run_call.keywords}
    verify_kwargs = {k.arg: k.value for k in verify_call.keywords}
    for field in ('expected_identities', 'timeout', 'max_output_bytes', 'direct_outputs'):
        assert ast.dump(run_kwargs[field]) == ast.dump(verify_kwargs[field]), field
    expressions_equal(run_kwargs['max_output_bytes'], 'river_workers_api.MAX_NATIVE_OUTPUT_BYTES')
    expressions_equal(run_kwargs['direct_outputs'], 'query_outputs')
    expressions_equal(verify_kwargs['arguments'], 'query_arguments')
    expressions_equal(verify_kwargs['executable'], "native['bridge']")
    statements = [n for n in ast.walk(collection) if isinstance(n, ast.For) and
                  isinstance(n.target, ast.Tuple) and ast.unparse(n.target) == '(chunk, start)']
    assert len(statements) == 1
    body = statements[0].body
    invoke_index = next(i for i,n in enumerate(body) if isinstance(n, ast.Assign) and
                        isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name) and n.value.func.id == 'run_native')
    assert isinstance(body[invoke_index+1], ast.Expr) and body[invoke_index+1].value is verify_call
    assert 'json.loads(qp.read_bytes())' == ast.unparse(body[invoke_index+2].value)
    board_verify = function(new, 'verify_board')
    checked_native = next(n for n in ast.walk(board_verify) if isinstance(n, ast.Call)
                          and isinstance(n.func, ast.Name) and n.func.id == 'verify_native')
    board_kwargs = {k.arg:k.value for k in checked_native.keywords}
    expressions_equal(board_kwargs['arguments'],
        "[str(Path(context_path).resolve()),str(request_path),'--output-byte-limit='+str(limits['max_output_bytes'])]")
    expressions_equal(board_kwargs['timeout'], "limits['native_timeout_seconds']")
    expressions_equal(board_kwargs['max_output_bytes'], "limits['max_output_bytes']")
    expressions_equal(board_kwargs['direct_outputs'], '()')

    reverted = copy.deepcopy(new)
    reverted.body.remove(assignment(reverted, 'BOARD_RESULT_FIELDS'))
    assignment(reverted, 'METHOD').value = ast.Constant('typed-all-node-native-joint-cycle-v1')
    versions = {'preflop_expected_board_workers_v2':'preflop_expected_board_workers_v1',
                'preflop_expected_river_workers_v2':'preflop_expected_river_workers_v1',
                'preflop_expected_native_execution_v2':'preflop_expected_native_execution_v1'}
    class Versions(ast.NodeTransformer):
        def visit_Import(self, node):
            for alias in node.names:
                alias.name = versions.get(alias.name, alias.name)
            return node
        def visit_ImportFrom(self, node):
            node.module = versions.get(node.module, node.module)
            return node
        def visit_Constant(self, node):
            if isinstance(node.value, str) and node.value in versions:
                node.value = versions[node.value]
            return node
    reverted = Versions().visit(reverted)
    ver = function(reverted, 'verify_board')
    messages = ('Complete v2 board worker envelope required', 'Complete v2 board worker schema and provenance required')
    removed = [statement for statement in ver.body if isinstance(statement, ast.If) and
               any(isinstance(n, ast.Constant) and n.value in messages for n in ast.walk(statement))]
    assert len(removed) == 2
    for statement in removed:
        ver.body.remove(statement)
    native = next(n for n in ast.walk(ver) if isinstance(n, ast.Call) and
                  isinstance(n.func, ast.Name) and n.func.id == 'verify_native')
    native.keywords = [k for k in native.keywords if k.arg not in ('timeout', 'max_output_bytes', 'direct_outputs')]
    next(k.value for k in native.keywords if k.arg == 'arguments').elts.pop()

    col = function(reverted, 'collect')
    class RevertQuery(ast.NodeTransformer):
        def visit_Assign(self, node):
            if any(isinstance(t, ast.Name) and t.id in ('query_arguments','query_outputs') for t in node.targets):
                return None
            return self.generic_visit(node)
        def visit_Expr(self, node):
            if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == 'verify_native':
                return None
            return self.generic_visit(node)
        def visit_Call(self, node):
            if isinstance(node.func, ast.Name) and node.func.id == 'run_native':
                node.args[1] = copy.deepcopy(arguments.value)
                node.args[1].elts.pop()
                node.keywords = [k for k in node.keywords if k.arg not in ('max_output_bytes','direct_outputs')]
            return self.generic_visit(node)
    RevertQuery().visit(col)
    upd = function(reverted, 'update')
    output = assignment(upd, 'result').value
    next(k for k in output.keywords if k.arg == 'format').value = ast.Constant(1)
    assert ast.dump(reverted, include_attributes=False) == ast.dump(original, include_attributes=False), 'Unregistered pipeline behavior difference'
    proofs = {}
    for name in ('wait','verify_sources','identities','_artifact_ref','_read','verify_board','collect','update'):
        left, right = function(original,name), function(reverted,name)
        assert ast.dump(left) == ast.dump(right)
        proofs[name] = hashlib.sha256(ast.dump(left).encode()).hexdigest()
    source_paths = [previous,current,ROOT/'pipeline_board_admission_check_v2.py',
                   STAGE/'preflop_expected_board_workers_v1.py',STAGE/'preflop_expected_board_workers_v2.py',
                   STAGE/'preflop_expected_river_workers_v1.py',STAGE/'preflop_expected_river_workers_v2.py',
                   STAGE/'preflop_expected_native_execution_v1.py',STAGE/'preflop_expected_native_execution_v2.py',
                   STAGE/'preflop_expected_training_fit_v1.py',STAGE/'preflop_expected_training_checkpoint_v1.py',
                   STAGE/'preflop_expected_pipeline_board_admission_check_v1.py',
                   STAGE/'preflop_expected_policy_v1.py',STAGE/'preflop_expected_native_targets_v2.py',
                   STAGE/'preflop_expected_native_targets_v1.py']
    return dict(passed=True, complete_inverse_ast_equal=True, original_calculation_functions=proofs,
                coordinator_query_output_argv_index=5, coordinator_query_aggregate_cap=64_000_000,
                run_and_verify_arguments_match=True, explicit_verify_precedes_query_read=True,
                board_schema_fields=sorted(result_fields), board_schema_matches_v2_worker=True,
                verifier_required_keywords=required, source_identities={str(p):sha(p) for p in source_paths},
                model_collection_fit_checkpoint_rng_math_unchanged=True,
                scope='Source parity only; no runtime/native execution and no poker accuracy qualification.')


if __name__ == '__main__':
    report = run()
    report['review_source_sha256'] = sha(__file__)
    with (ROOT/'source-parity-result.json').open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(report,stream,sort_keys=True,indent=2)
        stream.write('\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('source_identities','board_schema_fields','original_calculation_functions')}))
