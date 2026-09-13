"""Audit extraction provenance and independently decode all support identities."""
import collections,gzip,hashlib,json
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw';LAB=HERE.parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    r=read(RAW/'d17-occupancy.json');frozen=read(RAW/'d17-frozen.json')
    assert sha(Path(frozen['executable']))==frozen['sha256']
    records=['d17-support-test-v1','d17-small-v1','d17-large-v1','d17-occupancy-v1']
    for name in records:
        rec=read(RAW/(name+'-exit.json'));assert rec['returncode']==0 and rec['reason'] is None
        assert rec['seconds']<=(300 if name==records[0] else 180)
        for p,h in rec['inputs'].items():assert sha(Path(p))==h,p
        for p,h in rec['solver_source_files'].items():assert sha(LAB/p)==h,p
    mapping=read(HERE/'artifacts/d17-v1-source-map.json')
    assert len(mapping)==1
    for p,h in mapping.items():
        assert sha(LAB/p)==sha(HERE/'artifacts/d17-v1/terminal_tiles.rs')==h
    for name,h in r['sources'].items():assert sha(RAW/name)==h
    assert r['protocol_sha256']==sha(HERE/'D17_PROTOCOL.md') and r['script_sha256']==sha(HERE/'d17_occupancy.py')
    z=(RAW/'d17-pattern-counts.json.gz').read_bytes()
    assert hashlib.sha256(z).hexdigest()==r['pattern_counts_compressed_sha256']
    data=gzip.decompress(z);assert hashlib.sha256(data).hexdigest()==r['pattern_counts_sha256'];patterns=json.loads(data)
    dtype=np.dtype([('mode','<u4'),('seat','<u4'),('id','<u4'),('bits','<u8',(3,))]);assert dtype.itemsize==36
    bounds={}
    for fixture,f in r['fixtures'].items():
        name=f'd17-{fixture}-v1';manifest=read(RAW/(name+'-manifest.json'))
        prior=read(RAW/f'd10-{fixture}-v1-witness-manifest.json')
        for a,b in [('save_sha256','save_sha256'),('original_witness_sha256','witness_sha256'),('original_json_sha256','output_sha256')]:
            assert manifest[a]==prior[b]
        assert manifest['executable_sha256']==frozen['sha256'] and manifest['original_d10_exact']
        witness=LAB/f'target/{name}-witness.bin';assert sha(witness)==prior['witness_sha256']
        packed=(RAW/(name+'-support.bin.gz')).read_bytes();assert hashlib.sha256(packed).hexdigest()==manifest['compressed_sha256']
        b=gzip.decompress(packed);assert hashlib.sha256(b).hexdigest()==manifest['support_sha256'] and len(b)==manifest['support_bytes']
        assert b[:8]==b'D17V1\0\0\0';np_=int.from_bytes(b[8:12],'little')
        rows=np.frombuffer(b[12:],dtype=dtype);assert len(rows)==f['distinct_rows'] and np.all(rows['mode']==0)
        counts={int(x['mask'],16):x for x in patterns[fixture]};assert len(counts)==len(patterns[fixture])==f['unique_support_patterns']
        aggregate=collections.Counter();sum_empty=0
        old=read(RAW/f'd10-{fixture}-v1.json');assert old['players']==np_==len(f['seats'])
        for seat in range(np_):
            selected=rows[rows['seat']==seat];assert np.array_equal(selected['id'],np.arange(len(selected)))
            histogram=[0]*170;empty=0
            for a,b,c in selected['bits']:
                assert int(c)>>41==0
                mask=int(a)+(int(b)<<64)+(int(c)<<128);assert mask
                histogram[mask.bit_count()]+=1;aggregate[mask]+=1;empty+=counts[mask]['empty_tiles']
            expected=next(x for x in old['rows'] if x['mode']==0 and x['player']==seat)
            assert expected['unique_support_histogram']==histogram and expected['unique_distributions']==len(selected)
            assert f['seats'][seat]==dict(seat=seat,rows=len(selected),empty_tile_scans=empty)
            sum_empty+=empty
        assert aggregate=={p:v['rows'] for p,v in counts.items()}
        assert sum_empty==f['empty_tile_scans'] and f['total_tile_scans']==len(rows)*6144
        assert f['empty_fraction']==sum_empty/f['total_tile_scans']
        bounds[fixture]=f['empty_fraction']
    assert r['independent_three_word_and_integer_methods_agree']
    admitted=bounds['large']>=.20;assert admitted==r['admit_gpu_prototype']
    out=dict(verified=True,admitted=admitted,retained=False,
        status='Actual empty learning tiles admit GPU prototype' if admitted else 'Actual empty learning tile gate rejected',
        empty_fractions=bounds,original_identity_and_terminal_witnesses_exact=True,
        all_learning_arenas_and_iterations_unchanged=True,
        census_sha256=sha(RAW/'d17-occupancy.json'),protocol_sha256=r['protocol_sha256'],
        scope='Saved-state occupancy census; no measured kernel, complete-work or convergence gain.')
    dest=RAW/'d17-verified.json'
    if dest.exists():assert read(dest)==out
    else:dest.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
