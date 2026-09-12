"""Exact independent-stratum variance diagnostic; no learning sampler enabled."""
from run07 import *

if __name__=='__main__':
    manifest=RAW/'particle-batch-manifest-v1.json'
    frozen=json.loads(manifest.read_text())
    run('particle-independent-numerical-v1',['cargo','test','--release','-p','solver','--features','preflop-research',
        '--lib','particle_independent_gpu_variance_diagnostic','--','--nocapture','--test-threads=1'],900,[manifest])
    rows=[]
    for line in (RAW/'particle-independent-numerical-v1.log').read_text().splitlines():
        if 'INDEPENDENT_VARIANCE ' in line:rows.append(json.loads(line.split('INDEPENDENT_VARIANCE ',1)[1]))
    if [(r['players'],r['family']) for r in rows]!=[(n,f) for n in (3,4,6,8) for f in range(3)]:raise RuntimeError('Incomplete coverage')
    if any(r['checksum_fnv64']!=frozen['checksum_fnv64'] for r in rows):raise RuntimeError('Changed partition')
    ratio=sum(r['pooled_variance'][1] for r in rows)/sum(r['pooled_variance'][0] for r in rows)
    eight=rows[-3:];eight_ratio=sum(r['pooled_variance'][1] for r in eight)/sum(r['pooled_variance'][0] for r in eight)
    result=dict(pooled_ratio=ratio,eight_player_ratio=eight_ratio,passed=ratio<=.9 and all(r['ratio']<=1.25 for r in rows),fixtures=rows)
    (RAW/'particle-independent-variance-v1.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k!='fixtures'}),flush=True)
    print('Diagnostic only: actual independent selection and learning qualification remain unimplemented',flush=True)
