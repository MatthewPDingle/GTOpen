"""Post-hoc evaluation-cost planning; never a new confidence statement."""
import json
import math
from pathlib import Path
import time
import numpy as np
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT,sha,save

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'


def main():
    began=time.monotonic();assert idle()
    candidates=[];inputs={}
    for prefix in ['sampled-physical-dense-evaluation-v1','sampled-physical-hybrid-evaluation-v2']:
        paths={s:OUT/f'{prefix}-{s}.json' for s in ['registration','result','independent-review']}
        reg,result,review=[json.loads(paths[s].read_text()) for s in paths]
        assert review['passed'] and review['result_sha256']==sha(paths['result'])
        assert review['registration_sha256']==sha(paths['registration'])
        context=json.loads(Path(reg['context']).read_text());width=2*context['config']['stack']+context['dead_money']
        series=reg['comparisons'];log=math.log(4*len(series)/.05)
        groups={c:[] for c in range(169)}
        for offset in range(0,16384,16):
            if offset%1024==0:assert idle() and time.monotonic()-began<120
            folder=Path(reg['store'])/f'{prefix}-test-{offset}'
            summary_path=folder/'summary.json';paired_path=folder/'paired.json'
            summary=json.loads(summary_path.read_text());paired=json.loads(paired_path.read_text())
            assert sha(summary_path)==result['batch_summary_hashes'][folder.name]
            assert paired['series']==series and paired['response_sha256']==result['response_sha256']
            assert len(summary['classes'])==len(paired['differences'])==16
            for c,row in zip(summary['classes'],paired['differences']):groups[c].append(row)
            inputs[str(summary_path)]=sha(summary_path);inputs[str(paired_path)]=sha(paired_path)
        all_rows=np.concatenate([np.asarray(x) for x in groups.values()]);n=len(all_rows)
        assert n==16384 and all(len(x)>=2 for x in groups.values())
        means=all_rows.mean(0);variances=all_rows.var(0,ddof=1)
        between=sum(len(x)*(np.asarray(x).mean(0)-means)**2 for x in groups.values())
        within=sum(((np.asarray(x)-np.asarray(x).mean(0))**2).sum(0) for x in groups.values())
        assert np.allclose(between+within,(n-1)*variances,rtol=1e-12,atol=1e-8)
        rows=[]
        for j,name in enumerate(series):
            reported=result['intervals'][name]
            assert math.isclose(means[j],reported['mean'],abs_tol=1e-10)
            assert math.isclose(variances[j],reported['sample_variance'],rel_tol=1e-10)
            def radius(count,var=variances[j]):
                return math.sqrt(2*var*log/count)+7*(2*width)*log/(3*(count-1))
            assert math.isclose(radius(n),reported['radius'],rel_tol=1e-10)
            budgets=[]
            for target in [.5,.25,.1]:
                low,high=2,2
                while radius(high)>target:high*=2
                while high-low>1:
                    mid=(low+high)//2
                    if radius(mid)>target:low=mid
                    else:high=mid
                assert radius(high)<=target<radius(high-1)
                budgets.append(dict(target_half_width_bb=target,plug_in_deals=high,
                    marginal_hours_at_observed_rate=high*result['seconds']/24576/3600))
            rows.append(dict(comparison=name,variance=variances[j],
                observed_between_class_fraction=float(between[j]/((n-1)*variances[j])),
                observed_within_class_fraction=float(within[j]/((n-1)*variances[j])),
                current_half_width_bb=radius(n),plug_in_budgets=budgets))
        inputs.update({str(p):sha(p) for p in paths.values()})
        candidates.append(dict(prefix=prefix,rows=rows,
            measured_main_evaluation_seconds=result['seconds'],measured_main_evaluation_deals=24576))
    inputs[str(Path(__file__))]=sha(Path(__file__))
    report=dict(passed=True,inputs=inputs,candidates=candidates,seconds=time.monotonic()-began,
        new_evaluation=False,training_launched=False,production_modified=False,
        scope='Descriptive planning using already audited completed results. Budgets plug observed variances into the original five-comparison radius and assume the measured throughput persists. They are not guaranteed future precision, statistical power, new confidence intervals, strategic accuracy targets or wall-clock deadlines. Runtime excludes reference preparation and final audits. Empirical class decomposition is not a validated stratified estimator; no new policy or stopping rule is selected.')
    save(OUT/'sampled-root-evaluation-precision-diagnosis-v1-result.json',report)
    print(json.dumps({k:v for k,v in report.items() if k!='inputs'},indent=2))


if __name__=='__main__':main()
