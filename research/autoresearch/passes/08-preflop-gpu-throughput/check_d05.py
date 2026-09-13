"""Independent D05 histogram, exhaustive partition and memory/admission audit."""
import functools,hashlib,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parents[3];RAW=HERE/'raw'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
@functools.cache
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()
def partitions(n):
    # Independent enumeration: insert each new seat into an existing block or
    # create one new block. The Rust enumerator instead chooses the first block.
    result=[()]
    for p in range(n):
        next=[]
        for old in result:
            next.append(old+(1<<p,))
            for i,group in enumerate(old):
                if group.bit_count()<4: next.append(old[:i]+(group|(1<<p),)+old[i+1:])
        result=next
    return set(result)
def main():
    pre=read(RAW/'d05-cohort-tests-v2-exit.json');sources=pre['solver_source_files']
    assert pre['returncode']==0 and pre['reason'] is None
    assert '2 passed; 0 failed; 1 ignored' in (RAW/'d05-cohort-tests-v2.log').read_text()
    mapping={str(Path(k)):v for k,v in read(HERE/'artifacts/d05-source-map.json').items()}
    for p,h in sources.items():
        if p in mapping:assert digest(HERE/mapping[p])==h,p
        else:
            blob=subprocess.check_output(['git','show',pre['source_commit']+':'+Path(p).as_posix()],cwd=LAB)
            assert hashlib.sha256(blob).hexdigest()==h,p
    for p,h in pre['inputs'].items():assert digest(Path(p))==h,p
    frozen=LAB/'target/d05-inventory-frozen.exe';fixtures={}
    for fixture,n in [('small',6),('large',8)]:
        name=f'd05-{fixture}-v1';rec=read(RAW/(name+'-exit.json'));x=read(RAW/(name+'.json'))
        assert rec['returncode']==0 and rec['reason'] is None and rec['seconds']<=180
        assert rec['solver_source_files']==sources and rec['exe_sha256']==digest(frozen)
        for p,h in rec['inputs'].items():assert digest(frozen if p==rec['command'][0] else Path(p))==h,p
        assert rec['environment_overrides']['PREFLOP_GPU_COHORT_INVENTORY']=='1'
        old=read(RAW/f'd04-{fixture}-v1.json')
        for k in ['input','players','nodes','iteration','batch','rows','baseline_cdf_rows','all_player_union','pairs',
            'same_source_rechecks','source_identities','all_static_union','buffer_bytes','base_bytes','retained_c01_bytes',
            'best_pairing','natural_pairing','all_pairings']:assert x[k]==old[k],(fixture,k)
        assert x['players']==n and x['batch']==32 and x['read_only'] and x['arenas_unchanged'] and x['average_reaches_unchanged']
        c=x['cohorts'];all=(1<<n)-1
        def union(h,subset):return sum(v for mask,v in enumerate(h) if mask&subset)
        for hkey,ukey,total in [('static_membership_histogram','static_subset_unions',x['all_static_union']),
            ('unique_membership_histogram','unique_subset_unions',x['all_player_union'])]:
            hist=c[hkey];u=c[ukey]
            assert len(hist)==len(u)==1<<n and hist[0]==0 and sum(hist)==total
            assert u==[union(hist,s) for s in range(1<<n)]
        su=c['static_subset_unions'];uu=c['unique_subset_unions']
        for p,row in enumerate(x['rows']):assert su[1<<p]==row['static_slots'] and uu[1<<p]==row['unique_distributions']
        for pair in x['pairs']:
            p,q=pair['players'];mask=(1<<p)|(1<<q)
            assert su[mask]==pair['static_union'] and uu[mask]==pair['unique_union']
        expected=partitions(n);actual={tuple(p[0]) for p in c['all_partitions']}
        assert actual==expected and len(actual)==len(c['all_partitions'])==c['partitions_count']
        b=x['buffer_bytes'];base=x['base_bytes'];capacity=b['d_mw_normalized']//(169*4);baseline=x['baseline_cdf_rows']
        pow2=lambda v:1<<(v-1).bit_length()
        def costs(groups):
            largest=max(g.bit_count() for g in groups);cap=max(capacity,max(su[g] for g in groups))
            fields=dict(cdf_bytes=cap*32*170*4,normalized_bytes=cap*169*4,classification_bytes=(cap+pow2(cap*2))*4,
                maps_bytes=len(groups)*su[all]*4,work_bytes=sum(su[g]*4 for g in groups),
                extra_value_bytes=(largest-1)*b['d_val'],extra_prob_bytes=(largest-1)*b['d_mw_prob'])
            total=base-b['d_mw_cdf']-b['d_mw_normalized']+sum(fields.values())
            fields.update(largest_group=largest,static_capacity=cap,total_bytes=total,reserve_bytes=256*1024*1024,
                planned_initial_peak_bytes=total+256*1024*1024,cdf_rows=sum(uu[g] for g in groups),static_rows=sum(su[g] for g in groups))
            fields['replace_existing_peak_bytes']=fields['planned_initial_peak_bytes']+b['d_mw_cdf']+b['d_mw_normalized']+(capacity+pow2(capacity*2))*4
            fields['fits_preplanned_23gb']=fields['planned_initial_peak_bytes']<=23_000_000_000
            fields['saved_fraction']=1-fields['cdf_rows']/baseline
            return fields
        computed={g:costs(g) for g in actual}
        for groups,rows,static_rows,peak in c['all_partitions']:
            d=computed[tuple(groups)];assert (rows,static_rows,peak)==(d['cdf_rows'],d['static_rows'],d['planned_initial_peak_bytes'])
        eligible=[g for g,d in computed.items() if d['fits_preplanned_23gb']]
        selected=min(eligible,key=lambda g:(computed[g]['static_rows'],computed[g]['total_bytes'],json.dumps(g,separators=(',',':'))))
        assert c['selected_static_plan']['group_masks']==list(selected)
        assert c['best_observed_fitting_plan']['cdf_rows']==min(computed[g]['cdf_rows'] for g in eligible)
        fullplans=[c['selected_static_plan'],c['best_observed_fitting_plan']]+c['natural_plans']+c['pareto_frontier']
        for p in fullplans:
            d=computed[tuple(p['group_masks'])]
            for k,v in d.items():assert p[k]==v,(fixture,k)
        # Frontier must have exactly every nondominated memory/work coordinate.
        points={(d['planned_initial_peak_bytes'],d['cdf_rows']) for d in computed.values()}
        frontier=set();best=float('inf')
        for peak,rows in sorted(points):
            if rows<best:frontier.add((peak,rows));best=rows
        assert frontier=={(p['planned_initial_peak_bytes'],p['cdf_rows']) for p in c['pareto_frontier']}
        assert c['admitted']==(computed[selected]['saved_fraction']>=.25)
        fixtures[fixture]=dict(selected=c['selected_static_plan'],partitions=c['partitions_count'],admitted=c['admitted'])
    assert fixtures['large']['admitted']
    result=dict(retained=False,status='Inventory passed - prototype admitted',verified=True,
        source_input_hashes_verified=True,read_only_arena_preservation=True,fixtures=fixtures,
        executable_sha256=digest(frozen),scope='No speed measurement. Static grouping fits the registered unchanged-batch memory plan; prototype numerical and timing qualification remain.')
    (RAW/'d05-verified.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
