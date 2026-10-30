"""Publish qualified research variants and compact retained evidence once.

No native child, training, scientific run, production change, or push occurs.
Large retained payloads stay in their original stores and are explicitly pinned.
"""
import os
os.environ.update(PYTHONDONTWRITEBYTECODE='1', CUDA_VISIBLE_DEVICES='-1')
import hashlib
import importlib
import inspect
import json
from pathlib import Path
import subprocess
import sys
import time

STAGE = Path(__file__).resolve().parent
ROOT = Path(r'T:\Dev\GTOpen')
TOOLS = ROOT / 'tools/research'
OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
DEST = OUT / 'native-bounds-evidence-20261003'
NOTE = OUT / 'STACK-CONTEXT-COMPLETE-NATIVE-BOUNDS-20261003.md'
JOURNAL = OUT / 'RIVER-CONTINUATION-RUNNING.md'
HEAD = '6f6b726bfbd9ff72536cd9a4a21e81f9bfc83bad'
MODULES = {
    'preflop_expected_native_execution_v2.py': '1627430507472de471552ffca420b416a5ab0d6670b9ea8e5fb0e11b0da6699f',
    'preflop_expected_board_workers_v2.py': 'd4f941fc7fcabb9197aa3cbea95698cbd78294e05ea21c47af5f00a7ea736b1d',
    'preflop_expected_river_workers_v2.py': 'd34f4134c65adc8603882c4a6c2023b653dbdf27fd6f09794a2504c90f3d1fce',
    'preflop_expected_river_transport_v2.py': '2b1c8fbc5484af9288375ee7665e0e87d9ec0486a7c93c74d670063d21610ddc',
    'preflop_expected_training_pipeline_v2.py': '499a828901ed2a12b26680b1accfea73f4ca6eee527088ac9fb86a266ac3536d',
}
RUST = {
    'crates/solver/examples/research_sampled/research_bounded_output_v1.rs': 'dd61cf57460fbe409c199f48a1149610bebadf8aa97eb3b602c8add171e19da9',
    'crates/solver/examples/hu_fixed_board_tree_bounded_v2.rs': '7eaa77dfaf433baa1ebcc48b067dab672a6a47faab623bd9feac70c916c6e0c5',
    'crates/solver/examples/hu_sampled_allin_history_bridge_bounded_v2.rs': '18b1e6a7bb4137ee1db4f189871f1f8a84852a8c5dff0e01ea4aa43e12a432ee',
    'crates/solver/examples/hu_sampled_action_trace_bounded_v3.rs': '550d3cb460552b9a1628cd44de7a997383e5c9b3bc30a86d72af6f015ac77daa',
    'crates/solver/examples/hu_river_two_stage_stream_bounded_v2.rs': 'e3ff51bb28657327dea8303ce45a825cf0a5412ea68f745aea9dfc3f49b2d5ac',
}
STAGE_FOLDERS = [
    'native-bounded-export-sources-v1', 'native-bounded-export-sources-v2',
    'native-bounded-export-review-v1', 'native-bounded-export-independent-readback-v1',
    'native-direct-output-controls-v2',
    'preflop-expected-board-worker-v2-integration-review-v1',
    'preflop-expected-river-v2-source-review-v1',
    'preflop-expected-river-v2-software-controls-v1',
    'preflop-expected-river-v2-software-controls-v2',
    'native-bounded-pipeline-source-preparation-v1',
    'native-bounded-pipeline-source-preparation-v2',
    'preflop-expected-pipeline-v2-integration-review-v1',
]
SOURCES = [
    'research_bounded_output_control_v1.rs',
    'preflop_expected_bounded_native_publish_v1.py',
    'preflop_expected_bounded_native_publish_v2.py',
    'preflop_expected_bounded_native_build_v1.py',
    'preflop_expected_bounded_native_control_v1.py',
    'preflop_expected_native_execution_check_v2.py',
    'preflop_expected_board_workers_v2_check_v1.py',
    'preflop_expected_river_workers_source_check_v2.py',
    'preflop_expected_river_workers_source_check_v2a.py',
    'preflop_expected_pipeline_bound_prepare_v1.py',
    Path(__file__).name,
]
REQUIRED = {
    STAGE/'native-bounded-export-review-v1/source-review-publication-v2/result.json': '83d27d0da4ab851273b53a53296f89776945054b3ab2333f831d63a73a4cffbf',
    STAGE/'native-bounded-export-independent-readback-v1/result.json': '86360a16d5f47d1db8cc007d985f0ed5ee1297ea8ed22589cfdcd360603e9cfc',
    STAGE/'native-bounded-export-independent-readback-v1/parameter-ownership-result.json': '595e73a194571e2d3ca6b0a2d6c68a793cec893949c3a7a15c9f4aed917a1a4d',
    STAGE/'native-direct-output-controls-v2/result.json': 'a7a120d11dcac660ab6ff49d7af60090f0dabda6ec18ec8795f2f85f78c0f7e6',
    STAGE/'native-direct-output-controls-v2/terminal-artifact-audit-v1.json': '7e326680e810fe92dc9087daa4764f9767ca6052edf3ab50c6ee1d6dc10281cc',
    STAGE/'preflop-expected-board-worker-v2-integration-review-v1/software-control-v1/result.json': '744f94385d50ba3ce47bba7caa0abbb661e85da0908f6d5d1a5230f81cf8e5e4',
    STAGE/'preflop-expected-river-v2-source-review-v1/review.json': '5ab93f35ba7abb591dd163e4636c68dc342bc944f2cc3ceb68fbab202bbb7482',
    STAGE/'preflop-expected-river-v2-software-controls-v2/result.json': '92cee97a409e5ce540b88d29fc41729c7a90c2b6d621969767ac71944aa591de',
    STAGE/'preflop-expected-pipeline-v2-integration-review-v1/result.json': '5db9798c9a95863ec7fcb455eee5d5bd4fceba5271869f35cb21b8f6bb764a89',
}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for part in iter(lambda:f.read(1024*1024), b''):
            h.update(part)
    return h.hexdigest()


