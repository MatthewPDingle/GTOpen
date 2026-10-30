"""CPU-only native stack-depth geometry and public-price checks; no strategic training."""
import json
from pathlib import Path
import subprocess
import time
import numpy as np
import psutil
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from sampled_public_economics_features_v1 import encode_document,SPEC
from hu_context_audit_20260922 import audit
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='stack-geometry-control-v1'
STORE=Path('S:/GTOpen-research')/PREFIX


def main():
    started=time.monotonic();error=None
    def guard():
        assert time.monotonic()-started<900
        assert psutil.virtual_memory().available>20_000_000_000 and psutil.disk_usage('S:/').free>40_000_000_000
    guard();assert not STORE.exists()
    examples=ROOT/'target/release/examples'
    paths=[Path(__file__),ROOT/'tools/research/sampled_public_economics_features_v1.py',
           ROOT/'tools/research/hu_context_audit_20260922.py',ROOT/'Cargo.toml',ROOT/'Cargo.lock',ROOT/'crates/solver/Cargo.toml',
           ROOT/'cache/preflop_eq169.bin',
           *[ROOT/'crates/solver/examples'/n for n in ('hu_stack_geometry_fixtures_v1.rs','hu_public_economics_v1.rs','hu_sampled_geometry_probe.rs','research_sampled/state.rs','research_sampled/poker_reference_v1.rs')],
           *[examples/(n+'.exe') for n in ('hu_stack_geometry_fixtures_v1','hu_public_economics_v1','hu_sampled_geometry_probe')],
           *ROOT.glob('crates/solver/src/**/*.rs')]
    fit=ROOT/'cache/realization_fit.json'
    if fit.exists():paths.append(fit)
    reg=dict(inputs={str(p):sha(p) for p in paths},stack_depths=[20,40,60,100,150,200,400],maximum_seconds=900,
        feature_spec=SPEC,scope='Native, unsolved 3-seat BTN-open/SB-fold/BB-response geometry fixtures at seven equal stack depths. No learned ranges, GPU, new evaluation draws or production changes.',production_modified=False)
    rp=OUT/f'{PREFIX}-registration.json';save(rp,reg);STORE.mkdir()
    def invoke(name,args):
        guard();done=subprocess.run([str(examples/(name+'.exe')),*map(str,args)],cwd=ROOT,timeout=180,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
        assert done.returncode==0,done.stderr[-2500:]
        guard()
    try:
        fixtures=STORE/'fixtures';invoke('hu_stack_geometry_fixtures_v1',[fixtures])
        manifest=json.loads((fixtures/'manifest.json').read_text());assert not manifest['solved']
        board=STORE/'board.json';save(board,dict(bet_menu='50',boards=[dict(board='2c3d4h')]))
        records=[];vectors=[];contexts=[]
        for item in manifest['fixtures']:
            depth=item['stack'];name=item['name'];cp=fixtures/f'{name}-context.json';qp=fixtures/f'{name}-queries.json'
            context=json.loads(cp.read_text());assert context['iteration']==0 and context['config']['stack']==depth
            context_review=audit(context)
            raw=STORE/f'{name}-public.json';invoke('hu_public_economics_v1',[cp,qp,raw])
            document=json.loads(raw.read_text());matrix=encode_document(document,expected_context_sha256=sha(cp))
            rows={r['hi']:r for r in document['public_states']};root=rows['1']
            assert root['call_cost']==1 and root['pot']==3.5 and root['remaining']==[depth-1,depth-2]
            assert [a['increment'] for a in root['actions']]==[0.,1.,5.,depth-1]
            # Independent native TreeBuilder checks every legal postflop history,
            # all turn/river cards, sizes, chip totals and terminal payouts.
            geom=STORE/f'{name}-geometry.json';invoke('hu_sampled_geometry_probe',[cp,board,geom])
            g=json.loads(geom.read_text());assert g['passed'] and not g['device_allocated'] and not g['strategy_arenas_allocated']
            assert len(matrix)==item['public_decisions']
            root_index=[r['hi'] for r in document['public_states']].index('1');vectors.append(matrix[root_index]);contexts.append(sha(cp))
            records.append(dict(stack=depth,context_sha256=sha(cp),context_review=context_review,public_states=len(rows),
                root_incremental_costs=[a['increment'] for a in root['actions']],
                native_legal_nodes=sum(r['legal_nodes_checked'] for r in g['rows']),
                native_actions=sum(r['actions_checked'] for r in g['rows']),
                maximum_reference_tree_bytes=max(r['reference_tree_bytes'] for r in g['rows']),
                geometry_result_sha256=sha(geom),encoded_rows_finite=bool(np.isfinite(matrix).all())))
            print(json.dumps(records[-1]),flush=True)
        assert len(records)==7 and len(set(contexts))==7
        assert all(not np.array_equal(a,b) for i,a in enumerate(vectors) for b in vectors[i+1:])
        assert records[0]['context_review']['nodes']<records[-1]['context_review']['nodes'],'Expected shallow-stack tree reduction'
        # Same public node IDs across trees must never defeat context binding.
        rejects=0
        for i,item in enumerate(manifest['fixtures']):
            d=json.loads((STORE/f"{item['name']}-public.json").read_text())
            try:encode_document(d,expected_context_sha256=contexts[(i+1)%7])
            except ValueError:rejects+=1
            else:raise AssertionError('Cross-stack context accepted')
        for p,h in reg['inputs'].items():assert sha(p)==h,p
        guard();result=dict(passed=True,registration_sha256=sha(rp),contexts=records,cross_context_rejections=rejects,
            artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()},seconds=time.monotonic()-started,
            ready_for_strategic_training=False,accuracy_qualified=False,production_modified=False,scope=reg['scope'])
        save(OUT/f'{PREFIX}-result.json',result)
    except Exception as exc:error=repr(exc);raise
    finally:save(OUT/f'{PREFIX}-status.json',dict(state='stopped' if error else 'complete',error=error,production_modified=False))

if __name__=='__main__':main()
