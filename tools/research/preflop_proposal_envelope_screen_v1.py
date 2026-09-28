"""Cheap deterministic planning screen; not a new accuracy evaluation."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import copy
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
from board_prefix_publication_v1 import atomic_json
from preflop_allin_matrix_v1 import AllinMatrix
from complete_preflop_decomposition_v1 import tables,reaches,integrated_preflop,physical_preflop,POSTFLOP
from crossed_complete_policy_comparison_v1 import PAIRS,PROFILE_NAMES,CONTRAST_NAMES
from sampled_physical_root_evaluation_v1 import hand_class
from bounded_parallel_evaluation_archive_v2 import production_available

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='preflop-proposal-envelope-screen-v1';REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json')
FOLDER=OUT/NAME;PLAN=OUT/'PREFLOP-PROPOSAL-ENVELOPE-SCREEN-PLAN.md'
SOURCE=Path('S:/GTOpen-research/weighted-complete-river-continuation-v1')
EXPORT='complete-preflop-bank-export-control-v1'
CONTEXT=OUT/'bb-context-candidate.json';MATRIX=OUT/'preflop-allin-matrix-control-v1-matrix.json'
EXE=ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe'
PATHS={2:{0:1},5:{0:2,3:1},8:{0:2,3:2,6:1}}
CONTRASTS=((2,0,0),(3,1,0),(1,0,1),(3,2,1),(6,4,0),(7,5,0),(5,4,1),(7,6,1))


def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    start=time.monotonic();assert not any(p.exists() for p in (REG,RESULT,FOLDER)),'Preserve earlier attempts'
    export_result=OUT/(EXPORT+'-result.json');export_reg=OUT/(EXPORT+'-registration.json')
    proof=read(export_result);assert proof['passed'] and proof['complete'] and proof['registration_sha256']==sha(export_reg)
    cfg=read(export_reg)
    for p,h in cfg['inputs'].items():assert sha(p)==h,p
    assert sha(CONTEXT)==cfg['inputs'][str(CONTEXT)] and sha(MATRIX)==cfg['inputs'][str(MATRIX)]
    transport_proof=SOURCE/'evaluation-transport-control.json';prior=read(transport_proof)
    assert prior['passed'] and prior['new_test_deals']==0
    assert prior['bank_identities_sha256']==sha(SOURCE/'bank-identities.json')
    original_reg=read(OUT/'river-matched-continuation-v1-registration.json')
    assert sha(EXE)==original_reg['inputs'][str(EXE)]
    for p,h in prior['artifacts'].items():assert sha(SOURCE/p)==h,p
    artifacts={Path(p).name:SOURCE/p for p in prior['artifacts']}
    paths=[Path(__file__),PLAN,export_result,export_reg,CONTEXT,MATRIX,EXE,transport_proof,*artifacts.values(),
        ROOT/'crates/solver/examples/hu_sampled_profile_allin_evaluation_v1.rs']
    banks=[]
    for row in proof['banks']:
        assert sha(row['file'])==row['sha256'];paths.append(Path(row['file']));banks.append(read(row['file']))
    for module in list(sys.modules.values()):
        p=getattr(module,'__file__',None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix=='.py':paths.append(Path(p))
    inputs={str(p):sha(p) for p in paths}
    atomic_json(REG,dict(inputs=inputs,new_poker_deals=0,gpu_used=False,maximum_seconds=180,
        maximum_output_bytes=4_000_000,proposed_payoff_bounds=[-200.,200.5],
        validation='Reconstruct all eight frozen profiles on the retained training transport. Native forced-leaf values isolate each postflop continuation; recombine with independently propagated preflop reach and chip ledger.',
        purpose='Planning screen for envelope width, not a qualified floating sampler or new confidence interval.'))
    context=read(CONTEXT);matrix=AllinMatrix(read(MATRIX),CONTEXT.read_text())
    assert context['config']['stack']==200. and context['dead_money']==.5
    source_tables=[tables(context,b,matrix) for b in banks]
    profiles=[];reach=[];terminal=[];flop=[]
    for seed in range(2):
        for bb,btn in PAIRS:
            p={n:source_tables[2*seed+(bb if context['nodes'][n]['actor']==0 else btn)][n] for n in source_tables[0]}
            profiles.append(p);r=reaches(context,p);reach.append(r)
            terminal.append(integrated_preflop(context,matrix,r));flop.append(sum(r[n] for n in POSTFLOP))
    # Reuse actual retained full-policy transport. Forcing only preflop choices
    # exposes each existing postflop conditional value without changing its policy.
    old=read(artifacts['profiles.json']);query=read(artifacts['queries.json']);batch=read(artifacts['conditional-batch.json'])
    assert len(batch['deals'])==1 and [p['name'] for p in old['profiles']]==list(PROFILE_NAMES)
    assert old['batch_source']==artifacts['conditional-batch.json'].read_text()
    assert old['context_source']==query['context_source']==CONTEXT.read_text()
    forced=[];policy_error=0.;seen=set()
    for i,profile in enumerate(old['profiles']):
        assert len(profile['policies'])==len(query['observations'])
        for o,row in zip(query['observations'],profile['policies']):
            assert (o['hi'],o['lo'],o['actor'],o['n'])==(row['hi'],row['lo'],row['actor'],row['n'])
            if o['phase']!=0:continue
            lo=int(o['lo']);cls=hand_class([lo&63,(lo>>6)&63]);node=int(o['hi'])-1
            policy_error=max(policy_error,float(np.max(abs(profiles[i][node][cls]-row['probabilities']))));seen.add(node)
        for leaf in POSTFLOP:
            new=copy.deepcopy(profile);new['name']=profile['name']+':forced-'+str(leaf)
            for o,row in zip(query['observations'],new['policies']):
                node=int(o['hi'])-1
                if o['phase']==0 and node in PATHS[leaf]:
                    row['probabilities']=[float(a==PATHS[leaf][node]) for a in range(4)]
            forced.append(new)
    assert seen=={0,3,6,9,12} and policy_error<1e-10
    FOLDER.mkdir();transport=FOLDER/'forced-leaf-profiles.json';native=FOLDER/'native-forced-leaves.json'
    atomic_json(transport,dict(old,profiles=[*old['profiles'],*forced]))
    assert production_available(),'An active solve has priority'
    run=subprocess.run([str(EXE),str(CONTEXT),str(artifacts['conditional-batch.json']),str(transport),str(native)],
        capture_output=True,text=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
    assert run.returncode==0,run.stderr[-2000:]
    result=read(native);assert len(result['profiles'])==32
    assert result['maximum_forward_cashflow_error']<1e-10 and result['maximum_conservation_error']<1e-10
    lookup={p['name']:np.asarray(p['deals'][0]['values']) for p in result['profiles']}
    cards=batch['deals'][0];classes=hand_class(cards[:2]),hand_class(cards[2:4])
    label=batch['allin_counts'][0];assert label['private_cards']==cards[:4]
    equity=(label['wins']+.5*label['ties'])/label['boards'];errors=[]
    for i,name in enumerate(PROFILE_NAMES):
        t=physical_preflop(context,reach[i],*classes,equity)
        recombined=t.copy()
        for leaf in POSTFLOP:
            value=lookup[name+':forced-'+str(leaf)]
            assert np.all(value>=-200.) and np.all(value<=200.5)
            recombined+=reach[i][leaf][classes]*value
        error=float(np.max(abs(recombined-lookup[name])));assert error<1e-10
        errors.append(dict(profile=name,maximum_absolute_error=error,postflop_reach=float(flop[i][classes])))
    contrasts=[];widths=[];lower=-200.;upper=200.5;half=(upper-lower)/2.;mid=(upper+lower)/2.
    for name,(new,old,player) in zip(CONTRAST_NAMES,CONTRASTS):
        width=half*(flop[new]+flop[old]);widths.append(width)
        c=float(terminal[new][player]-terminal[old][player])+mid*math.fsum((matrix.mass*(flop[new]-flop[old])).ravel())
        contrasts.append(dict(name=name,integrated_center=c,
            expected_half_width=math.fsum((matrix.mass*width).ravel()),
            old_postflop_probability=math.fsum((matrix.mass*flop[old]).ravel()),
            new_postflop_probability=math.fsum((matrix.mass*flop[new]).ravel())))
    b=np.max(widths,axis=0);z=math.fsum((matrix.mass*b).ravel())
    assert z>=0 and np.isfinite(b).all()
    normalized=matrix.mass*b/z if z else np.zeros_like(b)
    if z:assert abs(math.fsum(normalized.ravel())-1)<1e-12
    assert time.monotonic()-start<180
    for p,h in inputs.items():assert sha(p)==h,p
    assert sum(p.stat().st_size for p in FOLDER.rglob('*') if p.is_file())<4_000_000
    atomic_json(RESULT,dict(passed=True,registration_sha256=sha(REG),gpu_used=False,new_poker_deals=0,
        retained_training_deals=1,profiles_checked=8,native_forced_leaf_profiles=24,
        preflop_policy_max_absolute_error=policy_error,native_decomposition_errors=errors,
        global_candidate_half_width_Z=z,contrasts=contrasts,
        proposed_class_pair_support=int(np.count_nonzero(normalized)),
        fixed_16384_deal_additive_bernstein_term=7*(2*z)*math.log(4*8/.05)/(3*(16384-1)),
        estimated_work='No new test run; this is deterministic proposal planning from frozen policies.',
        artifacts={str(p):sha(p) for p in FOLDER.iterdir() if p.is_file()},seconds=time.monotonic()-start,
        numerical_bound_qualified=False,proposal_sampler_qualified=False,accuracy_claim=False,
        limitation='One retained full-bank physical-deal decomposition control plus complete class reach algebra. Matrix provenance is inherited. C/Z are floating planning values; further sampler and conservative numerical-bound qualification is required before statistical use.'))
    print(json.dumps(read(RESULT)),flush=True)


if __name__=='__main__':main()