def info(path):
    path = Path(path).resolve()
    return dict(path=str(path), sha256=sha(path), bytes=path.stat().st_size)


def write(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2, sort_keys=True, allow_nan=False)
        f.write('\n'); f.flush(); os.fsync(f.fileno())


NOTE_TEXT = """# Complete native output bounds and runner integration

The research runner now accounts for native files written directly to disk,
as well as stdout and stderr. Separate export-only Rust variants check the
serialized aggregate size before opening or writing any output. The board
ceiling is 2 GB; bridge, trace and river ceilings are 64 MB. A 256-byte failure
reserve is included. A requested ceiling can only tighten the fixed ceiling.

This prepares a larger resource profile. It is not evidence of accurate poker
ranges, convergence, a training speedup, or production readiness.

## What was checked

- Two isolated offline builds preserve each original exporter's feature graph.
  Board, bridge and trace use the original default serde_json graph; river uses
  the original continuation-transfer-research / float_roundtrip graph. Original
  sources and executables remain unchanged.
- Thirty-nine actual child invocations passed. Seven retained poker fixtures
  produced identical original bytes at the inclusive and one-byte-extra limits.
  At one byte below the required aggregate, they wrote no payload and retained
  only the fixed error. Direct files use create_new. Large error/panic messages,
  invalid limits, collisions and the river's existing input limits were checked.
- The independent retained audit rehashed the output, source, feature and
  ownership evidence. All 39 child PID/creation identities are distinct; up to
  six native children overlapped. Padded admitted river inputs preserve the
  entire original JSON result after removing only the echoed padding.
- Native execution v2 controls check complete direct-output receipts and refuse
  missing files, partial/nonzero exits, overages, timeout/cancellation and changed
  sources, budgets, hashes, paths or schemas. It is an acceptance/polling bound,
  not a filesystem quota by itself.
- Board worker controls and river call-path controls qualify the v2 wiring.
  Pipeline controls admit one valid result and refuse 118 invalid results;
  three synthetic full-domain draws preserve RNG/scientific state. Native
  verification in those pipeline controls is mocked; they are not a full cycle.
- Source parity reviews preserve target calculations, sampling, action and
  retention RNGs, fitting and scientific selection logic. Prospective contracts
  explicitly tighten board limits to 256..2,000,000,000 bytes and require exact
  v2 envelopes rather than admitting older or malformed results.

The original uncompiled declaration-placement defect and the first river
control's incorrect final verification-count assertion are retained. The latter
changed only a separate control, not implementation or scientific inputs. No
started scientific attempt was retried.

## Evidence and limits

The compact evidence directory records exact original/copy identities and pins
excluded large payloads in their retained stores. Raw native controls remain in
S:\\GTOpen-research\\native-bounded-export-controls-v1 and builds in
S:\\GTOpen-research\\native-bounded-export-build-v1. No old files were compressed,
linked, moved or deleted.

The helper serializes in memory before checking the byte gate, so this does not
bound peak RAM or CPU work. Nonriver input reads retain their previous bounds;
no new input-size ceiling was added. Python-generated policies, events and
other derived outputs still need their own admission reserve. Bridge walk is
outside the seven retained parity fixtures and unused by the qualified runner.
Disk-full, partial-write and abrupt-kill injection were not
tested. Named allocated file sizes do not include all filesystem metadata.
Collision identities were checked live but their before/after records were not
persisted. The general native receipt's observed_argv is the owned Popen vector,
not an OS command-line attestation; four small Python wiring controls separately
checked OS command lines. The helper compiler has no process-creation receipt.
Finite retained-fixture parity is not a guarantee for every future context.
Future configurations must pin the new repository paths and bounded executable
identities; historical receipts keep their original paths and identities.

The next admission needs a fresh inventory under the global 800 GB budget,
explicit six-child and derived-output/metadata reserves, then one genuine full
cycle at 20/40/100/200/400bb with both CUDA fits and checkpoint restoration.
Only afterward can sufficiently sampled independent stability/payoff research
be registered. K2/F4 resource checks cannot establish poker accuracy.

Full preflop accuracy, stack-specific openings, five-bets, additional positions,
multiway/Wizard validation and deployment remain outstanding. Production on
56708 is unchanged. No GitHub push or deployment is part of this publication.
"""

