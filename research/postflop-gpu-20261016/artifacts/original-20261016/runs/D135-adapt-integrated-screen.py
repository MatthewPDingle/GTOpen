"""Prepare fixed E084 integration scripts from the established screen."""
from pathlib import Path
import ast
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
replacements={
    'E082':'E084', 'e082':'e084',
    'prefix_consumer_raw_equivalence':'first_card_total_raw_equivalence',
    'D133-prepare-prefix-consumers.py':'D135-prepare-first-card-total.py',
    'D133-readonly-prefix-consumers':'D135-first-card-total',
    "['direct','raw-replay']":"['direct','audit']",
    'unchanged38registers/local0/static1040/worst dynamic22600/maxthreads1024/residency':'38to39registers/local0/static1040/worst dynamic22600/maxthreads1024/residency unchanged',
    'resources equal.':'shared/local allocation and occupancy limits unchanged, registers38to39.',
    "'B275'":"'B278'", "'B276'":"'B279'", "'B277'":"'B280'",
    'B275/E084R1, E084R2/B276, B277/E084R3':'B278/E084R1, E084R2/B279, B280/E084R3',
}
for name in ['prepare-final-build.py','freeze-primary.py']:
    source=R/('runs/E082-'+name)
    target=R/('runs/E084-'+name)
    assert not target.exists()
    t=source.read_text()
    for a,b in replacements.items():t=t.replace(a,b)
    ast.parse(t)
    target.write_text(t,encoding='utf-8',newline='\n')
    print(target,flush=True)
