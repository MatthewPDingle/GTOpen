"""Independent arithmetic, candidate selection, gate and saved-audit verification."""
import gzip,hashlib,json,math
from run07 import HERE,LAB,RAW,digest
from check_root_repair import checked_local,f32
from check_joint import require
NAME='large-sampled-conditional-policy-v1'
GRID=[0.125,0.25,0.5,0.875,1.0]
def checked(c,paths):
    gaps=c['global_gaps'];evs=c['global_evs']
    require(len(gaps)==len(evs)==8 and all(math.isfinite(x) for x in gaps+evs) and min(gaps)>=0,'Invalid global values')
    require(abs(sum(gaps)-c['gap'])<1e-12,'Incorrect gap total')
    passed=checked_local(c['rows'],paths)
    reachable=all(r['candidate']['status']=='evaluated' for r in c['rows'])
    require(c['reachable'] is reachable and c['passed']==passed,'Incorrect coverage')
    losses=[]
    for row in c['rows']:
        r=row['candidate']
        if r['status']!='evaluated':losses.append(None);continue
        loss=sum(h['conditional_hand_mass']*sum(p*(max(h['action_values_bb'])-q)
            for p,q in zip(h['candidate_probabilities'],h['action_values_bb'])) for h in r['hands'])
        require(abs(loss-r['weighted_action_loss_bb'])<=1e-10,'Incorrect weighted loss')
        losses.append(loss)
    require(c['qualified'] is (sum(gaps)<=0.005 and passed==39 and reachable),'Incorrect qualification')
    require((c['objective'] is None and not reachable) or (reachable and abs(c['objective']-sum(losses[:27]))<=1e-10),'Incorrect objective')
    return losses

