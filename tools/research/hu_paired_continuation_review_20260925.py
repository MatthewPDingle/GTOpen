"""Scalar reconstruction of the fixed paired-continuation diagnostic.

Independent statistical and transport logic; does not rerun native poker or
neural inference and does not prove strategic accuracy.
"""
import hashlib
import json
import math
from pathlib import Path
import statistics
import struct
import time
from archived_evaluation_reader_v1 import ArchivedEvaluationReader
from reboot_research_idle_v1 import idle

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='paired-continuation-v1'


def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    started=time.monotonic();last=0.;maximum=0.
    def guard():
        nonlocal last
        now=time.monotonic();assert now-started<3600
        if now-last>2:assert idle();last=now
    def close(a,b):
        nonlocal maximum
        err=abs(a-b);assert math.isfinite(err) and err<1e-8,(a,b)
        maximum=max(maximum,err)
    rp,pp=[OUT/f'{PREFIX}-{s}.json' for s in ('registration','result')]
    reg,result=read(rp),read(pp);assert result['passed'] and result['registration_sha256']==sha(rp)
    assert result['deals']==reg['deals']==10816 and reg['per_class']==64 and reg['batch_size']==32
    assert result['batches']==338 and result['production_modified'] is False and result['accuracy_qualified'] is False
    assert reg['inputs'][str(Path(__file__).resolve())]==sha(Path(__file__))
    for path,digest in reg['inputs'].items():guard();assert sha(path)==digest,path
    store=Path(result['store']);analysis=read(store/'analysis.json')
    assert sha(store/'analysis.json')==result['analysis_sha256']
    sampled=read('T:/GTOpen-research/root-retained-wider-study-v1/evaluation/training-deals.json')
    reader=ArchivedEvaluationReader(store,result['archive_manifest_hashes'],external_files=[],guard=guard)
    names=[f'train-{i:06d}' for i in range(0,10816,32)]
    assert set(names)==set(result['archive_manifest_hashes'])==set(result['batch_summary_hashes'])
    observations=0;all_values=[]
    for index,name in enumerate(names):
        guard();folder=store/name
        raw={filename:reader.read_bytes(folder/filename) for filename in (
            'query-batch.json','conditional-batch.json','queries.json','profiles.json','native.json','summary.json')}
        docs={k:json.loads(v) for k,v in raw.items()}
        s=docs['summary.json'];assert hashlib.sha256(raw['summary.json']).hexdigest()==result['batch_summary_hashes'][name]
        assert set(s['artifacts'])==set(raw)-{'summary.json'}
        for filename,digest in s['artifacts'].items():assert hashlib.sha256(raw[filename]).hexdigest()==digest
        batch=docs['query-batch.json'];wanted=sampled['deals'][index*32:index*32+32]
        assert batch==dict(format=2,batch_id=f'{PREFIX}-{name}',seed=0,query_limit=100000,deals=wanted)
        q=docs['queries.json'];labels=docs['conditional-batch.json'];transport=docs['profiles.json'];native=docs['native.json']
        assert q['batch_source']==raw['query-batch.json'].decode() and labels['deals']==wanted
        assert transport['batch_source']==raw['conditional-batch.json'].decode()
        assert transport['context_source']==q['context_source']==(OUT/'bb-context-candidate.json').read_text()
        assert native['format']==2 and native['terminal_estimator']=='conditional-preflop-allin-v1'
        assert native['postflop_outcomes']=='sampled-board'
        assert s['profile_order']==['AA','AB','BA','BB'] and s['action_order']==['call','raise']
        expected_names=[f'{p}-{a}' for p in s['profile_order'] for a in s['action_order']]
        assert [p['name'] for p in transport['profiles']]==[p['name'] for p in native['profiles']]==expected_names
        obs=q['observations'];profiles=[p['policies'] for p in transport['profiles']]
        assert all(len(p)==len(obs) for p in profiles)
        roots={i for i,o in enumerate(obs) if o['phase']==0 and int(o['hi'])==1}
        for i,o in enumerate(obs):
            for k,p in enumerate(profiles):
                row=p[i];assert {z:row[z] for z in ('hi','lo','actor','n')}=={z:o[z] for z in ('hi','lo','actor','n')}
                prob=row['probabilities'];assert len(prob)==4 and all(math.isfinite(x) and x>=0 for x in prob)
                close(math.fsum(prob),1.);assert all(x==0 for x in prob[o['n']:])
                pair=k//2;bb_index=(0,0,6,6)[pair];btn_index=(0,6,0,6)[pair]
                expected=([float(a==1+k%2) for a in range(4)] if i in roots
                          else profiles[bb_index if o['actor']==0 else btn_index][i]['probabilities'])
                assert prob==expected,'Crossed continuation transport differs'
        for k,base in enumerate((0,6)):
            cov=s['coverage'][k];rootmap={r['query']:r for r in cov['roots']}
            assert set(rootmap)==roots
            expected_counts=[[sum(o['actor']==a and o['phase']==p for o in obs) for p in range(4)] for a in range(2)]
            assert cov['rows_by_actor_phase']==expected_counts
            assert all(0<=cov['zero_reach_by_actor_phase'][a][p]<=expected_counts[a][p] for a in range(2) for p in range(4))
            digest=hashlib.sha256()
            for i,row in enumerate(profiles[base]):
                prob=rootmap[i]['probabilities'] if i in roots else row['probabilities']
                digest.update(struct.pack('<4d',*prob))
            assert digest.hexdigest()==cov['probabilities_sha256']
        for key in ('maximum_forward_cashflow_error','maximum_conservation_error'):
            close(s[key],native[key]);assert 0<=native[key]<1e-10
        assert s['classes']==sampled['hand_classes'][index*32:index*32+32]
        assert all(len(p['deals'])==32 for p in native['profiles'])
        for d in range(32):
            values=[[native['profiles'][2*p+a]['deals'][d]['values'][0] for a in range(2)] for p in range(4)]
            for p in range(4):
                for a in range(2):close(values[p][a],s['values'][d][p][a])
            all_values.append(values)
        observations+=len(obs)
    assert len(all_values)==10816 and len(analysis['classes'])==169
    assert analysis['profiles']==['AA','AB','BA','BB'] and analysis['contrasts']==['call','raise','call minus raise']
    assert analysis['effect_names']==['diagonal','BB policy','BTN policy','interaction']
    assert analysis['accuracy_qualified'] is False and analysis['simultaneous_confidence_claim'] is False
    means=[];variances=[];profilevars=[]
    for c,row in enumerate(analysis['classes']):
        assert row['hand_class']==c and row['samples']==64
        close(row['mass'],sampled['original_class_masses'][c])
        xs=[];es=[]
        for repeat in range(64):
            ps=all_values[repeat*169+c];x=[p+[p[0]-p[1]] for p in ps];xs.append(x)
            aa,ab,ba,bb=x
            es.append([[bb[k]-aa[k] for k in range(3)],
                [(ba[k]-aa[k]+bb[k]-ab[k])/2 for k in range(3)],
                [(ab[k]-aa[k]+bb[k]-ba[k])/2 for k in range(3)],
                [bb[k]-ba[k]-ab[k]+aa[k] for k in range(3)]])
            for k in range(3):close(es[-1][0][k],es[-1][1][k]+es[-1][2][k])
        for label,data in (('profiles',xs),('effects',es)):
            for p in range(4):
                for k in range(3):
                    values=[r[p][k] for r in data];mean=statistics.mean(values);var=statistics.variance(values)
                    close(mean,row[label]['mean'][p][k]);close(var,row[label]['sample_variance'][p][k])
                    close(math.sqrt(var/64),row[label]['standard_error'][p][k])
                    for h in range(2):close(statistics.mean(values[32*h:32*(h+1)]),row[label]['half_means'][h][p][k])
        means.append([[statistics.mean(r[p][k] for r in es) for k in range(3)] for p in range(4)])
        variances.append([[statistics.variance(r[p][k] for r in es) for k in range(3)] for p in range(4)])
        profilevars.append([[statistics.variance(r[p][k] for r in xs) for k in range(3)] for p in range(4)])
    m=sampled['original_class_masses'];close(math.fsum(m),1.)
    for p in range(4):
        for k in range(3):
            close(math.fsum(m[c]*means[c][p][k] for c in range(169)),analysis['weighted_effect_mean'][p][k])
            close(math.sqrt(math.fsum(m[c]*means[c][p][k]**2 for c in range(169))),analysis['weighted_rms_class_effect_mean'][p][k])
            close(math.sqrt(math.fsum(m[c]*variances[c][p][k]/64 for c in range(169))),analysis['weighted_rms_class_effect_standard_error'][p][k])
            close(math.sqrt(math.fsum(m[c]*profilevars[c][p][k]/64 for c in range(169))),analysis['weighted_rms_class_profile_standard_error'][p][k])
    output=dict(passed=True,registration_sha256=sha(rp),result_sha256=sha(pp),reader_sha256=sha(Path(__file__)),
        batches=338,deals=10816,observations=observations,maximum_scalar_error=maximum,
        seconds=time.monotonic()-started,production_modified=False,accuracy_qualified=False,
        scope='All archive identities, paired cards, crossed transport, native value extraction and scalar statistics reconstructed. Does not rerun neural inference, verify support values, or independently implement native poker traversal.')
    target=OUT/f'{PREFIX}-independent-review.json';assert not target.exists()
    target.write_text(json.dumps(output,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(output),flush=True)


if __name__=='__main__':main()
