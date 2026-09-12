"""Freeze the fixed partition, then test GPU variance; no learning/deployment."""
from run07 import *

if __name__=='__main__':
    run('particle-batch-construction-v1',['cargo','test','--release','-p','solver','--features','preflop-research',
        '--lib','particle_batch_construction','--','--nocapture','--test-threads=1'],600)
    construction=[]
    for line in (RAW/'particle-batch-construction-v1.log').read_text().splitlines():
        if 'BATCH_CONSTRUCTION ' in line:construction.append(json.loads(line.split('BATCH_CONSTRUCTION ',1)[1]))
    if len(construction)!=1:raise RuntimeError('Missing construction manifest')
    manifest=RAW/'particle-batch-manifest-v1.json'
    if manifest.exists():raise RuntimeError('Existing manifest')
    manifest.write_text(json.dumps(construction[0],indent=2)+'\n',encoding='utf-8',newline='\n')
    run('particle-batch-numerical-v1',['cargo','test','--release','-p','solver','--features','preflop-research',
        '--lib','particle_batch_gpu_','--','--nocapture','--test-threads=1'],900,[manifest])
    rows=[]
    for line in (RAW/'particle-batch-numerical-v1.log').read_text().splitlines():
        if 'BATCH_VARIANCE ' in line:rows.append(json.loads(line.split('BATCH_VARIANCE ',1)[1]))
    if [(r['players'],r['family']) for r in rows]!=[(n,f) for n in (3,4,6,8) for f in range(3)]:
        raise RuntimeError('Incomplete variance coverage')
    if any(r['checksum_fnv64']!=construction[0]['checksum_fnv64'] for r in rows):raise RuntimeError('Changed partition')
    ratio=sum(r['pooled_variance'][1] for r in rows)/sum(r['pooled_variance'][0] for r in rows)
    eight=[r for r in rows if r['players']==8]
    eight_ratio=sum(r['pooled_variance'][1] for r in eight)/sum(r['pooled_variance'][0] for r in eight)
    result=dict(pooled_ratio=ratio,eight_player_ratio=eight_ratio,passed=ratio<=.9 and all(r['ratio']<=1.25 for r in rows),fixtures=rows)
    (RAW/'particle-batch-variance-v1.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k!='fixtures'}),flush=True)
    print('Numerical screen only; learning integration and capture checks still required',flush=True)
