"""Read back posterior64 terminal evidence and preserve the preflight failure."""
import hashlib,json,os,time
from pathlib import Path

OUT=Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')
ROOT=Path('T:/Dev/GTOpen')
DEST=OUT/'river-posterior64-evidence-review-v1.json'
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,value):
    raw=(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
    with p.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
    assert read(p)==value

def main():
    assert not DEST.exists();results=[]
    for name in ('river-posterior64-control-v2','river-posterior64-native-control-v1'):
        folder=OUT/name;rp=OUT/(name+'-registration.json');ep=OUT/(name+'-result.json')
        reg,result=read(rp),read(ep)
        assert result['passed'] and result['complete'] and result['registration_sha256']==sha(rp)
        assert not result['gpu_used'] and not result['training'] and not result['production_modified']
        assert not (OUT/(name+'-failure.json')).exists()
        for path,h in reg['inputs'].items():assert sha(Path(path))==h,path
        assert len(result['cases'])==8
        for case in result['cases']:
            p=folder/case['case']/'result.json' if 'native' in name else folder/(case['case']+'.json')
            assert read(p)==case
            for path,h in case.get('artifacts',{}).items():assert sha(folder/case['case']/path)==h,path
        files={str(p.relative_to(folder)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(folder.rglob('*')) if p.is_file()}
        count=sum(x['bytes'] for x in files.values());assert count<reg['maximum_bytes']
        results.append(dict(name=name,inputs_checked=len(reg['inputs']),registration_sha256=sha(rp),result_sha256=sha(ep),retained_bytes=count,artifacts=files))
    oldname='river-posterior64-control-v1'
    assert (OUT/oldname).is_dir() and not list((OUT/oldname).iterdir())
    assert not (OUT/(oldname+'-registration.json')).exists()
    failure=OUT/(oldname+'-failure.json')
    write(failure,dict(terminal=True,stage='pre-registration preflight',compute_started=False,
        error="KeyError: 'd000-9266201-board-root/new/export.json'",evidence_origin='Observed runner exit 1 before the registration write; empty output directory retained.',
        source_sha256=sha(ROOT/'tools/research/river_posterior64_control_v1.py'),
        correction='Version 2 uses native Windows manifest separators; all experimental choices unchanged.',reviewed_unix=time.time()))
    payload=dict(passed=True,reviewed_unix=time.time(),source_sha256=sha(Path(__file__)),experiments=results,preflight_failure_sha256=sha(failure),
                 scope='Evidence integrity and source readback only; not a new quality test.')
    write(DEST,payload)
    print(json.dumps(dict(passed=True,experiments=2,files=sum(len(x['artifacts']) for x in results),retained_bytes=sum(x['retained_bytes'] for x in results))))

if __name__=='__main__':main()
