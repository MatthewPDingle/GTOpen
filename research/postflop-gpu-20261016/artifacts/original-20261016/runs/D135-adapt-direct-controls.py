"""Reuse the unchanged physical showdown raw corpus for E084."""
from pathlib import Path
import ast
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
source=R/'runs/E082-prepare-direct.py'
target=R/'runs/E084-prepare-direct.py'
assert not target.exists()
t=source.read_text().replace('E082','E084')
t=t.replace('pass_compiled_prefix_consumer_prerequisites','pass_compiled_first_card_total_prerequisites')
t=t.replace('D133-readonly-prefix-consumers/algebra-and-ownership-control.json','D135-first-card-total/ordered-sum-control.json')
t=t.replace('D133-readonly-prefix-consumers/history.json','D135-first-card-total/history.json')
t=t.replace('independent-prefix-consumer','first-card-total-cache')
t=t.replace('prefix_consumer_raw_equivalence','first_card_total_raw_equivalence')
t=t.replace('prefix/synchronization','first-card-total/synchronization')
t=t.replace('prefix_consumer','first_card_total')
ast.parse(t)
target.write_text(t,encoding='utf-8',newline='\n')
print(target,flush=True)
