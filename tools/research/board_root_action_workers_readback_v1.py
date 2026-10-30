"""Review all worker qualification receipts and exact retained outputs."""
import hashlib
import json
from pathlib import Path
import time

ROOT=Path('T:/Dev/GTOpen')
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
STORE=Path('S:/GTOpen-research/board-root-action-workers-v1')
CONTROL=Path('S:/GTOpen-research/board-root-action-control-v1')
PREFIX='board-root-action-workers-v1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def main():
    started=time.monotonic()
    rp,pp=[OUT/(PREFIX+'-'+s+'.json') for s in ('registration','result')]
    destination=OUT/(PREFIX+'-review.json')
    report_path=OUT/'BOARD-ROOT-ACTION-WORKER-FINDINGS.md'
    assert not destination.exists() and not report_path.exists()
    reg,result=read(rp),read(pp)
    assert result['passed'] and result['registration_sha256'] == sha(rp)
    assert reg['worker_counts'] == [1,4,8,12] and reg['jobs_per_count'] == 12
    assert reg['job_sequence'] == ['test-000000','test-032768']*6
    assert read(STORE/'owner.json') == dict(root=str(STORE),registration_sha256=sha(rp))
    for path,h in reg['inputs'].items(): assert sha(path) == h
    bindings={}
    tables=[];count=0
    expected_folders=set()
    for workers,row in zip(reg['worker_counts'],result['timings'],strict=True):
        assert row['workers'] == workers and row['jobs'] == len(row['rows']) == 12 and row['seconds'] > 0
        for index,receipt in enumerate(row['rows']):
            name=reg['job_sequence'][index]
            folder=STORE/f'w{workers:02d}-j{index:02d}';expected_folders.add(folder.name)
            assert folder.parent == STORE and not folder.is_symlink()
            assert {p.name for p in folder.iterdir()} == {'owner.json','native.json','action-values.json','receipt.json'}
            assert read(folder/'owner.json') == dict(root=str(folder),parent=str(STORE),workers=workers,index=index,batch=name)
            assert read(folder/'receipt.json') == receipt
            assert receipt['workers'] == workers and receipt['index'] == index and receipt['name'] == name
            assert receipt['all_values_exactly_equal'] and receipt['existing_deals_replayed'] == 32
            assert receipt['new_deals'] == 0 and receipt['original_native_rerun'] is False
            assert (folder/'native.json').read_bytes() == (CONTROL/name/'forced-native.json').read_bytes()
            assert (folder/'action-values.json').read_bytes() == (CONTROL/name/'action-values.json').read_bytes()
            assert sha(folder/'native.json') == receipt['native_sha256'] == reg['expected_native_hashes'][name]
            assert sha(folder/'action-values.json') == receipt['action_values_sha256']
            assert receipt['temporary_input_sha256'] == {n:sha(CONTROL/name/n)
                for n in ('conditional-batch.json','forced-profiles.json')}
            for path in folder.iterdir(): bindings[str(path)]=sha(path)
            count+=1
        tables.append(dict(workers=workers,seconds=row['seconds'],
            relative_speed=result['timings'][0]['seconds']/row['seconds']))
    assert {p.name for p in STORE.iterdir()} == expected_folders|{'owner.json'}
    best=min(t['seconds'] for t in tables)
    choice=min(t['workers'] for t in tables if t['seconds'] <= best*1.05)
    assert choice == result['recommended_workers'] == 12 and count == 48
    total=sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file())
    assert total == result['retained_bytes'] and total < reg['maximum_additional_bytes']
    assert result['new_deals'] == 0 and not result['gpu_used'] and not result['full_replay_launched']
    lines=['# Saved root-action replay: CPU throughput qualification', '',
        'All 48 repeated-input jobs reproduced the qualified action values and native',
        'outputs exactly. Twelve workers were fastest in this bounded timing test.', '',
        '| CPU workers | Time for 12 batches | Speed relative to one worker |',
        '| ---: | ---: | ---: |']
    lines += [f"| {t['workers']} | {t['seconds']:.2f} s | {t['relative_speed']:.2f}x |" for t in tables]
    lines += ['', 'This measures saved-data reconstruction, validation, serialization and native',
        'evaluation, including worker startup. It is not a preflop-solver speedup or a',
        'range-accuracy result. Each worker-count case was timed once on the same small',
        'repeated inputs; full-sample throughput may differ.', '',
        'The benchmark used only the two already-qualified 32-deal batches. Repetition',
        'did not add independent scientific samples. All later policies stayed fixed.',
        'The next replay should use 12 workers when other workloads permit, with the',
        'original full sample and per-batch mixture/accounting checks.', '',
        f'The benchmark retains {total/1e6:.2f} MB. Its newly owned temporary input copies',
        'were hash-verified and retired; original evidence remains intact. An independent',
        'file review checked all 48 receipts, exact original-versus-replayed output bytes,',
        'the worker selection rule, and absence of leftover temporary inputs.', '',
        'The benchmark used no GPU and changed no production code. The full 65,536-deal',
        'replay has not launched; its bounded recovery/aggregation runner is the next step.', '']
    report='\n'.join(lines).encode()
    with report_path.open('xb') as stream: stream.write(report)
    review=dict(passed=True,registration_sha256=sha(rp),result_sha256=sha(pp),
        reviewer_sha256=sha(Path(__file__)),findings_sha256=sha(report_path),
        retained_artifacts=bindings,jobs_checked=count,unique_deals=64,new_deals=0,
        native_outputs_exactly_equal=True,compact_values_exactly_equal=True,
        temporary_inputs_absent=True,recommended_workers=choice,timings=tables,
        retained_bytes=total,seconds=time.monotonic()-started,full_replay_launched=False,
        gpu_used=False,accuracy_qualified=False)
    with destination.open('xb') as stream:
        stream.write(json.dumps(review,separators=(',',':'),allow_nan=False).encode())
    print(json.dumps({k:v for k,v in review.items() if k != 'retained_artifacts'}))


if __name__ == '__main__':
    main()
