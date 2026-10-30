"""Read-only source/history review before any child-value-cache prototype."""
import hashlib, json, re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
h.custody()
h.ar.refuse_active(h.ar.live_status())
assert not (ROOT / 'gpu-run.lock').exists() and not (ROOT / 'epoch-sequence.lock').exists()

UI = ROOT / 'runs/D302-live-UI-check'
UI.mkdir(exist_ok=False)
snapshots = [Path(r'X:\Dev\GTOpen\.playwright-cli\page-2026-10-29T19-53-57-875Z.yml'),
             Path(r'X:\Dev\GTOpen\.playwright-cli\page-2026-10-29T19-54-40-695Z.yml')]
images = [ROOT / 'output/playwright' / ('D302-' + name + '.png') for name in ['tracker-before', 'preflop-menu']]
tracker, menu = [path.read_text(encoding='utf-8') for path in snapshots]
assert 'New RAM measurement epoch' in tracker and 'Prior accepted gain' in tracker
assert '10.46 s' in tracker and 'E122' in tracker
assert 'PREFLOP GAME' in menu
assert not any(text in menu for text in ['Legacy Calibration', 'Positional (legacy)', 'Raw Equity', 'Postflop model'])
js = Path(r'X:\Dev\GTOpen\web\js\preflop_lab.js').read_text(encoding='utf-8')
assert "const DEFAULT_REALIZATION = 'balanced';" in js
console = Path(r'X:\Dev\GTOpen\.playwright-cli\console-2026-10-29T19-54-39-860Z.log')
assert '400 (Bad Request)' in console.read_text() and '/api/preflop/session' in console.read_text()
h.save(UI / 'report.json', {'id': 'D302', 'at': h.now(), 'status': 'pass_scoped_live_menu_and_tracker_render',
    'source_source_PTX_live_custody': True, 'actual_browser': 'Playwright CLI isolated gtopen-research-ui; owned browser explicitly closed',
    'tracker': 'Rendered current baseline10.46s/5measurements/bestE080GPUcompressed16, earlier14.74% explicitly historical and not pooled, E122closed-0.447667%, table/links/chart present. Tracker console0errors0warnings.',
    'freshness': 'Before screenshot honestly reported stale after6minutes without a milestone publication; no stale threshold/percentage/baseline changed. New source-stage milestones will update status.',
    'preflop': 'Live initial rendered UI lacks all legacy/postflopmodel selector options; source defaults balanced. No game build/load/save/solve attempted; current API has no live preflop session.',
    'expected_console_response': 'One400 /api/preflop/session while no game exists; no exception or UI failure inferred from expected absent-session response.',
    'bounds': 'Checks initial rendered configuration only; does not newly prove old-save migration, numerical continuation, or improved model quality.',
    'inspected_files_sha256': {str(p): h.sha(p) for p in snapshots + images + [console, Path(r'X:\Dev\GTOpen\web\js\preflop_lab.js')]},
    'new_compiler_GPU_kernel_solver_or_speed_samples': 0,
    'closed_leads_preserved': 'D100/D187 forbid cache-preference/carveout/kernel-scope retries; E005/E014 arity split, E063rank segments, E024genericcache and E117earlierchildloads remain closed.',
    'terminal_audit_recheck': 'All E122 create-only audit assertions before save passed; re-invocation stopped solely on existing terminal-audit.json. Original receipt retained; subsequent explicit read-only custody/live/locks/HEAD recheck passed, no experiment/native repeat.'})

H = ROOT / 'runs/D303-child-cache-scout'
H.mkdir(exist_ok=False)
def helper(text):
    match = re.search(r'__device__[^\n]*\bvoid up_action_impl\(', text)
    if not match:
        return ''
    end = text.find('extern "C" __global__ void up_action(', match.start())
    return text[match.start():end if end >= 0 else len(text)]

seen, hits, inventory = {}, [], []
for folder in [Path(r'S:\GTOpen-research\postflop-gpu-20261016\runs'), ROOT / 'runs']:
    paths = subprocess.check_output(['rg', '--files', str(folder), '-g', '*.cu'], text=True).splitlines()
    inventory.append({'root': str(folder), 'CUDA_files': len(paths)})
    for name in paths:
        blob = Path(name).read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
        if digest in seen:
            continue
        seen[digest] = name
        body = helper(blob.decode('utf-8'))
        # The proposed narrow form retains original regret caching and removes
        # only child-value temporary storage, with a direct late CFV reread.
        if body and 'rc[' in body and 'vc[' not in body and re.search(r'float val\s*=\s*cfv\[', body):
            hits.append({'path': name, 'sha256': digest, 'body': body})
revisions = subprocess.check_output(['git', 'log', '--all', '--format=%H', '--', 'crates/solver/src/gpu/kernels.cu'], cwd=h.REPO, text=True).splitlines()
local = []
for revision in revisions:
    text = subprocess.check_output(['git', 'show', revision + ':crates/solver/src/gpu/kernels.cu'], cwd=h.REPO).decode('utf-8')
    body = helper(text)
    if body and 'rc[' in body and 'vc[' not in body and re.search(r'float val\s*=\s*cfv\[', body):
        local.append({'revision': revision, 'body': body})
source = (h.REPO / 'crates/solver/src/gpu/kernels.cu').read_bytes()
body = helper(source.decode())
assert body.count('float rc[8], vc[8];') == 1
assert body.count('if (small) vc[a] = v;') == 1
assert body.count('float val = small ? vc[a] : cfv[') == 1
assert 'regrets_p[idx] = r * d + (val - out);' in body
h.save(H / 'report.json', {'id': 'D303', 'at': h.now(), 'status': 'history_review_before_prototype',
    'inventories': inventory, 'unique_CUDA_hashes': len(seen), 'local_all_ref_revisions': len(revisions),
    'retained_matches': hits, 'local_matches': local,
    'candidate_concept': 'Keep all original rc regret caching, sums/sigma/out/strategy/discount/regret equations. Remove only vc array and its copy; original late regret phase reloads same child CFV word. All template arities, ABI, host, launch/arrays/quality unchanged. No volatile, asm, flags, new helper or closed source composition.',
    'counterevidence': 'E024 removes BOTH caches ONLY in generic NA0; failedspeed. E117 loads child CFV EARLIER into vc during regret-sum pass; resource/maxthreadfailed. E123 would instead remove child cache across original helper while retaining regret cache and original load/equation order otherwise. Not a transfer/tune of either closed fixed hunk.',
    'critical_uncertainty': 'Compiler may CSE late reloads into original registers, producing no new mechanism; extra memory traffic can erase any resource benefit. Require actual compute120 register count strictly below62 and changed native body before application kernels, in addition to original resource/ABI gates. No advantage inferred from source cache words.',
    'alias_argument': 'No cfv writes in helper between original value load and regret-phase reload; only regrets/strategy stores, with original device allocations disjoint from cfv. Final parent CFV store stays after all regret updates. For na>8 original already reloads. Full actual raw GPU inputs/outputs/caller alias and broader controls mandatory; source argument not universal/compiler/NaN proof.',
    'accepted_CUDA_sha256': hashlib.sha256(source).hexdigest(), 'new_compiler_GPU_applicationkernel_solver_or_speed_samples': 0,
    'limits': 'Bounded recognized helper/literal/local-all-ref search, not exhaustive semantic or remote novelty. Review any hits before staging.'})
print(json.dumps({'unique_CUDA': len(seen), 'retained_matches': len(hits), 'local_matches': len(local), 'report_sha256': h.sha(H / 'report.json')}), flush=True)
h.custody()