JOURNAL_TEXT = """

## 2026-10-03 Adelaide - complete native export bounds and v2 runner qualification

Previous research turn completed genuine retained-fixture bounds and separate
worker/pipeline controls; the intervening user question was explanatory. This
continuation publishes the exact reviewed variants and compact evidence without
rerunning attempted controls or changing original scientific inputs or gates.

Separate Rust exporters perform aggregate direct/stdout/stderr byte checks before
output I/O, with a 256-byte failure reserve, 2 GB board and 64 MB transport
ceilings. Isolated offline builds preserve the original per-role feature graphs.
Thirty-nine actual child controls passed; seven retained poker fixtures match
original serialized bytes at inclusive/extra limits and refuse one-byte-short
limits before payload. Independent retained audits verify source/features,
output identities and all 39 distinct PID/creation identities (peak six overlap).
All admitted padded river JSON remains identical after removing echoed padding.

Published execution v2 includes complete direct output receipts. Board/river v2
source/wiring checks and pipeline one-valid/118-refusal controls pass with math,
sampler/action/retention state and fit logic unchanged. Exact v2 schema and
256..2GB board contracts are prospective tightening, not unchanged operational
gates. Pipeline native verification is mocked; full native five-depth integration
remains outstanding. Published-path qualification is imports/signatures/pure
limit validation only, not another scientific/native/control attempt.

Saved STACK-CONTEXT-COMPLETE-NATIVE-BOUNDS-20261003.md and exact sources,
registrations, retained receipts, source parity and independent audits in
native-bounds-evidence-20261003. Preserved uncompiled declaration-placement
failure and first river control's final counter error; no implementation change
or scientific retry was needed for the latter. Excluded large artifacts are
pinned in the publication manifest and remain in original stores.

These checks do not bound serialization RAM or constitute a filesystem quota.
No disk-full/short-write/abrupt-kill test; named allocations exclude some metadata;
general observed_argv records the owned Popen vector, not OS attestation. Next:
fresh global 800GB inventory and explicit concurrent/derived reserves, genuine
one-cycle 20/40/100/200/400bb resource profile, then registered sufficient-board
stability/fresh-payoff research. No scientific trial started by this publication,
no production56708 change, push/deployment or broad accuracy/completion claim.
Goal remains active.
"""


