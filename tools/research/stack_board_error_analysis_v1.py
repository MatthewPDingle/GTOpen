"""Descriptive aggregation of the completed fit/validation-only diagnosis."""
import hashlib,json
from pathlib import Path
from board_prefix_publication_v1 import atomic_json
OUT=Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')
SOURCE=OUT/'stack-board-error-diagnosis-v2-result.json'
DEST=OUT/'stack-board-error-diagnosis-v2-analysis.json'
CATEGORIES=('high_card','pair','two_pair','trips','straight','flush','full_house','quads','straight_flush')
RELATIONS=('plays_board','same_category_better_kickers','improves_category')
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    assert not DEST.exists()
    r=read(SOURCE);regpath=OUT/'stack-board-error-diagnosis-v2-registration.json';reg=read(regpath)
    assert r['passed'] and r['registration_sha256']==sha(regpath)
    assert r['gpu_used'] is False and not r['test_boards_used'] and not r['heldout_depths_used']
    for paths in (reg['inputs'],r['artifacts']):
        for p,h in paths.items():assert sha(p)==h,p
    records=[]
    for record in r['records']:
        splits=[]
        for split in record['splits']:
            contexts=split['contexts'];base=split['rules'][0]['context_balanced_mean_regret_stack_fraction']
            groups={}
            for name in ('relations','board_categories','hand_categories','actors','price_bands','boards'):
                rows=[]
                for index in [v['index'] for v in contexts[0][name]]:
                    matched=[(c,next(v for v in c[name] if v['index']==index)) for c in contexts]
                    if not any(v['rows'] for c,v in matched):continue
                    contribution=sum(v['rows']/c['rows']*v['rules'][0]['mean_regret_stack_fraction'] for c,v in matched if v['rows'])/len(contexts)
                    mass=sum(v['rows']/c['rows'] for c,v in matched)/len(contexts)
                    row=dict(index=index,mean_row_share=mass,normalized_loss_contribution=contribution,
                        loss_share=contribution/base,group_mean_normalized_loss=contribution/mass)
                    if name=='relations':row['name']=RELATIONS[index]
                    if name in ('hand_categories','board_categories'):row['name']=CATEGORIES[index]
                    rows.append(row)
                assert abs(sum(v['mean_row_share'] for v in rows)-1)<1e-12
                assert abs(sum(v['loss_share'] for v in rows)-1)<1e-10
                groups[name]=sorted(rows,key=lambda x:-x['loss_share'])
            splits.append(dict(split=split['split'],base_mean_normalized_loss=base,groups=groups,
                conversion_improvements=[dict(rule=v['name'],relative_reduction=1-v['context_balanced_mean_regret_stack_fraction']/base) for v in split['rules'][1:]]))
        ratio=splits[1]['base_mean_normalized_loss']/splits[0]['base_mean_normalized_loss']
        records.append(dict(seed=record['seed'],validation_to_fit_subset_loss_ratio=ratio,splits=splits))
    result=dict(passed=True,source_sha256=sha(__file__),inputs={str(SOURCE):sha(SOURCE),str(regpath):sha(regpath)},
        records=records,scope='Exploratory description of existing fitting subset and validation losses; no new scientific gate.',
        new_training=False,test_boards_used=False,production_modified=False)
    atomic_json(DEST,result)
    for r in records:
        print(json.dumps(dict(seed=r['seed'],validation_to_fit_subset_loss_ratio=r['validation_to_fit_subset_loss_ratio'],
            validation={k:v for k,v in r['splits'][1].items() if k!='groups'},
            groups={k:v[:5] for k,v in r['splits'][1]['groups'].items() if k in ('relations','hand_categories','boards')})),flush=True)
if __name__=='__main__':main()
