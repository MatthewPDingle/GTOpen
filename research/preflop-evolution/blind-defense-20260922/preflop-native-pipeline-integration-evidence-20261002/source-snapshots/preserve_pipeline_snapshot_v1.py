"""Recover exactly the authenticated pre-cancellation software-test source."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
source=ROOT/'preflop_expected_training_pipeline_v1.py'
proof=json.loads((ROOT/'preflop-expected-pipeline-control-v2-362/result.json').read_bytes())
expected=proof['input_identities'][str(source.resolve())]
text=source.read_text(encoding='utf-8')
text=text.replace('import multiprocessing as mp\n','').replace('from preflop_expected_worker_cancellation_v1 import coordinated_pool\n','')
new="""    cancellation=mp.get_context('spawn').Event()
    with coordinated_pool(board_pool(board_workers,payload=payload,context_path=context_path,executable=native['board'],
            folder=board_folder,expected_native_identities=board_ids,runtime_limits=runtime_limits['board'],
            cancel_event=cancellation),cancellation) as boards:"""
old="""    with board_pool(board_workers,payload=payload,context_path=context_path,executable=native['board'],
            folder=board_folder,expected_native_identities=board_ids,runtime_limits=runtime_limits['board']) as boards:"""
assert new in text
text=text.replace(new,old)
text=text.replace('with coordinated_pool(river_pool(workers,context_path=context_path,cache=cache,targets=targets,',
                  'with river_pool(workers,context_path=context_path,cache=cache,targets=targets,')
text=text.replace("runtime_limits=runtime_limits['river'],cancel_event=cancellation),cancellation) as rivers:",
                  "runtime_limits=runtime_limits['river']) as rivers:")
raw=text.encode('utf-8'); actual=hashlib.sha256(raw).hexdigest()
assert actual==expected,(actual,expected)
target=ROOT/'preflop_expected_training_pipeline_v1-pre-cancellation-snapshot.py'
with target.open('xb') as stream: stream.write(raw)
print(json.dumps(dict(preserved=str(target),sha256=actual,source_unchanged=True)))
