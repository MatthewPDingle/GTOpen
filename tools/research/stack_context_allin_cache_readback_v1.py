"""Independent orbit/role and retained native-count readback; no new enumeration."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
import itertools
import math
from pathlib import Path
import time
import traceback
from sampled_allin_protocol_v3 import AllinCache,BOARDS
from sampled_physical_root_evaluation_v1 import sha,save
from hu_sampled_physical_dense_btn_jam_diagnosis_20260923 import showdown
from stack_context_allin_cache_v1 import OUT,STORE,NAME,REG,RESULT,LOCK,OTHER,read
from bounded_parallel_evaluation_archive_v2 import production_available


def orbit(cards):
    return {tuple(sorted(4*(c//4)+p[c%4] for c in cards[:2])+sorted(4*(c//4)+p[c%4] for c in cards[2:]))
            for p in itertools.permutations(range(4))}


def main():
    output=OUT/(NAME+'-readback.json');attempt=OUT/(NAME+'-readback-attempt.json');failure=OUT/(NAME+'-readback-failure.json')
    if any(p.exists() for p in (output,attempt,failure,LOCK,OTHER)):raise ValueError('Existing attempt or resource owner')
    if not production_available():raise ValueError('Production has priority')
    spec=read(REG);result=read(RESULT)
    if not result['complete'] or not result['passed'] or result['registration_sha256']!=sha(REG):raise ValueError('Main result not complete')
    save(attempt,dict(pid=os.getpid(),registration_sha256=sha(REG),result_sha256=sha(RESULT),reviewer_sha256=sha(__file__)))
    began=time.monotonic()
    def guard():
        if time.monotonic()-began>900 or not production_available():raise RuntimeError('Readback deadline or production activity')
    try:
        for p,h in spec['inputs'].items():
            if sha(p)!=h:raise ValueError('Registered input changed: '+p)
        keys=[tuple(k) for k in read(STORE/'keys.json')]
        if len(keys)!=len(set(keys)) or keys!=sorted(keys):raise ValueError('Duplicate or unordered universe keys')
        represented=0
        for i,key in enumerate(keys):
            if i%2048==0:guard()
            if len(set(key))!=4 or any(type(c) is not int or not 0<=c<52 for c in key):raise ValueError('Invalid private cards')
            options=orbit(key)
            if key!=min(options):raise ValueError('Noncanonical representative')
            represented+=len(options)
        # Unique canonical orbits are disjoint. Their sizes exhaust every
        # possible ordered pair of disjoint two-card holdings.
        if represented!=math.comb(52,2)*math.comb(50,2) or represented!=spec['physical_pairs']:
            raise ValueError('Missing physical private population')
        original=AllinCache(spec['original_cache'],spec['original_cache_sha256'])
        expected=dict(original.rows)
        for i,(key,row) in enumerate(original.rows.items()):
            if i%2048==0:guard()
            target=min(orbit(key[2:]+key[:2]))
            reversed_row=dict(private_cards=list(target),wins=row['losses'],losses=row['wins'],ties=row['ties'],boards=BOARDS)
            if target in expected and expected[target]!=reversed_row:raise ValueError('Reversed reviewed counts disagree')
            expected[target]=reversed_row
        reused=AllinCache(STORE/'reused-cache.json',spec['inputs'][str(STORE/'reused-cache.json')])
        if reused.rows!=expected or len(original.rows)!=spec['directly_reused'] or len(expected)!=spec['reused_after_role_reversal']:
            raise ValueError('Reused population differs')
        missing=set(keys)-set(expected)
        native_keys=sorted({min(key,min(orbit(key[2:]+key[:2]))) for key in missing})
        if native_keys!=[tuple(k) for k in read(STORE/'native-keys.json')]:raise ValueError('Wrong exact-enumeration representatives')
        batches=result['batches'];native_seconds=0.;checks=0
        for index,start in enumerate(range(0,len(native_keys),20)):
            guard();ip=STORE/'native'/f'input-{index:05d}.json';op=STORE/'native'/f'output-{index:05d}.json'
            entry=batches[str(index)]
            if sha(ip)!=entry['input_sha256'] or sha(op)!=entry['output_sha256']:raise ValueError('Native artifact changed')
            inp=read(ip);rows=read(op);selected=native_keys[start:start+20]
            if inp['format']!=1 or len(rows)!=len(selected) or len(inp['cases'])!=len(selected):raise ValueError('Wrong batch length')
            for key,case,row in zip(selected,inp['cases'],rows):
                deck=[c for c in range(52) if c not in key]
                if (case!=dict(private_cards=list(key),sampled_boards=[deck[:5],deck[-5:]])
                        or row['private_cards']!=list(key)
                        or any(type(row[k]) is not int or row[k]<0 for k in ('wins','ties','losses','exact_boards'))
                        or row['wins']+row['ties']+row['losses']!=BOARDS or row['exact_boards']!=BOARDS
                        or row['equity']!=(row['wins']+.5*row['ties'])/BOARDS):raise ValueError('Exact native counts invalid')
                scores=[]
                for board in case['sampled_boards']:
                    winner=showdown(list(key)+board);scores.append(1 if winner<0 else 2 if winner==0 else 0);checks+=1
                if scores!=row['sampled_scores']:raise ValueError('Independent sampled showdown mismatch')
                target=min(orbit(key[2:]+key[:2]))
                normal=dict(private_cards=list(key),wins=row['wins'],losses=row['losses'],ties=row['ties'],boards=BOARDS)
                reverse=dict(private_cards=list(target),wins=row['losses'],losses=row['wins'],ties=row['ties'],boards=BOARDS)
                for k,v in ((key,normal),(target,reverse)):
                    if k in expected and expected[k]!=v:raise ValueError('Count reconstruction contradiction')
                    expected[k]=v
                native_seconds+=row['exact_seconds']
        cache=AllinCache(result['cache_artifact'],result['cache_sha256'])
        if (set(cache.rows)!=set(keys) or cache.rows!=expected or len(native_keys)!=result['native_keys']
                or len(batches)!=math.ceil(len(native_keys)/20) or abs(native_seconds-result['native_seconds'])>1e-7):
            raise ValueError('Final cache or enumeration accounting differs')
        save(output,dict(complete=True,passed=True,registration_sha256=sha(REG),result_sha256=sha(RESULT),
            reviewer_sha256=sha(__file__),cache_artifact=result['cache_artifact'],cache_sha256=result['cache_sha256'],
            canonical_keys=len(keys),physical_pairs=represented,native_keys=len(native_keys),
            independent_sample_board_checks=checks,seconds=time.monotonic()-began,
            scope='Independent full-universe orbit coverage, role/count reconstruction and retained native artifact/sample-board checks. Does not rerun exhaustive enumeration or qualify a learned policy.',
            scientific_training=False,accuracy_qualified=False))
        print({'passed':True,'seconds':time.monotonic()-began,'canonical_keys':len(keys)})
    except BaseException as error:
        save(failure,dict(error=repr(error),traceback=traceback.format_exc(),retry_allowed=False));raise


if __name__=='__main__':main()
