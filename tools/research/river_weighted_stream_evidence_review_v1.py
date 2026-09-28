"""Seal weighted insertion and byte-identical stream evidence, retaining v1 failure."""
import hashlib,json,os,time
from pathlib import Path

OUT=Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')
DEST=OUT/'river-weighted-stream-evidence-review-v1.json'
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not DEST.exists();reports=[]
    for name,passed in [('river-weighted-overlay-control-v1',False),('river-weighted-overlay-control-v2',True),('river-stream-transport-control-v1',True)]:
        folder=OUT/name;rp=OUT/(name+'-registration.json');reg=read(rp)
        for path,h in reg['inputs'].items():assert sha(Path(path))==h,path
        ep=OUT/(name+('-result.json' if passed else '-failure.json'));result=read(ep)
        if passed:
            assert result['passed'] and result['complete'] and result['registration_sha256']==sha(rp)
            assert not result['gpu_used'] and not result['training'] and not result['production_modified']
            assert not (OUT/(name+'-failure.json')).exists()
            cases=result['cases']
        else:
            assert not (OUT/(name+'-result.json')).exists()
            assert 'all(n>0 for n in overflow)' in result['traceback']
            cases=[read(p) for p in sorted(folder.glob('d*/result.json'))]
        assert len(cases)==8
        for case in cases:
            assert read(folder/case['case']/'result.json')==case
            for path,h in case['artifacts'].items():assert sha(folder/case['case']/path)==h,path
        files={str(p.relative_to(folder)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(folder.rglob('*')) if p.is_file()}
        count=sum(x['bytes'] for x in files.values());assert count<reg['maximum_bytes']
        reports.append(dict(name=name,passed=passed,inputs_checked=len(reg['inputs']),registration_sha256=sha(rp),terminal_sha256=sha(ep),retained_bytes=count,artifacts=files))
    v2=read(OUT/'river-weighted-overlay-control-v2-result.json');stream=read(OUT/'river-stream-transport-control-v1-result.json')
    assert sum(c['river_rows'] for c in v2['cases'])==54
    assert sum(c['changed_river_values'] for c in v2['cases'])==50
    assert len(v2['negative_controls'])==17 and len(stream['negative_controls'])==14
    assert (stream['old_conditional_bytes'],stream['new_conditional_bytes'])==(34171727,675122)
    payload=dict(passed=True,reviewed_unix=time.time(),source_sha256=sha(Path(__file__)),experiments=reports,
                 scope='Evidence integrity only. V1 remains failed; v2 and streaming controls passed. No new fitted-policy quality evidence.')
    raw=(json.dumps(payload,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
    with DEST.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
    assert read(DEST)==payload
    print(json.dumps(dict(passed=True,experiments=len(reports),files=sum(len(r['artifacts']) for r in reports))))
if __name__=='__main__':main()
