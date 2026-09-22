"""Descriptive full-panel comparison, only after both all-in evaluation audits.

Different opponents and independent test seeds prevent a paired improvement
claim. Preserve all classes and never turn inspected values into hand patches.
"""
import json
from pathlib import Path
import time
from hu_sampled_physical_dense_comparison_20260922 import OUT,read
from sampled_physical_root_evaluation_v1 import ROOT,sha,save


def main():
    began=time.monotonic()
    btnpaths={k:OUT/f'sampled-physical-allin-btn-evaluation-v2-{k}.json'
              for k in ('registration','result','independent-review','status')}
    btn={k:json.loads(p.read_text()) for k,p in btnpaths.items()}
    assert btn['status']['state']=='complete' and btn['result']['passed'] and btn['independent-review']['passed']
    assert btn['independent-review']['inputs'][str(btnpaths['result'])]==sha(btnpaths['result'])
    assert btn['result']['registration_sha256']==sha(btnpaths['registration'])
    for p,h in btn['registration']['inputs'].items():assert sha(p)==h,p
    names={'dense':'sampled-physical-dense-evaluation-v1',
           'hybrid':'sampled-physical-hybrid-evaluation-v2',
           'allin':'sampled-physical-allin-evaluation-v2'}
    candidates={k:read(prefix) for k,prefix in names.items()}
    regs={k:json.loads((OUT/f'{prefix}-registration.json').read_text()) for k,prefix in names.items()}
    assert len({sha(r['context']) for r in regs.values()})==1
    assert len({r['config']['test_seed'] for r in regs.values()})==3
    configs={k:json.loads(Path(r['training_registration']).read_text())['config'] for k,r in regs.items()}
    assert configs['dense']==configs['hybrid']
    assert {k:v for k,v in configs['allin'].items() if k not in ('terminal_estimator','allin_cache_sha256')}==configs['dense']
    assert configs['allin']['terminal_estimator']=='conditional-preflop-allin-v1'
    assert all(r['selected_iterations']==78 for r in regs.values())
    changes=[]
    for rows in zip(*[candidates[k]['classes'] for k in names]):
        assert len({r['hand_class'] for r in rows})==len({r['hand'] for r in rows})==1
        changes.append(dict(hand=rows[0]['hand'],hand_class=rows[0]['hand_class'],
            dense_to_allin_probability_changes=[b-a for a,b in zip(rows[0]['baseline_probabilities'],rows[2]['baseline_probabilities'])],
            by_candidate={k:dict(test_deals=r['test_deals'],call_minus_fold_bb=r['call_minus_fold_bb']) for k,r in zip(names,rows)}))
    assert len(changes)==169
    scope=('Descriptive, complete-test-panel comparison after BB and BTN all-in audits. '
           'Different test seeds and opponent/continuation policies; dense used float32 evaluation, '
           'hybrid and all-in use checked float64 inference. All-in has alpha .025 for each of two '
           'predeclared families; older BB trials have alpha .05 and their BTN checks were post-hoc. '
           'No paired cross-candidate significance or best-response upper bound. All 169 classes '
           'retained; per-hand outcomes are diagnostics, not training targets or edits. '
           'No production/preview change, Wizard equivalence, or UTG/LJ transfer claim.')
    result=dict(source_sha256=sha(Path(__file__)),reader_sha256=sha(ROOT/'tools/research/hu_sampled_physical_dense_comparison_20260922.py'),
        candidates=candidates,training_configs=configs,class_changes=changes,
        btn=dict(evidence={str(p):sha(p) for p in btnpaths.values()},result=btn['result']),
        seconds=time.monotonic()-began,production_modified=False,scope=scope)
    save(OUT/'sampled-physical-allin-comparison-v1-result.json',result)
    print(json.dumps(dict(candidates={k:{n:v for n,v in c.items() if n not in ('classes','evidence')} for k,c in candidates.items()},scope=scope)))


if __name__=='__main__':main()
