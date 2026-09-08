"""Cross-check complete counters, exports and (optionally) the running API.

--server only calls /preflop/generate: no builds, solves, saves or seat changes.
--publish installs the already-reviewed models.json without refitting.
"""
import argparse, collections, json, math, urllib.request
from pathlib import Path
from fit import merge,n

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--input',default='output/coinpoker')
    ap.add_argument('--results',default='docs/coinpoker'); ap.add_argument('--server')
    ap.add_argument('--publish'); args=ap.parse_args()
    models=json.loads((Path(args.results)/'models.json').read_text(encoding='utf-8'))
    assert len({m['name'] for m in models})==len(models)
    for stake in ['NL10','NL25','NL50','NL100']:
        d=json.loads((Path(args.input)/(stake+'.json')).read_text()); a=d['audit']
        assert a['raw']==a['accepted']+a.get('duplicate',0)+sum(v for k,v in a.items() if k.startswith('excluded/')),stake
        assert not a.get('duplicate_variant'),stake
        for split in [0,1]:
            assert merge(cs[split] for cs in d['players'].values())==collections.Counter(d['pool'][split]),stake
        for cs in d['players'].values():
            for c in cs:
                h=n(c,'vpip')
                assert h==n(c,'pfr')==n(c,'position')==n(c,'occupancy')==n(c,'stack'),stake
                assert c.get('pfr|yes',0)<=c.get('vpip|yes',0),stake
        r=json.loads((Path(args.results)/(stake+'.json')).read_text())
        assert r['audit']==a
        assert r['models']==[m for m in models if m['source']['stakes']==stake]
        assert len(r['models'])==1+r['validation']['selected_k']
        typed=merge(c['counts'] for c in r['clusters'])
        assert n(typed,'vpip')+r['player_hands_under100']==n(r['pool_counts'],'vpip')
        for cl in r['clusters']: assert cl['players']>=30
        print(stake,'counter and export checks passed',flush=True)
    for m in models:
        s=m['stats']; pf=m['postflop']
        for k,v in s.items():
            if isinstance(v,(int,float)): assert math.isfinite(v) and 0<=v<=100,(m['name'],k)
        assert 0<=s['flatten']<=1 and s['pfr']<=s['vpip']
        assert s['threebet']<=s['cont_vs_raise'] and s['squeeze']<=s['cont_squeeze']
        assert s['open_raise']+s['open_limp']<=100 and s['iso_raise']+s['limp_behind']<=100
        bounds=s['cont_vs_raise_bands']; assert [b[0] for b in bounds]==[2.5,3.5,5.0,999.0]
        assert all(s['threebet']<=v<=100 for _,v in bounds)
        assert all(math.isfinite(x) and 0<=x<=100 for x in pf['cbet']+pf['fold_to_bet']+[pf['raise_bet'],pf['donk']])
        if args.server:
            body=json.dumps(dict(seat=0,stats=s,name=m['name'],adaptive_from=.25)).encode()
            req=urllib.request.Request(args.server.rstrip('/')+'/api/preflop/generate',data=body,headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(req,timeout=120) as res: generated=json.load(res)
            assert generated['profile']['buckets'],m['name']
    print(f'{len(models)} models passed'+(' live generation' if args.server else '')+' checks',flush=True)
    if args.publish:
        path=Path(args.publish)
        previous=json.loads(path.read_text(encoding='utf-8'))
        preserved=[m for m in previous if not m['name'].startswith('Data · CoinPoker · ')]
        tmp=path.with_suffix('.json.tmp')
        tmp.write_text(json.dumps(preserved+models,indent=1,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
        tmp.replace(path)
        print(f'Published {len(models)} CoinPoker models; preserved {len(preserved)} existing entries',flush=True)

if __name__=='__main__': main()
