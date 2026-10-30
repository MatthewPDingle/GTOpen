import ast, json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
script = ROOT / 'runs/D306-normal-division-PTX.py'
tree = ast.parse(script.read_text(encoding='utf-8'))
function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'inspect')
namespace = {'re': re}
exec(compile(ast.Module(body=[function], type_ignores=[]), str(script), 'exec'), namespace)
failures = []
for arch in ['compute_120', 'compute_75']:
    for name in ['down_action', 'up_action']:
        path = ROOT / 'runs/E124-resource/execution' / ('candidate-' + arch + '-' + name + '.ptx.txt')
        try:
            namespace['inspect'](path.read_text(encoding='utf-8'))
        except (AssertionError, KeyError) as error:
            trace = error.__traceback__
            while trace.tb_next:
                trace = trace.tb_next
            frame = trace.tb_frame.f_locals
            index = frame.get('index', 0)
            items = frame.get('items', [])
            failures.append({'section': arch + ':' + name, 'reader_line': trace.tb_lineno,
                             'error': repr(error), 'item_index': index,
                             'context': items[max(0, index - 9):index + 7]})
h.save(ROOT / 'runs/D306-normal-division-PTX/reader-v1-failure.json', {'at': h.now(),
    'script_sha256': h.sha(script), 'protocol_sha256': h.sha(ROOT / 'runs/D306-normal-division-PTX/protocol.json'),
    'failures': failures, 'new_compiler_GPU_module_kernel_solver_or_speed_samples': 0})
print(json.dumps(failures, indent=2), flush=True)
