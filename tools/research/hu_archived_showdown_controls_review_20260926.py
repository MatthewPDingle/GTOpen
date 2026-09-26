"""Separate readback using augmented least squares and scalar variances."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import hashlib
import math
from pathlib import Path
import time
import numpy as np
from archived_evaluation_reader_v1 import ArchivedEvaluationReader
from showdown_control_reference_v1 import score
from hu_frozen_root_precision_20260926 import OUT,ROOT,read,sha,save,values_from
from reboot_research_idle_v1 import idle

PREFIX='archived-showdown-control-diagnostic-v1'


def variance(values):
    mean=math.fsum(values)/len(values)
    return mean,math.fsum((v-mean)**2 for v in values)/(len(values)-1)


def main():
    start=time.monotonic();rp=OUT/f'{PREFIX}-result.json';result=read(rp)
    regp=OUT/f'{PREFIX}-registration.json';reg=read(regp)
    assert read(OUT/f'{PREFIX}-status.json')['state']=='complete' and result['passed']
    assert result['registration_sha256']==sha(regp)
    for p,h in reg['inputs'].items():assert sha(p)==h,p
    store=Path(reg['store']);assert sha(store/'centered-features.npy')==result['feature_sha256']
    x=np.load(store/'centered-features.npy',allow_pickle=False);assert x.shape==(65536,8) and np.isfinite(x).all()
    source=read(OUT/'frozen-root-precision-study-v1-result.json');sr=read(OUT/'frozen-root-precision-study-v1-registration.json')
    v,c=values_from(sr,source['jobs']);original=read(sr['source_result'])
    def guard():assert idle() and time.monotonic()-start<1200
    reader=ArchivedEvaluationReader(original['store'],original['archive_manifest_hashes'],external_files=[],guard=guard)
    offset=0
    assert sha(store/'cards.json')==result['cards_sha256'] and sha(store/'showdown.json')==result['native_sha256']
    cards_doc=read(store/'cards.json');native=read(store/'showdown.json')
    assert native['input_source']==(store/'cards.json').read_text()
    assert sha(store/'exact-equities.npy')==result['exact_equity_sha256']
    exact=np.load(store/'exact-equities.npy',allow_pickle=False);assert exact.shape==(65536,)
    assert np.all(x[:,1:]==0)
    for job in source['jobs']:
        path=Path(original['store'])/job['source']/'conditional-batch.json';raw=reader.read_bytes(path)
        assert hashlib.sha256(raw).hexdigest()==result['source_card_artifact_hashes'][job['source']]
        import json
        batch=json.loads(raw)
        assert len(batch['deals'])==len(batch['allin_counts'])==32
        for cards,counts in zip(batch['deals'],batch['allin_counts']):
            assert cards==cards_doc['deals'][offset] and counts['private_cards']==cards[:4]
            assert counts['boards']==1712304 and sum(counts[k] for k in ('wins','ties','losses'))==1712304
            equity=(2*counts['wins']+counts['ties'])/(2*counts['boards'])
            assert equity==exact[offset]
            reference=score(cards);assert reference==native['twice_bb_share'][offset]
            assert x[offset,0]==reference/2-equity
            offset+=1
    assert offset==65536
    maximum_beta=maximum_moment=0.
    masses=read(OUT/'later-action-final-root-stability.json')['entry_masses']
    for bank in range(4):
        guard();path=store/f'coefficients-{bank}.npy';assert sha(path)==result['coefficient_sha256'][bank]
        beta=np.load(path,allow_pickle=False);assert beta.shape==(169,2,8,3) and np.isfinite(beta).all()
        y=np.column_stack((v[bank,:,1]-v[bank,:,0],v[bank,:,2]-v[bank,:,0],v[bank,:,2]-v[bank,:,1]));fixed=y.copy()
        for hand in range(169):
            ids=np.flatnonzero(c==hand)
            for half in range(2):
                train=ids[ids%2!=half];test=ids[ids%2==half]
                expected=np.zeros((8,3))
                if len(train)>=20:
                    xx=x[train]-x[train].mean(0);yy=y[train]-y[train].mean(0)
                    # Different numerical route: ridge is eight unit pseudo-rows.
                    expected=np.linalg.lstsq(np.vstack((xx,np.eye(8))),np.vstack((yy,np.zeros((8,3)))),rcond=None)[0]
                maximum_beta=max(maximum_beta,float(np.max(abs(expected-beta[hand,half]))))
                fixed[test]-=x[test]@expected
        raw_terms=[[],[],[]];corrected_terms=[[],[],[]]
        for hand,row in enumerate(result['banks'][bank]['classes']):
            ids=np.flatnonzero(c==hand);assert row['count']==len(ids)
            for k in range(3):
                mean,var=variance([float(y[i,k]) for i in ids]);newmean,newvar=variance([float(fixed[i,k]) for i in ids])
                maximum_moment=max(maximum_moment,abs(mean-row['original_means'][k]),abs(var-row['original_variances'][k]),abs(newmean-row['corrected_means'][k]),abs(newvar-row['corrected_variances'][k]))
                raw_terms[k].append(masses[hand]*var);corrected_terms[k].append(masses[hand]*newvar)
        for k in range(3):
            ratio=math.fsum(corrected_terms[k])/math.fsum(raw_terms[k])
            maximum_moment=max(maximum_moment,abs(ratio-result['banks'][bank]['weighted_variance_ratios'][k]))
    assert maximum_beta<1e-9 and maximum_moment<1e-8
    save(OUT/f'{PREFIX}-readback.json',dict(passed=True,source_result_sha256=sha(rp),reviewer_sha256=sha(Path(__file__)),
        checked_feature_rows=offset,maximum_coefficient_error=maximum_beta,maximum_moment_error=maximum_moment,
        seconds=time.monotonic()-start,scope='Authenticated cards, exact counts, independently scored boards and forced values; augmented least-squares coefficient reconstruction and scalar moments. No new poker evaluation or independent proof of strategic accuracy.'))
    print('Archived showdown-control readback passed.')


if __name__=='__main__':main()
