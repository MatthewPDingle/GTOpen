"""Independent card-class, source and visible-flop routing readback."""
import hashlib
import itertools
import json
import os
from pathlib import Path
import time
import psutil

ROOT = Path('T:/Dev/GTOpen')
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME = 'stack-context-private-hand-holdout-readback-v1-result.json'


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def encoded(value):return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def read(path):return json.loads(Path(path).read_bytes())
def check_document(doc):
    raw = {k:v for k,v in doc.items() if k != 'sha256'}
    assert hashlib.sha256(encoded(raw)).hexdigest() == doc['sha256']
def hand_class(hand):
    r1,r2=hand[0]//4,hand[1]//4
    if r1 == r2:return 14*r1
    return max(r1,r2)*13+min(r1,r2) if hand[0]%4 == hand[1]%4 else min(r1,r2)*13+max(r1,r2)
def private_side(hand,cfg):
    raw = hashlib.sha256(encoded(['own-169-hand-class-holdout-v1',cfg['sha256'],hand_class(hand)])).digest()
    return 'test' if int.from_bytes(raw,'big') % cfg['buckets'] in cfg['test_buckets'] else 'fit'
def canonical(flop):
    return min(tuple(sorted(4*(c//4)+p[c%4] for c in flop)) for p in itertools.permutations(range(4)))
def public_side(board,cfg):
    key = list(canonical(board[:3]))
    raw = hashlib.sha256(encoded(['public-canonical-flop-partition-v1',cfg['sha256'],key])).digest()
    return 'test' if int.from_bytes(raw,'big') % cfg['buckets'] in cfg['test_buckets'] else 'fit'
def verify(row,hand,board,phase,actor,depth,source,index,cfg,fcfg,sources):
    own=private_side(hand,cfg);public=public_side(board,fcfg) if phase else None
    axes=(['depth'] if depth == 'heldout' else [])+(['own-hand'] if own == 'test' else [])
    axes+=['public-flop'] if public == 'test' else []
    assert row['phase'] == phase and row['actor'] == actor and row['hand_class'] == hand_class(hand)
    assert row['own_hand_split'] == own and row['public_flop_split'] == public and row['holdout_axes'] == axes
    assert row['depth_split'] == depth and row['source_side'] == source and row['parent_draw_index'] == index
    side='test' if axes else 'fit';assert row['label_side'] == side
    assert row['label_generation_allowed'] == (side == source)
    source_id=sources[source+'_source_identity'];assert row['source_identity'] == source_id
    assert row['source_cluster_identity'] == hashlib.sha256(encoded(['disjoint-prediction-source-routing-v1',source_id,index])).hexdigest()
    assert row['private_hand_config_sha256'] == cfg['sha256'] and row['public_flop_config_sha256'] == fcfg['sha256']
    assert row['source_config_sha256'] == sources['sha256']
    assert row['unseen_own_hand_excluded_from_all_fitting'] and row['partition_is_metadata_not_model_input']
    assert not row['preflop_future_board_used'] and not row['opponent_cards_used'] and not row['scientific_admission']
    if phase:assert row['canonical_public_flop'] == list(canonical(board[:3]))
    else:assert 'canonical_public_flop' not in row
    check_document(row)


def main():
    target=OUT/NAME
    if target.exists():raise ValueError('Preserve existing independent readback')
    result_path=OUT/'stack-context-private-hand-holdout-check-v1-result.json'
    attempt_path=OUT/'stack-context-private-hand-holdout-check-v1-attempt.json'
    result,attempt=read(result_path),read(attempt_path)
    assert result['complete'] and result['passed'] and result['inputs'] == attempt['inputs']
    assert not (OUT/'stack-context-private-hand-holdout-check-v1-failure.json').exists()
    for path,identity in result['inputs'].items():assert sha(path) == identity
    assert result['qualification_only'] and not result['scientific_accuracy_evidence']
    assert result['scientific_samples'] == result['native_calls'] == result['fits'] == 0 and not result['gpu']
    assert not result['production_modified'] and not result['actual_diagnostic_registered'] and not result['actual_diagnostic_complete']
    cfg,fcfg,sources=[result[k] for k in ('synthetic_hand_contract','synthetic_flop_contract','synthetic_sources_contract')]
    for doc in (cfg,fcfg,sources):check_document(doc)
    assert cfg == attempt['synthetic_hand_contract'] and fcfg == attempt['synthetic_flop_contract'] and sources == attempt['synthetic_sources_contract']
    assert cfg['test_buckets'] == [0,3] and cfg['buckets'] == 7 and fcfg['test_buckets'] == [1] and fcfg['buckets'] == 5
    assert sources['fit_source_identity'] != sources['test_source_identity'] and sources['independence_is_registration_requirement']
    counts=[0]*169;totals={'fit':0,'test':0}
    for pair in itertools.combinations(range(52),2):
        counts[hand_class(pair)]+=1;totals[private_side(pair,cfg)]+=1
    assert counts == result['independent_physical_counts']
    catalogue=result['catalogue']
    # The in-memory combinatorial count map uses integer multiplicity keys;
    # JSON preserves their spelling as strings. Restore that declared type
    # only for checking its original semantic digest, without changing evidence.
    original_catalogue=catalogue|{'combo_multiplicities':{int(k):v for k,v in catalogue['combo_multiplicities'].items()}}
    check_document(original_catalogue)
    assert catalogue['config'] == cfg and catalogue['hand_classes'] == 169 and catalogue['physical_combos'] == 1326
    assert catalogue['combo_multiplicities'] == {'4':78,'6':13,'12':78} and catalogue['physical_combos_by_split'] == totals
    for row in catalogue['rows']:
        c=row['hand_class'];assert counts[c] == row['physical_combos'] and hand_class(row['representative']) == c
        assert private_side(row['representative'],cfg) == row['split']
    assert result['suit_order_checks'] == 63648 and result['visible_suit_checks'] == 2304
    assert len(result['controls']) == 112 and result['descendants_checked'] == 96
    for control in result['controls']:
        verify(control['expected'],control['hand'],control['board'],control['phase'],control['actor'],
            control['depth_split'],control['source_side'],control['draw_index'],cfg,fcfg,sources)
    observations={d:read(Path(f'S:/GTOpen-research/stack-context-matched-evaluation-integration-check-v1/{d}-cached/queries.json'))['observations']
        for d in (20,60)}
    assert sum(map(len,observations.values())) == 918 and len(result['retained_native_controls']) == 1836
    for control in result['retained_native_controls']:
        depth,index=control['fixture_depth'],control['observation_index'];obs=observations[depth][index]
        value=int(obs['lo']);cards=[(value >> (6*i)) & 63 for i in range(7)]
        n=(2,5,6,7)[obs['phase']]
        assert (value >> 42) & 1 == obs['actor'] and all(c == 63 for c in cards[n:])
        assert len(set(cards[:n])) == n and all(c < 52 for c in cards[:n])
        verify(control['expected'],cards[:2],cards[2:n],obs['phase'],obs['actor'],
            'fit' if depth == 20 else 'heldout',control['source_side'],index,cfg,fcfg,sources)
    assert len(result['corruption_rejections']) == len(set(result['corruption_rejections'])) == 31
    reg=OUT/'stack-context-matched-learning-v1-registration.json'
    assert sha(reg) == 'ea0665fcb2ae2888a0aca0fd8ee282d06656d013fa41d98e8981cdc3f52c25e3'
    live=[]
    for pid,created,parent in ((84788,1790752536.9318762,2980),(94544,1790753443.077002,84788),
        (100604,1790753511.1853917,94544),(93416,1790753512.997676,94544),
        (104568,1790753514.8583736,94544),(81788,1790753516.7905183,94544)):
        p=psutil.Process(pid);assert abs(p.create_time()-created)<.01 and p.ppid() == parent
        live.append(dict(pid=pid,created=p.create_time(),parent=p.ppid(),command=p.cmdline()))
    status_path=OUT/'stack-context-parallel-continuation-v2-status.json';status=read(status_path)
    assert time.time()-status_path.stat().st_mtime<60 and status['stage'] == 'parallel-training' and status['pid'] == 94544
    assert not list(OUT.glob('stack-context-parallel-continuation-v2*failure.json'))
    store=Path('S:/GTOpen-research/stack-context-matched-learning-v1')
    progress={a:read(store/a/'progress.json')['completed_cycles'] for a in ('A-baseline','A-relative','B-baseline','B-relative')}
    receipt=dict(complete=True,passed=True,unix=time.time(),reader_source_sha256=sha(__file__),
        result_sha256=sha(result_path),attempt_sha256=sha(attempt_path),authenticated_inputs=len(result['inputs']),
        independent_physical_pairs=1326,independent_classes=169,independent_route_controls=112,
        retained_native_observations=918,retained_native_routes=1836,private_physical_sides=totals,
        qualification_only=True,scientific_samples=0,native_calls=0,fits=0,gpu=False,
        production_modified=False,actual_diagnostic_registered=False,actual_diagnostic_complete=False,
        scientific_accuracy_evidence=False,registration_sha256=sha(reg),live_processes=live,published_cycles=progress)
    with target.open('xb') as stream:stream.write(encoded(receipt));stream.flush();os.fsync(stream.fileno())
    print(json.dumps({k:receipt[k] for k in ('passed','authenticated_inputs','private_physical_sides','published_cycles')}))


if __name__ == '__main__':main()