def main():
    actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
        text=True, creationflags=subprocess.CREATE_NO_WINDOW).strip()
    if actual != HEAD: raise ValueError('Unexpected publication base')
    if DEST.exists() or NOTE.exists(): raise FileExistsError('Preserve prior publication')
    for name, expected in MODULES.items():
        if sha(STAGE/name) != expected: raise ValueError('Qualified module changed: '+name)
        if (TOOLS/name).exists(): raise FileExistsError(TOOLS/name)
    for name, expected in RUST.items():
        if sha(ROOT/name) != expected: raise ValueError('Qualified Rust changed: '+name)
    for p, expected in REQUIRED.items():
        if sha(p) != expected: raise ValueError('Required evidence changed: '+str(p))
    build = Path(r'S:\GTOpen-research\native-bounded-export-build-v1')
    controls = Path(r'S:\GTOpen-research\native-bounded-export-controls-v1')
    for p in (build/'result.json', controls/'result.json'):
        if json.loads(p.read_bytes()).get('passed') is not True: raise ValueError('Terminal evidence absent')
    pairs=[]; excluded=[]
    def add(source, relative):
        source=Path(source)
        if source.stat().st_size > 1_000_000 or source.suffix in ('.exe','.pdb'):
            excluded.append(info(source)); return
        pairs.append((source, relative, info(source)))
    for name in STAGE_FOLDERS:
        folder=STAGE/name
        for p in sorted(folder.rglob('*')):
            if p.is_file(): add(p, Path('staging')/name/p.relative_to(folder))
    for name in SOURCES: add(STAGE/name, Path('sources')/name)
    for role in ('default-features','river-features'):
        folder=build/role
        for p in sorted(folder.glob('*')):
            if p.is_file(): add(p, Path('build')/role/p.name)
    for p in sorted(build.glob('*')):
        if p.is_file(): add(p, Path('build')/p.name)
    for p in sorted(controls.rglob('*')):
        if p.is_file(): add(p, Path('native-controls')/p.relative_to(controls))
    if len({str(r) for _,r,_ in pairs}) != len(pairs): raise ValueError('Repeated copy target')
    if sum(i['bytes'] for _,_,i in pairs)>20_000_000: raise ValueError('Compact evidence unexpectedly large')
    old_journal=info(JOURNAL)
    DEST.mkdir()
    records=[]
    for src, relative, original in pairs:
        if sha(src)!=original['sha256']: raise ValueError('Source changed during preparation')
        dest=DEST/relative; dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open('xb') as f: f.write(src.read_bytes())
        copied=info(dest)
        if copied['sha256']!=original['sha256']: raise ValueError('Copy changed')
        records.append(dict(original=original,copy=copied))
    runtime=[]
    for name, expected in MODULES.items():
        dest=TOOLS/name
        with dest.open('xb') as f: f.write((STAGE/name).read_bytes())
        if sha(dest)!=expected: raise ValueError('Runtime publication changed')
        runtime.append(info(dest))
    # Import exclusively from the actual published research directory.
    sys.path=[str(TOOLS)]+[p for p in sys.path if p and Path(p).resolve()!=STAGE]
    imported={}
    for name, expected in MODULES.items():
        module=importlib.import_module(Path(name).stem)
        if Path(module.__file__).resolve()!=TOOLS/name or sha(module.__file__)!=expected:
            raise ValueError('Unexpected runtime import')
        imported[Path(name).stem]=module
    execution=imported['preflop_expected_native_execution_v2']
    worker=imported['preflop_expected_board_workers_v2']
    pipeline=imported['preflop_expected_training_pipeline_v2']
    for fn in (execution.run_native,execution.verify_native):
        if not {'max_output_bytes','timeout','direct_outputs'}<=set(inspect.signature(fn).parameters):
            raise ValueError('Explicit native output API missing')
    if pipeline.board_workers_api is not worker: raise ValueError('Wrong board worker wiring')
    limits=dict(max_worker_seconds=180,native_timeout_seconds=120)
    if worker._limits(limits)['max_output_bytes']!=2_000_000_000: raise ValueError('Wrong default board bound')
    refused=[]
    for value in (255,2_000_000_001,True):
        try: worker._limits(dict(limits,max_output_bytes=value))
        except ValueError: refused.append(value)
        else: raise ValueError('Invalid published board bound accepted')
    qualifier=dict(passed=True,scope='Published path imports, API signatures and pure limit validation only',
        imports=runtime,invalid_limits_refused=refused,native_children=0,scientific_runs=0,
        fitting=False,gpu=False,original_control_attempts_replayed=False)
    write(DEST/'published-path-qualification.json',qualifier)
    with NOTE.open('x',encoding='utf-8',newline='\n') as f: f.write(NOTE_TEXT)
    if sha(JOURNAL)!=old_journal['sha256']: raise ValueError('Journal changed concurrently')
    with JOURNAL.open('a',encoding='utf-8',newline='\n') as f: f.write(JOURNAL_TEXT)
    receipt=dict(passed=True,purpose='Exact qualified research-only publication',base_commit=HEAD,
        created_unix=time.time(),required_evidence={str(p):s for p,s in REQUIRED.items()},
        copies=records,excluded_retained_large_artifacts=excluded,runtime=runtime,
        rust=[info(ROOT/name) for name in RUST],qualification=info(DEST/'published-path-qualification.json'),
        findings=info(NOTE),journal_before=old_journal,journal_after=info(JOURNAL),
        control_attempts_replayed=False,scientific_runs=0,production_changed=False,push=False,deploy=False)
    write(DEST/'publication.json',receipt)
    owned=[str((TOOLS/name).relative_to(ROOT)).replace('\\','/') for name in MODULES]
    owned+=list(RUST)+[str(NOTE.relative_to(ROOT)).replace('\\','/'),str(JOURNAL.relative_to(ROOT)).replace('\\','/')]
    owned += [str(p.relative_to(ROOT)).replace('\\','/') for p in sorted(DEST.rglob('*')) if p.is_file()]
    (STAGE/'native-bounds-publication-v1-git-paths.txt').write_text('\n'.join(owned)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,evidence_files=len(records),excluded_large_files=len(excluded),
        copied_bytes=sum(r['copy']['bytes'] for r in records),publication=info(DEST/'publication.json'),owned_paths=len(owned))))


if __name__=='__main__': main()
