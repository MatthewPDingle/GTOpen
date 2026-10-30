"""Own the one fixed compiled host-tag control execution."""
from pathlib import Path
import sys
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
H=R/'runs/E077-plan-control';M=R/'runs/E077-host-manager';old.custody();assert not M.exists()and not(R/'gpu-run.lock').exists();M.mkdir()
old.child([sys.executable,'-B',str(H/'execute.py'),old.sha(H/'protocol.json')],M,'host',old.env(),1800)
q=old.read(H/'report.json');assert q['status']=='pass_compiled_prefix_tags_against_retained_model'and len(q['cases'])==12
old.custody();print('E077 host control terminal:12 maps and3 tests pass.',flush=True)
