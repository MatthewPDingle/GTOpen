"""Independent standard-library reconstruction of frozen-policy statistics."""
import hashlib
import json
import math
from pathlib import Path
import statistics
import time

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='root-fixed-variance-v1'

def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    start=time.monotonic();maximum=0.
    def close(a,b):
        nonlocal maximum
        error=abs(a-b);assert math.isfinite(error) and error<1e-8
        maximum=max(maximum,error)
    rp,pp=[OUT/f'{PREFIX}-{s}.json' for s in ('registration','result')]
    reg,result=read(rp),read(pp)
    assert result['passed'] and result['registration_sha256']==sha(rp)
    for p,h in {**reg['inputs'],**result['batch_hashes']}.items():assert sha(p)==h,p
    original=read(OUT/'root-retained-wider-study-v1-registration.json')
    response=read(Path(reg['source'])/'response.json')
    byclass=[[] for _ in range(169)]
    counts=0
    for p in sorted(result['batch_hashes']):
        assert time.monotonic()-start<600
        data=read(p)
        for c,row in zip(data['classes'],data['action_values']):
            assert c==counts%169
            byclass[c].append(row);counts+=1
    assert counts==43264 and all(len(rows)==256 for rows in byclass)
    variance_totals=[0.,0.,0.];denominator=0.;disagreement=0;disagreement_mass=0.
    for c,(data,reported) in enumerate(zip(byclass,result['classes'])):
        assert c==reported['hand_class']
        mass=original['exact']['masses'][c];close(reported['mass'],mass)
        means=[statistics.mean(row[a] for row in data) for a in range(4)]
        means[0]=original['exact']['fold_entries'][c]/mass
        means[3]=original['exact']['jam_entries'][c]/mass
        for a in range(4):close(means[a],reported['means'][a]);close(means[a],response['class_action_means'][c][a])
        contrasts=[[row[1]-row[0],row[2]-row[0],row[1]-row[2]] for row in data]
        variance=[]
        for a in range(3):
            column=[row[a] for row in contrasts]
            v=statistics.variance(column);variance.append(v)
            close(statistics.mean(column),reported['contrasts_mean'][a])
            close(v,reported['contrasts_sample_variance'][a])
            close(math.sqrt(v/256),reported['contrast_descriptive_standard_error'][a])
            variance_totals[a]+=mass*v
        calls=[row[1] for row in data];raises=[row[2] for row in data]
        vm=statistics.variance(calls)+statistics.variance(raises)
        denominator+=mass*vm
        close(variance[2]/vm,reported['call_raise_paired_to_independent_variance_ratio'])
        for i,x in enumerate((calls,raises)):
            for j,y in enumerate((calls,raises)):
                covariance=statistics.covariance(x,y)
                close(covariance,reported['call_raise_covariance'][i][j])
        actions=[]
        for hi,part in enumerate((data[:128],data[128:])):
            m=[statistics.mean(row[a] for row in part) for a in range(4)]
            m[0]=means[0];m[3]=means[3]
            actions.append(max(range(4),key=m.__getitem__))
            for a in range(4):close(m[a],reported['half_means'][hi][a])
        assert actions==reported['half_actions']
        if actions[0]!=actions[1]:disagreement+=1;disagreement_mass+=mass
    for a in range(3):close(math.sqrt(variance_totals[a]/256),result['incoming_mass_weighted_class_rms_standard_error'][a])
    close(variance_totals[2]/denominator,result['weighted_call_raise_paired_to_independent_variance_ratio'])
    assert disagreement==result['half_disagreeing_classes']==62
    close(disagreement_mass,result['half_disagreement_mass'])
    path=OUT/f'{PREFIX}-independent-review.json';assert not path.exists()
    output=dict(passed=True,registration_sha256=sha(rp),result_sha256=sha(pp),reader_sha256=sha(Path(__file__)),
        rows=counts,classes=169,maximum_scalar_error=maximum,seconds=time.monotonic()-start,
        scope='Independent arithmetic on saved fixed-policy values. No fresh data, new inference, confidence claim or independent native game implementation.',
        production_modified=False,accuracy_qualified=False)
    path.write_text(json.dumps(output,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
    print(output)


if __name__=='__main__':main()
