"""Bounded integer-only source scout; no solver, compiler, GPU or timing."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent
B=H.parents[1]
P=B/'runs/D037-showdown-cache-design/census.py'
# Reuse only the four frozen range-expansion functions and their constants.
tree=ast.parse(P.read_text(encoding='utf-8'))
nodes=[]
for n in tree.body:
    if isinstance(n,ast.FunctionDef) and n.name in {'card','cls','combos','expand'}:nodes.append(n)
    elif isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in {'RANKS','SUITS'} for t in n.targets):nodes.append(n)
ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(P),'exec'),ns)
anchor_path=B/'runs/D033-oracle-anchors/anchors.json'
anchors=json.loads(anchor_path.read_text(encoding='utf-8'))['fixtures']
accepted_path=B/'runs/E020C1/report.json'
accepted=json.loads(accepted_path.read_text(encoding='utf-8'))['results']
rows=[]
def row(name,p,hands,scope):
    degrees=[sum(c in h for h in hands) for c in range(52)]
    assert sum(degrees)==2*len(hands)
    order=sorted(range(52),key=lambda c:(-degrees[c],c))
    old=[max(degrees[i:i+32],default=0) for i in range(0,52,32)]
    new=[max((degrees[c] for c in order[i:i+32]),default=0) for i in range(0,52,32)]
    return {'fixture_id':name,'opponent_player':p,'hands':len(hands),'card_list_lengths':degrees,
      'current_card_order':list(range(52)),'single_proposed_order':order,
      'current_per_warp_max_loop_counts':old,'descending_per_warp_max_loop_counts':new,
      'current_sum_of_warp_maxima':sum(old),'descending_sum_of_warp_maxima':sum(new),
      'structural_delta':sum(old)-sum(new),'same_total_scalar_card_loop_additions':sum(degrees),
      'same_longest_single_card_loop':max(degrees,default=0),'scope':scope}
for fixture in anchors:
    config=fixture['config'];name=fixture['fixture_id']
    assert config==next(x['config'] for x in accepted if x['fixture_id']==name)
    board={ns['card'](config['board'][i:i+2]) for i in range(0,len(config['board']),2)}
    for p,key in enumerate(['range_oop','range_ip']):
        hs=set().union(*(ns['expand'](t) for t in config[key].split(',')))
        hands=sorted(tuple(sorted(h)) for h in hs if not board.intersection(h))
        assert len(hands)==len(set(hands))==fixture['hands'][p]
        rows.append(row(name,p,hands,'Derived from exact archived accepted config with reused frozen parser; hand count matches immutable anchor. Not a native GpuPlan dump.'))
        # Preserve the derived lists, not only aggregate favorable proxy values.
        rows[-1]['derived_root_hand_cards']=hands
board={ns['card'](s) for s in ['Qh','7s','2d','Kc']}
full=[(a,b) for a in range(52) for b in range(a+1,52) if a not in board and b not in board]
assert len(full)==1128
rows.append(row('synthetic_full_range_turn',None,full,'Combinatorial full range after four distinct board cards; not the registered holdout board or a runtime measurement.'))
report={'id':'D055','scope':'SOURCE_ONLY_INTEGER_WORK_PROXY','rows':rows,
 'interpretation':'Sum of per-warp longest scalar card loops is only a divergence proxy. It is not executed instructions, cycles, occupancy, memory transactions, native kernel time or a complete-cycle bound. Per-card addition count/order, longest card loop and total-reach reduction do not change.',
 'proposed_candidate':'One stable descending card-list-length permutation only; no alternative order search.',
 'reference_sha256':{str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in [P,anchor_path,accepted_path]},
 'compiler_native_gpu_executed':False,'performance_measured':False}
with (H/'card-work-proxy.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps([{k:r[k] for k in ['fixture_id','opponent_player','hands','current_per_warp_max_loop_counts','descending_per_warp_max_loop_counts','structural_delta']} for r in rows]))
