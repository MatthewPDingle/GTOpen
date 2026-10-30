"""Prepare E086 build/timing bookkeeping for its passed chance corpus."""
import ast
from pathlib import Path
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
for name in ['prepare-build.py','freeze-primary.py']:
    p=R/('runs/E085-'+name);out=R/('runs/E086-'+name)
    assert not out.exists()
    t=p.read_text().replace('E085','E086').replace('e085','e086').replace('V085','V086')
    pairs=[
        ('E086-resource-r2','E086-resource'),
        ('E086-kernel-control-root-check','E086-kernel-control'),
        ('pass_scoped_up_action_raw_equivalence','pass_scoped_chance_raw_equivalence'),
        ('actual_device_inputs_retained_both_arms','actual_immutable_images_preserved'),
        ("assert q['all_parent_child_cfv_rows_disjoint'] and q['kernel_launches']==1638","assert q['kernel_launches']==850"),
        (" and control['all_parent_child_cfv_rows_disjoint']",''),
        ('D136-strategy-streaming-store','D137-bitfield-membership'),
        ('819','425'),('1638','850'),('63899','2508695'),
        ('62to56registers, local64/static0/dynamic0, maxthreads1024, theoretical128thread residency8to9','30registers,local0/static0/dynamic0,maxthreads1024,theoretical128thread residency12 unchanged'),
        ('raw action','raw chance'),('action outputs','chance outputs'),
        ('B281','B284'),('B282','B285'),('B283','B286'),
    ]
    for a,b in pairs:t=t.replace(a,b)
    assert 'all_parent_child_cfv_rows_disjoint' not in t
    ast.parse(t);out.write_text(t,encoding='utf-8',newline='\n')
    print(out,flush=True)
