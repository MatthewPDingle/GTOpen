"""Saved-file integrity and cashflow readback; no new training or enumeration."""
import hashlib
import json
import math
from pathlib import Path
import time
import traceback

ROOT=Path('T:/Dev/GTOpen')
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='stack-context-resources-v1'


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def read(path):return json.loads(Path(path).read_bytes())


def save(path,value):
    with Path(path).open('x') as stream:json.dump(value,stream,indent=2,allow_nan=False)


def main():
    result_path=OUT/(PREFIX+'-result.json');reg_path=OUT/(PREFIX+'-registration.json')
    output=OUT/(PREFIX+'-readback.json');attempt=OUT/(PREFIX+'-readback-attempt.json');failure=OUT/(PREFIX+'-readback-failure.json')
    locks=[ROOT/('research/preflop-evolution/'+name+'/running.lock') for name in
           ('representative-coverage-20260919','symmetric-bridge-20260919')]
    if any(p.exists() for p in [output,attempt,failure,*locks]):raise ValueError('Existing attempt or active research')
    result=read(result_path);reg=read(reg_path)
    if not (result['complete'] and result['passed'] and result['registration_sha256']==sha(reg_path)):
        raise ValueError('Completed resource preparation required')
    save(attempt,dict(reader_sha256=sha(__file__),result_sha256=sha(result_path),scientific_training=False))
    began=time.monotonic()
    try:
        identities=dict(reg['inputs'])
        tests_path=OUT/(PREFIX+'-tests.json');tests=read(tests_path)
        if not (tests['complete'] and tests['passed'] and tests['tests']==3):raise ValueError('Implementation checks did not pass')
        identities.update(tests['inputs']);identities[str(tests_path)]=sha(tests_path)
        cache_review=read(OUT/'stack-context-complete-allin-cache-v1-readback.json')
        cache_result=OUT/'stack-context-complete-allin-cache-v1-result.json'
        if not (cache_review['complete'] and cache_review['passed'] and cache_review['result_sha256']==sha(cache_result)
                and result['cache_sha256']==cache_review['cache_sha256']):raise ValueError('Completed cache proof mismatch')
        records=[]
        for key,record in result['contexts'].items():
            identities.update(record['artifacts'])
            source=Path(record['context_path']).read_text();context=json.loads(source)
            if hashlib.sha256(source.encode()).hexdigest()!=key:raise ValueError('Changed context')
            matrix=read(record['matrix']);population=read(record['population'])
            if matrix['context_sha256']!=key or population['context_sha256']!=key:raise ValueError('Misbound resource')
            if record['matrix_sha256']!=sha(record['matrix']):raise ValueError('Matrix identity differs')
            root=context['nodes'][0];response=context['nodes'][root['children'][3]]
            called=context['nodes'][response['children'][1]]
            rake=called['pot']*context['rake_fraction']
            if context['rake_cap']>0:rake=min(rake,context['rake_cap'])
            conserved=called['pot']-sum(called['invested'])-rake
            arrays=[matrix[k] for k in ('class_mass','bb_showdown_entries','btn_showdown_entries')]
            if any(len(a)!=169 or any(len(row)!=169 for row in a) for a in arrays):raise ValueError('Matrix dimensions differ')
            mass,bb,btn=[[x for row in a for x in row] for a in arrays]
            if (not all(math.isfinite(x) for a in (mass,bb,btn) for x in a) or min(mass)<0
                    or abs(math.fsum(mass)-1)>1e-12):raise ValueError('Invalid saved entries')
            error=max(abs(b+t-p*conserved) for p,b,t in zip(mass,bb,btn))
            if error>1e-11:raise ValueError('Saved cashflow conservation differs')
            if (len(population['rows'])!=93769 or population['physical_pairs']!=1624350
                    or abs(math.fsum(r['probability'] for r in population['rows'])-1)>1e-12):raise ValueError('Saved population coverage differs')
            if record['incoming_class_support']!=[169,169]:raise ValueError('Fixture support changed')
            records.append(dict(depth=record['depth'],context_sha256=key,maximum_cashflow_error=error))
        if sorted(r['depth'] for r in records)!=[20,40,60,100,150,200,400]:raise ValueError('Complete depth set required')
        for path,expected in identities.items():
            if sha(path)!=expected:raise ValueError('Changed retained input or artifact: '+path)
        save(output,dict(complete=True,passed=True,result_sha256=sha(result_path),registration_sha256=sha(reg_path),
            reader_sha256=sha(__file__),checked_identities=len(identities),contexts=records,seconds=time.monotonic()-began,
            scope='Saved artifacts, complete declared population, probability mass and context-specific cashflow conservation. Reuses prior exact count verification; does not independently rerun enumeration or certify learned ranges.',
            scientific_training=False,accuracy_qualified=False,full_training_cycle_qualified=False))
        print(json.dumps(dict(passed=True,contexts=len(records),identities=len(identities),seconds=time.monotonic()-began)))
    except BaseException as error:
        save(failure,dict(error=repr(error),traceback=traceback.format_exc(),retry_allowed=False));raise


if __name__=='__main__':main()