def verify():
    envelope=json.loads((RAW/(NAME+'-result-envelope.json')).read_text())
    packed=RAW/(NAME+'-result.json.gz');data=gzip.decompress(packed.read_bytes());r=json.loads(data)
    require(digest(packed)==envelope['gzip_sha256'] and hashlib.sha256(data).hexdigest()==envelope['original_sha256'] and len(data)==envelope['original_bytes'],'Result hash mismatch')
    for name in (NAME,NAME+'-audit'):
        process=json.loads((RAW/(name+'-exit.json')).read_text())
        require(process['returncode']==0 and process['reason'] is None,'Incomplete process')
        for path,h in process['inputs'].items():require(digest(path)==h,'Changed input '+path)
    require(r['nodes']==1567754 and r['global_age']==1050,'Wrong anchor')
    require(r['regrets_unchanged'] and r['unselected_averages_unchanged'] and r['roundtrip_exact'],'Preservation failed')
    require(r['normal_global_resume_supported'] is False,'Unsafe resume claim')
    originals=json.loads((HERE/'broad-paths.json').read_text());plan=r['plan']
    require([n['path'] for n in plan['selected']]==originals,'Original coverage changed')
    paths=json.loads((RAW/(NAME+'-all-paths.json')).read_text())
    require(paths==originals+plan['heldout_paths'] and len(paths)==39 and len(set(map(tuple,paths)))==39,'Invalid held-out coverage')
    require(plan==json.loads((RAW/(NAME+'-plan.json')).read_text()),'Plan differs')
    held=plan['heldout_paths'];require(held==sorted(held,key=lambda p:(len(p),p)),'Held-out order changed')
    require(all(0<n['subtree_nodes']<=50000 and n['start']<n['end'] for n in plan['selected']),'Invalid selected geometry')
    anchor=r['anchor'];anchor_losses=checked(anchor,paths)
    require(anchor['reachable'] and anchor['gap']<=0.005,'Unqualified global anchor')
    require(all(abs(a-b)<=1e-5 for a,b in zip(r['original_global_gaps'],anchor['global_gaps'])),'Normalization changed global evaluation')
    current=anchor;summaries=[]
    require(0<=len(r['cycles'])<=3,'Cycle budget changed')
    for cycle in r['cycles']:
        base=cycle['baseline']
        require(base['rows']==current['rows'] and base['global_gaps']==current['global_gaps'],'Wrong cycle baseline')
        require(not base['qualified'],'Continued qualified policy')
        sources=[];targets=[]
        for row in base['rows'][:27]:
            c=row['candidate'];na=len(c['actions']);source=[0.]*(169*na);target=source.copy()
            for h,hand in enumerate(c['hands']):
                q=hand['action_values_bb'];p=list(map(f32,hand['candidate_probabilities']))
                eligible=[a for a in range(na) if max(q)-q[a]<=1e-8];mass=sum(p[a] for a in eligible)
                for a in range(na):source[a*169+h]=p[a]
                for a in eligible:target[a*169+h]=f32(p[a]/mass) if mass>0 else f32(1/f32(len(eligible)))
            sources.append(source);targets.append(target)
        require(targets==[list(map(f32,t)) for t in cycle['targets']],'Target is not registered value-directed response')
        require([c['alpha'] for c in cycle['candidates']]==GRID,'Changed alpha grid')
        eligible_indices=[];compact=[]
        for i,c in enumerate(cycle['candidates']):
            losses=checked(c,paths);alpha=GRID[i]
            for source,target,actual in zip(sources,targets,c['policies']):
                expect=[f32((1-alpha)*p+alpha*t) for p,t in zip(source,target)]
                for h in range(169):
                    mass=sum(expect[h::169])
                    for j in range(h,len(expect),169):expect[j]=f32(expect[j]/mass)
                require(expect==list(map(f32,actual)),'Wrong candidate mixture')
            for row,weights in zip(c['rows'][:27],c['policies']):
                if row['candidate']['status']!='evaluated':continue
                for h,hand in enumerate(row['candidate']['hands']):
                    mass=0.0
                    for w in weights[h::169]:mass=f32(mass+f32(w))
                    expected=[f32(f32(w)/mass) for w in weights[h::169]]
                    require(expected==list(map(f32,hand['candidate_probabilities'])),'Applied policy differs from mixture')
            protected=c['reachable'] and c['gap']<=0.005 and all(losses[j]<=anchor_losses[j]+1e-5
                and (not anchor['rows'][j]['candidate']['passes_local_tail_gate'] or c['rows'][j]['candidate']['passes_local_tail_gate']) for j in range(27,39))
            require(c['eligible'] is protected,'Wrong held-out/global protection')
            if protected:eligible_indices.append(i)
            compact.append(dict(alpha=alpha,gap=c['gap'],passed=c['passed'],objective=c['objective'],eligible=protected))
        selected=min(eligible_indices,key=lambda i:(cycle['candidates'][i]['objective'],GRID[i])) if eligible_indices else None
        if selected is not None and cycle['candidates'][selected]['objective']>=base['objective']-1e-6:selected=None
        require(selected==cycle['selected_index'],'Wrong objective selection')
        current=base if selected is None else cycle['candidates'][selected]
        summaries.append(dict(candidates=compact,selected_index=selected))
        if selected is None:require(cycle is r['cycles'][-1],'Continued after no improvement')
    final=r['final_check'];second=r['second_check'];checked(final,paths);checked(second,paths)
    for check in (final,second):require(check['rows']==current['rows'] and check['global_gaps']==current['global_gaps'],'Final recheck mismatch')
    audit=json.loads((RAW/(NAME+'-audit.json')).read_text())
    require([x['candidate'] for x in audit['rows']]==[x['candidate'] for x in final['rows']],'Independent saved audit mismatch')
    require(math.isfinite(r['seconds']) and r['seconds']>0,'Invalid elapsed time')
    return dict(evidence_verified=True,seconds=r['seconds'],anchor_gap=anchor['gap'],anchor_passed=anchor['passed'],
        cycles=summaries,final_gap=final['gap'],final_passed=final['passed'],accuracy_screen_passed=final['qualified'],
        large_game_speed_qualified=False,scope='Bounded saved-policy repair only; fresh end-to-end speed remains unproven')
if __name__=='__main__':print(json.dumps(verify(),indent=2))
