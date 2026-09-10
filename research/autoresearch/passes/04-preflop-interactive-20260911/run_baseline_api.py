"""Reuse the previously verified isolated API runner against the new baseline only."""
import datetime as dt
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OLD = HERE.parent / '03-preflop-20260910'
LAB = ROOT / 'target/autoresearch/preflop-interactive-20260911'
spec = importlib.util.spec_from_file_location('prior_api_qualification', OLD / 'proposals/final-api-qualification/qualify_api.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
m.HERE = HERE
m.DEADLINE = dt.datetime.fromisoformat('2026-09-11T02:53:27+00:00')

def main():
    m.live_idle()
    source_protocol = json.loads((OLD/'build-owned-confirm-a-protocol.json').read_text())
    source = Path(source_protocol['pairs'][0]['baseline']['output'])
    initial = m.native(source)
    m.require(initial['header']['iteration'] == 0, 'fresh input required')
    m.require(all(a['sha256'] == m.zero_hash(a['elements']) for a in initial['arrays']), 'nonzero input')
    exe = ROOT/'target/desktop-runtime/release/gto-server.exe'
    exe_sha = m.sha(exe)
    m.require(exe_sha == '7e96cde87bb87ee6dbdd693e010275851eb4d1cc6b4d2bcb550c4ef89173bb6d', 'production baseline changed')
    folder = LAB/'target/interactive-api/baseline-eight-50-a'
    folder.mkdir(parents=True, exist_ok=False)
    case = {'side':'baseline', 'exe':str(exe), 'sha256':exe_sha, 'port':m.free_port(),
            'input':str(source), 'input_sha256':m.sha(source)}
    caches = {n:{'path':str(ROOT/'cache'/n),'sha256':m.sha(ROOT/'cache'/n)}
              for n in ('preflop_eq169.bin','realization_fit.json')}
    protocol = {'frozen_utc':dt.datetime.now(dt.timezone.utc).isoformat(), 'baseline_source':'ff54279',
                'case':case,'caches':caches,'solve':m.SOLVE,'fixed_environment':m.FIXED_ENV,
                'runner_sha256':m.sha(__file__), 'reused_runner_sha256':m.sha(OLD/'proposals/final-api-qualification/qualify_api.py'),
                'measure':'fresh native0 to first published default50 strategy, not convergence',
                'case_timeout_seconds':600,'live_guard_seconds':0.5,'poll_seconds':0.2}
    m.write_new(HERE/'baseline-eight-50-a-protocol.json', protocol)
    result = m.run_case(case, initial, folder, caches)
    compact = {k:result[k] for k in ('completed','error','post_ack_seconds','first_published_checkpoint_seconds','first_strategy_response_seconds','publication_interval_lower_seconds','publication_interval_upper_seconds','final_status','output','output_sha256','case_seconds')}
    compact['raw_result'] = str(folder/'baseline/result.json')
    m.write_new(HERE/'baseline-eight-50-a.json', compact)
    print(json.dumps(compact,indent=2))

if __name__ == '__main__':
    main()
