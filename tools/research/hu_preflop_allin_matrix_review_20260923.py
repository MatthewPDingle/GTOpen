"""Independently rebuild every matrix cell with outcome-wise scalar sums."""
import json
import math
from pathlib import Path
import time
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read,load_complete_cache
from reboot_research_idle_v1 import idle

PREFIX='preflop-allin-matrix-control-v1'


def classify(cards):
    a,b=cards;ra,rb=a//4,b//4
    return max(ra,rb)*13+min(ra,rb) if ra==rb or a%4==b%4 else min(ra,rb)*13+max(ra,rb)


def main():
    start=time.monotonic();assert idle()
    rp,pp=[OUT/f'{PREFIX}-{s}.json' for s in ('registration','result')]
    reg,result=read(rp),read(pp)
    assert result['passed'] and result['registration_sha256']==sha(rp)
    for p,h in reg['inputs'].items():assert sha(p)==h,p
    assert result['matrix_sha256']==sha(result['matrix_artifact'])
    matrix=read(result['matrix_artifact']);cache=load_complete_cache()
    crp=OUT/'complete-private-allin-cache-v2-registration.json';cr=read(crp);population=read(cr['population'])
    cp=OUT/'bb-context-candidate.json';context=read(cp)
    assert matrix['context_sha256']==sha(cp)==population['context_sha256']
    root=context['nodes'][0];jam=context['nodes'][root['children'][3]]
    folded,called=[context['nodes'][i] for i in jam['children']]
    rake=called['pot']*context['rake_fraction']
    if context['rake_cap']>0:rake=min(rake,context['rake_cap'])
    net=called['pot']-rake;cost=called['invested']
    cells={}
    for i,row in enumerate(population['rows']):
        if i%4096==0:assert idle() and time.monotonic()-start<180
        h=row['private_cards'];b,t=classify(h[:2]),classify(h[2:]);w=row['probability']
        q=cache.rows[tuple(h)];n=q['boards'];assert n==1712304
        bpay=(q['wins']*(net-cost[0])+q['ties']*(net/2-cost[0])-q['losses']*cost[0])/n
        tpay=(q['losses']*(net-cost[1])+q['ties']*(net/2-cost[1])-q['wins']*cost[1])/n
        cell=cells.setdefault((b,t),[[],[],[]]);cell[0].append(w);cell[1].append(w*bpay);cell[2].append(w*tpay)
    expected=[[[0.]*169 for _ in range(169)] for _ in range(3)];error=0.
    for b in range(169):
        for t in range(169):
            cell=cells.get((b,t),[[],[],[]])
            for k,field in enumerate(('class_mass','bb_showdown_entries','btn_showdown_entries')):
                value=math.fsum(cell[k]);expected[k][b][t]=value
                error=max(error,abs(value-matrix[field][b][t]))
    assert error<1e-11
    M,B,T=expected;mass=[math.fsum(r) for r in M]
    bb_fold=context['nodes'][root['children'][0]]['leaf']['utilities'][0]
    assert matrix['bb_fold']==bb_fold and matrix['bb_uncontested']==folded['leaf']['utilities'][0] and matrix['btn_fold']==folded['leaf']['utilities'][1]
    endpoint=read(OUT/'exhaustive-btn-response-v2-result.json');pairs={}
    for name in ('combined_269','visible_302'):
        path=endpoint['candidates'][name]['policy_artifact'];assert reg['inputs'][path]==sha(path)
        p=read(path);pairs[name]=(p['root_probabilities'],[0. if x is None else x for x in p['btn_call_probabilities']])
    pairs['zero-jam']=([[.5,.25,.25,0.]]*169,[0.]*169)
    pairs['all-jam']=([[0.,0.,0.,1.]]*169,[1.]*169)
    checks={}
    for bn,(bp,_) in pairs.items():
        for tn,(_,tp) in pairs.items():
            bg=[];tg=[]
            for c in range(169):
                f=mass[c]*bb_fold
                j=math.fsum(M[c][t]*(1-tp[t])*folded['leaf']['utilities'][0]+B[c][t]*tp[t] for t in range(169))
                bg.append((j-f)*bp[c][0] if j>f else (f-j)*bp[c][3])
                reach=math.fsum(M[b][c]*bp[b][3] for b in range(169))
                call=math.fsum(T[b][c]*bp[b][3] for b in range(169));fold=reach*folded['leaf']['utilities'][1]
                tg.append((call-fold)*(1-tp[c]) if call>fold else (fold-call)*tp[c])
            gains=dict(bb_gain=math.fsum(bg),btn_gain=math.fsum(tg));old=result['cross_pairings'][f'{bn}/{tn}']
            for k,v in gains.items():error=max(error,abs(v-old[k]))
            checks[f'{bn}/{tn}']=gains
    assert error<1e-9 and len(checks)==16
    for p,h in reg['inputs'].items():assert sha(p)==h,p
    assert idle() and time.monotonic()-start<180
    audit=dict(passed=True,registration_sha256=sha(rp),result_sha256=sha(pp),reviewer_sha256=sha(Path(__file__)),
        matrix_sha256=sha(result['matrix_artifact']),all_matrix_cells_reconstructed=3*169*169,
        canonical_pairs_reconstructed=len(population['rows']),maximum_scalar_error_bb=error,pairings=checks,
        seconds=time.monotonic()-start,gpu_used=False,production_modified=False,accuracy_qualified=False)
    save(OUT/f'{PREFIX}-independent-review.json',audit)
    print({k:v for k,v in audit.items() if k!='pairings'})


if __name__=='__main__':main()
