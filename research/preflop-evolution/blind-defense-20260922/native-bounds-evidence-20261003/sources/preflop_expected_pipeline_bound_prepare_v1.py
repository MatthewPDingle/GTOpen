"""Prepare a separate bounded-export pipeline; no imports or execution."""
from pathlib import Path
import hashlib
import json
import difflib
import ast

STAGE=Path(__file__).resolve().parent
OLD=STAGE/'preflop_expected_training_pipeline_v1.py'
NEW=STAGE/'preflop_expected_training_pipeline_v2.py'
EVIDENCE=STAGE/'native-bounded-pipeline-source-preparation-v1'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def once(text,old,new):
    if text.count(old)!=1:raise ValueError('Expected exact source transformation')
    return text.replace(old,new)
def main():
    if NEW.exists() or EVIDENCE.exists():raise FileExistsError('Separate preparation namespace exists')
    original=OLD.read_text();text=original
    for old,new in [('preflop_expected_board_workers_v1','preflop_expected_board_workers_v2'),
        ('preflop_expected_river_workers_v1','preflop_expected_river_workers_v2'),
        ('preflop_expected_native_execution_v1','preflop_expected_native_execution_v2'),
        ('typed-all-node-native-joint-cycle-v1','typed-all-node-native-joint-cycle-v2')]:text=text.replace(old,new)
    text=once(text,
        'arguments=[str(Path(context_path).resolve()),str(request_path)], expected_identities=invocation_ids)',
        'arguments=[str(Path(context_path).resolve()),str(request_path),\n            "--output-byte-limit="+str(limits["max_output_bytes"])], expected_identities=invocation_ids,\n        timeout=limits["native_timeout_seconds"],max_output_bytes=limits["max_output_bytes"],direct_outputs=())')
    text=once(text,
        "invocation=run_native(native['bridge'],['queries',str(context_path),str(bp),'-',str(qp)],\n                    folder=part,label='native-queries',expected_identities=invoke_ids,guard=guard,\n                    timeout=runtime_limits['river']['native_timeout_seconds'])",
        "query_arguments=['queries',str(context_path),str(bp),'-',str(qp),\n                    '--output-byte-limit='+str(river_workers_api.MAX_NATIVE_OUTPUT_BYTES)]\n                query_outputs=[dict(path=str(qp),argument_index=5)]\n                invocation=run_native(native['bridge'],query_arguments,\n                    folder=part,label='native-queries',expected_identities=invoke_ids,guard=guard,\n                    timeout=runtime_limits['river']['native_timeout_seconds'],\n                    max_output_bytes=river_workers_api.MAX_NATIVE_OUTPUT_BYTES,direct_outputs=query_outputs)\n                verify_native(invocation,executable=native['bridge'],arguments=query_arguments,\n                    expected_identities=invoke_ids,timeout=runtime_limits['river']['native_timeout_seconds'],\n                    max_output_bytes=river_workers_api.MAX_NATIVE_OUTPUT_BYTES,direct_outputs=query_outputs)")
    text=once(text,'result=dict(format=1,method=METHOD,completed_cycles=',
        'result=dict(format=2,method=METHOD,completed_cycles=')
    ast.parse(text)
    EVIDENCE.mkdir()
    with NEW.open('x',encoding='utf-8',newline='\n') as file:file.write(text)
    (EVIDENCE/OLD.name).write_bytes(OLD.read_bytes());(EVIDENCE/NEW.name).write_bytes(NEW.read_bytes())
    diff=''.join(difflib.unified_diff(original.splitlines(True),text.splitlines(True),fromfile=OLD.name,tofile=NEW.name))
    (EVIDENCE/'pipeline.diff').write_text(diff,encoding='utf-8')
    result=dict(prepared=True,executed=False,original=dict(path=str(OLD),sha256=sha(OLD)),new=dict(path=str(NEW),sha256=sha(NEW)),
        changes='V2 owned execution and worker imports; explicit cap argument/bounds/direct query path; v2 source provenance and metrics version. All collection/math/fit/checkpoint/RNG code unchanged.',
        scientific_accuracy_qualified=False)
    (EVIDENCE/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
