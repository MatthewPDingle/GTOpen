"""Audit D04 evidence, all pairing costs and complete buffer accounting."""
import functools, hashlib, itertools, json, math, re, subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent; LAB=HERE.parents[3]; RAW=HERE/'raw'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
@functools.cache
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
    return h.hexdigest()
def main():
    mapping={str(Path(k)):v for k,v in read(HERE/'artifacts/d04-source-map.json').items()}
    pre=read(RAW/'d04-identity-v1-exit.json'); sources=pre['solver_source_files']
    assert pre['returncode']==0 and pre['reason'] is None
    for p,h in pre['inputs'].items(): assert digest(Path(p))==h,p
    assert '1 passed; 0 failed' in (RAW/'d04-identity-v1.log').read_text()
    for p,h in sources.items():
        if p in mapping: assert digest(HERE/mapping[p])==h,p
        else:
            blob=subprocess.check_output(['git','show',pre['source_commit']+':'+Path(p).as_posix()],cwd=LAB)
            assert hashlib.sha256(blob).hexdigest()==h,p
    fields=set(re.findall(r'^    (\w+): CudaSlice<', (HERE/'artifacts/d04-inventory/gpu.rs').read_text(encoding='utf-8'), re.M))
    frozen=LAB/'target/d04-inventory-frozen.exe'; exe_hash=digest(frozen); fixtures={}
    for fixture,players in [('small',6),('large',8)]:
        name=f'd04-{fixture}-v1'; rec=read(RAW/(name+'-exit.json')); x=read(RAW/(name+'.json'))
        assert rec['returncode']==0 and rec['reason'] is None and rec['seconds']<=180
        assert rec['solver_source_files']==sources and rec['exe_sha256']==exe_hash
        for p,h in rec['inputs'].items(): assert digest(frozen if p==rec['command'][0] else Path(p))==h,p
        assert x['players']==players and x['batch']==32 and x['read_only'] and x['arenas_unchanged'] and x['average_reaches_unchanged']
        assert x['same_source_rechecks']>0 and x['source_identities']==x['all_static_union']
        assert fields==set(x['buffer_bytes']) and x['base_bytes']==sum(x['buffer_bytes'].values())
        b=x['buffer_bytes']; capacity=b['d_mw_normalized']//(169*4)
        pow2=lambda v:1<<(v-1).bit_length()
        old_class=(capacity+pow2(capacity*2))*4
        assert x['retained_c01_bytes']==x['base_bytes']+old_class
        rows=x['rows']; total=sum(r['unique_distributions'] for r in rows)
        assert total==x['baseline_cdf_rows'] and [r['player'] for r in rows]==list(range(players))
        assert x['source_identities']+x['same_source_rechecks']==sum(r['positive_slots'] for r in rows)
        pairs={tuple(p['players']):p for p in x['pairs']}; assert len(pairs)==players*(players-1)//2
        for (p,q),v in pairs.items(): assert v['shared_rows']==rows[p]['unique_distributions']+rows[q]['unique_distributions']-v['unique_union']
        plans=x['all_pairings']; assert len(plans)==(15 if players==6 else 105)
        seen=set()
        for p in plans:
            groups=p['groups']; key=tuple(tuple(v) for v in groups); assert key not in seen; seen.add(key)
            assert sorted(itertools.chain.from_iterable(groups))==list(range(players))
            assert all(len(v)==2 for v in groups)
            count=sum(pairs[tuple(v)]['unique_union'] for v in groups)
            assert count==p['cdf_rows'] and math.isclose(p['saved_fraction'],1-count/total)
            cap=max(capacity,max(pairs[tuple(v)]['static_union'] for v in groups))
            assert p['static_capacity']==cap and p['observed_unique_capacity']==max(pairs[tuple(v)]['unique_union'] for v in groups)
            assert p['cdf_bytes']==cap*32*170*4 and p['normalized_bytes']==cap*169*4
            assert p['classification_bytes']==(cap+pow2(cap*2))*4
            assert p['extra_value_bytes']==b['d_val'] and p['extra_prob_bytes']==b['d_mw_prob']
            assert p['work_bytes']==sum(pairs[tuple(v)]['static_union']*4 for v in groups)
            assert p['maps_bytes']==len(groups)*x['all_static_union']*4
            computed=x['base_bytes']-b['d_mw_cdf']-b['d_mw_normalized']+sum(p[k] for k in ['cdf_bytes','normalized_bytes','classification_bytes','maps_bytes','work_bytes','extra_value_bytes','extra_prob_bytes'])
            assert computed==p['total_bytes'] and p['reserve_bytes']==256*1024*1024
            assert p['planned_initial_peak_bytes']==computed+p['reserve_bytes']
            assert p['replace_existing_peak_bytes']==p['planned_initial_peak_bytes']+b['d_mw_cdf']+b['d_mw_normalized']+old_class
            assert p['fits_preplanned_23gb']==(p['planned_initial_peak_bytes']<=23_000_000_000)
        assert x['best_pairing']['cdf_rows']==min(p['cdf_rows'] for p in plans)
        assert x['natural_pairing']['groups']==[list(range(i,i+2)) for i in range(0,players,2)]
        admitted=[p for p in plans if p['saved_fraction']>=.25 and p['fits_preplanned_23gb']]
        assert not admitted and x['admitted_pairing'] is None
        fixtures[fixture]={k:x[k] for k in ['nodes','players','baseline_cdf_rows','all_player_union','same_source_rechecks','best_pairing','natural_pairing']}
    result=dict(retained=False,status='Rejected pair sharing - insufficient work reduction',verified=True,
        source_input_hashes_verified=True,read_only_arena_preservation=True,fixtures=fixtures,
        executable_sha256=exe_hash,reason='Best large pairing saves 21.02% of CDF rows, below the registered 25% gate.',
        scope='Inventory only. No speed measurement or live deployment. Wider groups require a separate protocol and inventory.')
    (RAW/'d04-verified.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='fixtures'},indent=2))
if __name__=='__main__':main()
