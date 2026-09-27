"""Qualify private-first variable continuation values against forward cashflows."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import json
from pathlib import Path
import subprocess
import time
import numpy as np
from board_fixed_policy_control_v1 import ROOT,OUT,read,save,sha,policy_rows
from board_root_components_control_v1 import preflop_policy,forward_variable
from weighted_training_policy_v1 import probabilities
from sampled_physical_bank_v1 import histories
from preflop_allin_matrix_v1 import AllinMatrix
from storage_strategic_common_prior_20260920 import PAIRS,CLASSES


def native_pair_values(folder,deals,model,args,context_source,exe):
    cp=OUT/'bb-context-candidate.json';batch=folder/'batch.json'
    save(batch,dict(format='variable-continuation-pairs-v1',deals=deals))
    query_path=folder/'queries.json'
    subprocess.run([str(exe),'queries',str(cp),str(batch),str(query_path)],check=True,
                   creationflags=subprocess.CREATE_NO_WINDOW,timeout=120)
    queries=read(query_path);histories(queries['observations'])
    assert queries['context_source']==context_source and queries['batch_source']==batch.read_text()
    p,_=probabilities(queries,model,device='cpu',**args)
    policy=folder/'policy.json'
    save(policy,dict(format='variable-continuation-policy-v1',context_source=context_source,
        batch_source=queries['batch_source'],policies=[dict(hi=o['hi'],lo=o['lo'],probabilities=row.tolist())
        for o,row in zip(queries['observations'],p)]))
    output=folder/'values.json'
    subprocess.run([str(exe),'evaluate',str(cp),str(batch),str(policy),str(output)],check=True,
                   creationflags=subprocess.CREATE_NO_WINDOW,timeout=120)
    rows=read(output)['rows'];assert [r['deal_index'] for r in rows]==list(range(len(deals)))
    values=np.array([r['variable_action_values'] for r in rows])
    assert values.shape==(len(deals),4) and np.isfinite(values).all() and np.all(values[:,[0,3]]==0)
    return values,[batch,query_path,policy,output]


def main():
    began=time.monotonic();prior_path=OUT/'board-root-components-control-v1-result.json';prior=read(prior_path)
    assert prior['passed']
    for path,digest in prior['inputs'].items():assert sha(path)==digest,path
    cp=OUT/'bb-context-candidate.json';source=cp.read_text();context=read(cp)
    model_paths=[Path(p) for p in prior['inputs'] if '/objects/' in p.replace('\\','/')];assert len(model_paths)==1
    model=read(model_paths[0]);mp=OUT/'preflop-allin-matrix-control-v1-matrix.json';matrix=AllinMatrix(read(mp),source)
    cat=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    args=dict(catalog_source=cat.read_text(),matrix_sha256=sha(mp),entry_mass=matrix.btn_mass)
    pre,_=preflop_policy(read('S:/GTOpen-research/board-root-components-control-v1/preflop-catalog.json'),context,model,args)
    tree=read('S:/GTOpen-research/board-full-support-control-v1/tree.json');post=policy_rows(tree,model,'saved-network')
    rng=np.random.default_rng(9279601);selected=[];deals=[]
    while len(deals)<24:
        i=int(rng.integers(len(tree['hands'][0])));j=int(rng.integers(len(tree['hands'][1])))
        private=tree['hands'][0][i]+tree['hands'][1][j]
        if len(set(private))!=4:continue
        selected.append((i,j));deals.append(private+tree['board'])
    folder=Path('S:/GTOpen-research/board-variable-pairs-control-v1');folder.mkdir(exist_ok=False)
    exe=ROOT/'target/release/examples/hu_variable_continuation_pairs_v1.exe'
    actual,paths=native_pair_values(folder,deals,model,args,source,exe)
    classes={tuple(h):int(c) for h,c in zip(PAIRS,CLASSES)};expected=np.zeros_like(actual)
    for k,(i,j) in enumerate(selected):
        t=dict(tree,hands=[[tree['hands'][0][i]],[tree['hands'][1][j]]],
               ranks=[[tree['ranks'][0][i]],[tree['ranks'][1][j]]])
        policies=[{ni:p[[i if branch['nodes'][ni]['actor']==0 else j]] for ni,p in rows.items()}
                  for branch,rows in zip(tree['branches'],post)]
        c=[np.array([classes[tuple(h[0])]]) for h in t['hands']]
        for a,start in ((1,2),(2,3)):
            expected[k,a]=forward_variable(t,policies,pre,context,[np.ones(1),np.ones(1)],c,start)[0]
    error=float(np.max(abs(actual-expected)));assert error<1e-9
    evidence=folder/'comparison.json';save(evidence,dict(actual=actual.tolist(),expected=expected.tolist()))
    inputs=dict(prior['inputs'])
    for p in [prior_path,Path(__file__),exe,evidence,*paths,ROOT/'crates/solver/examples/hu_variable_continuation_pairs_v1.rs',
              ROOT/'crates/solver/examples/research_sampled/policy_bank_v1.rs',ROOT/'crates/solver/examples/research_sampled/batch_queries_v1.rs']:
        inputs[str(p)]=sha(p)
    result=dict(passed=True,physical_deals=24,max_action_value_error=error,inputs=inputs,
        seconds=time.monotonic()-began,gpu_used=False,training_changed=False,production_modified=False,
        scope='Private-pair postflop-only action contributions against separate forward cashflows; not a precision study.')
    save(OUT/'board-variable-pairs-control-v1-result.json',result)
    print(json.dumps({k:result[k] for k in ('passed','physical_deals','max_action_value_error','seconds')}))


if __name__=='__main__':main()
