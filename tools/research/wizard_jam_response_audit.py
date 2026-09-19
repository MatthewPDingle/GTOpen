"""Fixed-policy local best responses with compatible cards; no full-game claim."""
import numpy as np
import wizard_continuation_study as s


def run():
    out=s.OUT/'jam-response-audit.json';assert not out.exists(),'Preserve evidence'
    audit=s.read(s.OUT/'premium-branches.json');root=[1,2,0,0,0,0,0,0]
    node=lambda suffix:next(n for n in audit['nodes'] if n['path']==root+suffix)
    case,=s.read(s.OUT/'fourbet-call/fixtures.json')['cases'];labels=[h['hand'] for h in case['balanced']['hands'][0]]
    pairs=[(a,b) for a in range(52) for b in range(a+1,52)]
    masks=np.array([(1<<a)|(1<<b) for a,b in pairs],dtype=np.uint64)
    cls=np.array([max(a//4,b//4)*13+min(a//4,b//4) if a%4==b%4 or a//4==b//4 else min(a//4,b//4)*13+max(a//4,b//4) for a,b in pairs])
    counts=np.zeros((169,169));a,b=np.where((masks[:,None]&masks[None,:])==0);np.add.at(counts,(cls[a],cls[b]),1)
    combos=np.bincount(cls,minlength=169);assert counts.sum()==1326*1225
    eq=np.frombuffer((s.ROOT/'cache/preflop_eq169.bin').read_bytes()[4:],dtype='<f4').reshape(169,169).astype(float)
    eq=(eq+1-eq.T)/2;np.fill_diagonal(eq,.5)
    hero=np.array(node([])['view']['reaches_all'][1]);opp=np.array(node([])['view']['reaches_all'][2])
    strategy=np.array(node([])['view']['strategy']).reshape(4,169)
    saved_call=np.array(node([3])['view']['strategy']).reshape(2,169)[1]
    reach=hero*strategy[3];independent=reach*combos;independent/=independent.sum()
    independent_ev=397.5*(independent@(1-eq))-182
    errors=[]
    for h in node([3])['selected_action_values']:
        errors.append(abs(independent_ev[labels.index(h['hand'])]-h['action_ev_bb'][1]))
    assert max(errors)<.0001
    rows=[];curve=[]
    for transfer in np.linspace(0,strategy[3,168],101):
        policy=strategy[3].copy();policy[168]-=transfer
        assert policy.min()>-1e-12
        mass=counts*(hero*policy)[:,None]
        equity=(mass*(1-eq)).sum(axis=0)/mass.sum(axis=0)
        ev=397.5*equity-182;best=(ev>0).astype(float)
        live_mass=mass.sum(axis=0)*opp;live_mass/=live_mass.sum()
        aa_mass=counts[168]*opp;aa_mass/=aa_mass.sum()
        aa_value=lambda response:float(aa_mass@((1-response)*27.5+response*(397.5*eq[168]-194)))
        curve.append(dict(aa_jam_to_call_transfer=float(transfer),aa_jam_probability=float(policy[168]),
            aa_call_probability=float(strategy[1,168]+transfer),aa_fourbet_probability=float(strategy[2,168]),
            aa_jam_ev_vs_local_best_response=aa_value(best),aa_jam_ev_vs_saved_response=aa_value(saved_call),
            local_response_gain_bb=float(live_mass@(np.maximum(ev,0)-saved_call*ev))))
        if transfer==0:
            for i,h in enumerate(labels):
                rows.append(dict(hand=h,entering_weight=float(opp[i]),independent_call_ev_bb=float(independent_ev[i]),
                    compatible_call_ev_bb=float(ev[i]),saved_call_probability=float(saved_call[i]),
                    local_best_call_probability=float(best[i]),response_loss_bb=float(max(ev[i],0)-saved_call[i]*ev[i])))
    s.write(out,dict(hand_results=rows,aa_transfer_curve=curve,reconstruction_max_error_bb=max(errors),
        source_hashes={p.relative_to(s.ROOT).as_posix():s.sha(p) for p in [s.OUT/'premium-branches.json',s.ROOT/'cache/preflop_eq169.bin',s.ROOT/'tools/research/wizard_jam_response_audit.py']},
        limitations='Local response only under frozen entering/raising policies. Two-hand compatibility exact; class equity sampled; six folded players omitted. Tiny edges can change with equity error. Transferring AA jam to call preserves AA probabilities but does not re-solve postflop or competing 4-bet responses. Not a new equilibrium or Wizard replication.'))
    print('Local gain',curve[0]['local_response_gain_bb'],'AA jam value',curve[0]['aa_jam_ev_vs_local_best_response'])
    for r in rows:
        if r['hand'] in ['AA','KK','QQ','JJ','AKs','AKo','AQs','AJs','ATs','KQs']:print(r)


if __name__=='__main__':run()
