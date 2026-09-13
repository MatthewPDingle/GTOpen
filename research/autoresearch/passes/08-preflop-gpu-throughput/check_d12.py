"""Audit guarded immutable D12 records and work accounting."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    rec=read(RAW/'d12-prefix-inventory-v1-exit.json');r=read(RAW/'d12-prefix-census.json')
    assert rec['returncode']==0 and rec['reason'] is None and rec['seconds']<=180
    assert rec['solver_source_files']==read(RAW/'d11-tracing-v1-exit.json')['solver_source_files']
    for p,h in rec['inputs'].items():assert digest(Path(p))==h,p
    assert digest(Path(rec['command'][0]))==rec['exe_sha256']
    for p,h in r['sources'].items():assert digest(RAW/p)==h,p
    assert digest(HERE/'D12_PROTOCOL.md')==r['protocol_sha256'] and digest(HERE/'d12_prefix_census.py')==r['script_sha256']
    assert r['pair_capacity']==12021 and r['bytes_per_pair']==43264 and r['budget_bytes']==512*1024**2 and r['reserved_bytes']==16*1024**2
    d11=read(RAW/'d11-work-census.json');plan=read(RAW/'d10-verified.json')
    for fixture,modes in r['fixtures'].items():
        m=read(RAW/f'd10-{fixture}-v1-witness-manifest.json')
        assert digest(RAW/f'd10-{fixture}-v1.json')==m['output_sha256']
        for label,v in modes.items():
            assert len(v['groups'])==(d11['fixtures'][fixture]['players'] if label=='learning' else len(plan['fixtures'][fixture]['cohorts']))
            keys=sum(g['selected_pairs'] for g in v['groups']);uses=sum(g['selected_uses'] for g in v['groups'])
            for g in v['groups']:
                assert g['selected_pairs']==min(12021,g['eligible_pairs']) and g['selected_uses']>=4*g['selected_pairs']
                assert g['payload_bytes']==g['selected_pairs']*43264
                assert g['payload_bytes']+r['reserved_bytes']<=r['budget_bytes']
            assert v['saved_source_operations']==(uses-keys)*14*169*1024
            assert v['saved_logical_bytes']==(2*uses-6*keys)*4*169*1024
            b=d11['fixtures'][fixture]['modes'][label]
            assert v['source_arithmetic_reduction']==v['saved_source_operations']/b['logical_fp_operations']
            assert v['logical_terminal_traffic_reduction']==v['saved_logical_bytes']/b['logical_cdf_gather_bytes']
    gate=all(v['source_arithmetic_reduction']>=.2 and v['logical_terminal_traffic_reduction']>=.1 for v in r['fixtures']['large'].values())
    assert r['admitted']==gate==False and r['independent_pair_counters_agree']
    result=dict(verified=True,admitted=gate,source_input_hashes_verified=True,work_accounting_verified=True,census_sha256=digest(RAW/'d12-prefix-census.json'),scope='Exact immutable snapshot census only; no GPU prototype or runtime improvement.')
    dest=RAW/'d12-verified.json'
    if dest.exists():assert read(dest)==result
    else:dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
