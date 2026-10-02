"""Read-only retained-publication review; no imports of research or test runners."""
import ast
import hashlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
STAGE = HERE.parent
REPO = Path(r'T:\Dev\GTOpen')
ROOT = REPO/'research/preflop-evolution/blind-defense-20260922/native-bounds-evidence-20261003'
EXPECTED_RECEIPT = 'eadcf1572e967f8be6a2b323830b431d06df7f77d00e04675df7de5bfc416ec0'
FAILURES = []
CHECKS = 0
HASHES = {}


def check(ok, name, **data):
    global CHECKS
    CHECKS += 1
    if not ok:
        FAILURES.append(dict(check=name, **data))


def sha(path):
    p = Path(path)
    h = hashlib.sha256()
    before = p.stat()
    with p.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            h.update(chunk)
    after = p.stat()
    check((before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),
          'stable file during hash', path=str(p))
    HASHES[str(p)] = dict(bytes=after.st_size,sha256=h.hexdigest())
    return h.hexdigest()


def artifact(record):
    path = Path(record['path'])
    check(path.is_file() and not path.is_symlink(), 'ordinary retained file', path=str(path))
    check(sha(path)==record['sha256'], 'SHA256 exact', path=str(path))
    check(path.stat().st_size==record['bytes'], 'length exact', path=str(path))


def load(path):
    return json.loads(Path(path).read_bytes())


def assignment(tree, name):
    values = [n for n in ast.walk(tree) if isinstance(n,ast.Assign)
              and any(isinstance(t,ast.Name) and t.id==name for t in n.targets)]
    assert len(values)==1, name
    return values[0].value


def function(tree, name):
    return next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)


def run():
    receipt_path = ROOT/'publication.json'
    check(sha(receipt_path)==EXPECTED_RECEIPT,'publication receipt exact identity')
    receipt = load(receipt_path)
    check(receipt['passed'] and receipt['scientific_runs']==0 and
          not any(receipt[x] for x in ('push','deploy','production_changed','control_attempts_replayed')),
          'publication scope flags')
    check(receipt['base_commit']=='6f6b726bfbd9ff72536cd9a4a21e81f9bfc83bad','base commit identity')
    check(len(receipt['copies'])==775,'copy count')
    check(len({x['copy']['path'] for x in receipt['copies']})==775,'unique copy destinations')
    original_map = {}
    for pair in receipt['copies']:
        original, copied = pair['original'],pair['copy']
        artifact(original); artifact(copied)
        check(original['sha256']==copied['sha256'] and original['bytes']==copied['bytes'],
              'original and copy exact bytes', source=original['path'],copy=copied['path'])
        check(Path(copied['path']).is_relative_to(ROOT),'copy stays in publication folder')
        original_map[original['path']] = copied
    check(sum(x['copy']['bytes'] for x in receipt['copies'])==9_730_865,'total compact copy bytes')
    check(len(receipt['excluded_retained_large_artifacts'])==15,'excluded retained artifact count')
    for value in receipt['excluded_retained_large_artifacts']:
        artifact(value)
        check(value['path'] not in original_map,'excluded large artifact not copied')
    for path, expected in receipt['required_evidence'].items():
        check(path in original_map and original_map[path]['sha256']==expected,'required evidence copied',path=path)
    suggested = [STAGE/'native-direct-output-controls-v2/result.json',
        Path(r'S:\GTOpen-research\native-bounded-export-build-v1/result.json'),
        Path(r'S:\GTOpen-research\native-bounded-export-controls-v1/result.json'),
        STAGE/'native-bounded-export-independent-readback-v1/result.json',
        STAGE/'native-bounded-export-independent-readback-v1/parameter-ownership-result.json',
        STAGE/'preflop-expected-board-worker-v2-integration-review-v1/independent-source-and-artifact-readback.json',
        STAGE/'preflop-expected-board-worker-v2-integration-review-v1/software-control-v1/result.json',
        STAGE/'preflop-expected-river-v2-source-review-v1/review.json',
        STAGE/'preflop-expected-river-v2-software-controls-v1/failure.json',
        STAGE/'preflop-expected-river-v2-software-controls-v2/result.json',
        STAGE/'preflop-expected-pipeline-v2-integration-review-v1/result.json',
        STAGE/'preflop-expected-pipeline-v2-integration-review-v1/source-parity-result.json']
    check(all(str(p) in original_map for p in suggested),'all twelve recommended records copied')
    names = {'preflop_expected_native_execution_v2.py':'1627430507472de471552ffca420b416a5ab0d6670b9ea8e5fb0e11b0da6699f',
             'preflop_expected_board_workers_v2.py':'d4f941fc7fcabb9197aa3cbea95698cbd78294e05ea21c47af5f00a7ea736b1d',
             'preflop_expected_river_workers_v2.py':'d34f4134c65adc8603882c4a6c2023b653dbdf27fd6f09794a2504c90f3d1fce',
             'preflop_expected_river_transport_v2.py':'2b1c8fbc5484af9288375ee7665e0e87d9ec0486a7c93c74d670063d21610ddc',
             'preflop_expected_training_pipeline_v2.py':'499a828901ed2a12b26680b1accfea73f4ca6eee527088ac9fb86a266ac3536d'}
    check({Path(v['path']).name for v in receipt['runtime']}==set(names),'five exact runtime modules')
    for value in receipt['runtime']:
        artifact(value)
        name=Path(value['path']).name
        check(value['sha256']==names[name]==sha(STAGE/name),'published runtime matches qualified staging',name=name)
        check(Path(value['path'])==REPO/'tools/research'/name,'runtime location',name=name)
    source_review = load(STAGE/'native-bounded-export-review-v1/source-review-publication-v2/result.json')
    rust_pins={source_review['helper_unchanged_from_reviewed_v1']['path']:source_review['helper_unchanged_from_reviewed_v1']['sha256']}
    rust_pins.update({v['new']:v['new_sha256'] for v in source_review['corrected_sources']})
    check({v['path']:v['sha256'] for v in receipt['rust']}==rust_pins,'five exact qualified Rust files')
    for value in receipt['rust']:
        artifact(value)
    for value in source_review['corrected_sources']:
        check(sha(value['original'])==value['original_sha256'],'original Rust source preserved',path=value['original'])
    pipeline_proof=load(STAGE/'preflop-expected-pipeline-v2-integration-review-v1/source-parity-result.json')
    for name in names:
        old=name.replace('_v2.py','_v1.py')
        original_repo=REPO/'tools/research'/old
        check(sha(original_repo)==sha(STAGE/old),'authoritative v1 source still equal',name=old)
    for path,expected in pipeline_proof['source_identities'].items():
        check(sha(path)==expected,'pipeline qualification source unchanged',path=path)
    for field in ('findings','journal_after','qualification'):
        artifact(receipt[field])
    journal=Path(receipt['journal_after']['path']).read_bytes()
    before=receipt['journal_before']
    check(hashlib.sha256(journal[:before['bytes']]).hexdigest()==before['sha256'],
          'journal changes append only and preserve exact old prefix')
    qualified=load(receipt['qualification']['path'])
    check(qualified['passed'] and qualified['imports']==receipt['runtime'] and
          qualified['native_children']==qualified['scientific_runs']==0 and
          qualified['fitting'] is False and qualified['gpu'] is False and
          qualified['original_control_attempts_replayed'] is False,'published path qualification restricted scope')
    trees={name:ast.parse((REPO/'tools/research'/name).read_text()) for name in names}
    forbidden={'preflop_expected_native_execution_v1','preflop_expected_board_workers_v1',
               'preflop_expected_river_workers_v1','preflop_expected_river_transport_v1'}
    for name,tree in trees.items():
        imports=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):imports.extend(x.name for x in node.names)
            if isinstance(node,ast.ImportFrom):imports.append(node.module)
        check(not (set(imports)&forbidden),'runtime imports v2 execution/worker adapters',module=name)
        for imported in set(imports)&{p[:-3] for p in names}:
            check((REPO/'tools/research'/(imported+'.py')).is_file(),'v2 peer import resolves in publication',module=name,imported=imported)
    pipe=trees['preflop_expected_training_pipeline_v2.py']
    collect=function(pipe,'collect')
    check(ast.unparse(assignment(collect,'query_outputs'))=='[dict(path=str(qp), argument_index=5)]',
          'coordinator full argv index five direct declaration')
    check(ast.unparse(assignment(collect,'query_arguments'))==
          "['queries', str(context_path), str(bp), '-', str(qp), '--output-byte-limit=' + str(river_workers_api.MAX_NATIVE_OUTPUT_BYTES)]",
          'coordinator resource argument is present')
    calls={}
    for node in ast.walk(collect):
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in ('run_native','verify_native'):
            calls[node.func.id]=node
    for field in ('timeout','max_output_bytes','direct_outputs','expected_identities'):
        left=next(k.value for k in calls['run_native'].keywords if k.arg==field)
        right=next(k.value for k in calls['verify_native'].keywords if k.arg==field)
        check(ast.dump(left)==ast.dump(right),'query run/verify bound symmetry',field=field)
    check(ast.literal_eval(assignment(trees['preflop_expected_river_workers_v2.py'],'MAX_NATIVE_OUTPUT_BYTES'))==64_000_000,
          'river native aggregate cap 64MB')
    fields=ast.literal_eval(assignment(pipe,'BOARD_RESULT_FIELDS'))
    produced=assignment(function(trees['preflop_expected_board_workers_v2.py'],'complete'),'result')
    check(len(fields)==33 and fields=={k.arg for k in produced.keywords},'exact pipeline/worker schema agreement')
    signature=function(trees['preflop_expected_native_execution_v2.py'],'verify_native').args
    required=[n.arg for n,d in zip(signature.kwonlyargs,signature.kw_defaults) if d is None]
    check(required==['executable','arguments','expected_identities','timeout','max_output_bytes'],'explicit verifier bound contract')
    findings=Path(receipt['findings']['path']).read_text()
    appended=journal[before['bytes']:].decode('utf-8')
    qualified_phrases=['not evidence of accurate poker','Native\n  verification in those pipeline controls is mocked',
                       'not a filesystem quota','no new input-size ceiling','not\ntested',
                       'Future configurations must pin','before/after records were not\npersisted']
    check(all(text in findings for text in qualified_phrases),'findings retain material scope limitations')
    check('full native five-depth integration\nremains outstanding' in appended and
          'imports/signatures/pure\nlimit validation only' in appended,'journal has correct integration/publication scope')
    actual_files={str(p) for p in ROOT.rglob('*') if p.is_file()}
    covered={v['copy']['path'] for v in receipt['copies']}|{str(receipt_path),receipt['qualification']['path']}
    extras=sorted(actual_files-covered)
    # Additive review/errata may legitimately arrive while this read-only review
    # is in progress. They must never replace receipt-pinned originals.
    check(sha(receipt_path)==EXPECTED_RECEIPT,'publication receipt remains immutable after readback')
    return dict(copy_count=775,copy_bytes=sum(v['copy']['bytes'] for v in receipt['copies']),
                retained_excluded_artifacts=15,runtime_sources=receipt['runtime'],rust_sources=receipt['rust'],
                journal_original_prefix_exact=True,published_path_imports_not_reexecuted=True,
                static_runtime_wiring_verified=True,required_evidence_count=len(receipt['required_evidence']),
                all_twelve_recommended_evidence_files_present=True,unlisted_additive_files=extras,
                findings_identity=receipt['findings'],journal_identity=receipt['journal_after'],
                journal_before_identity=before,qualification_identity=receipt['qualification'])


if __name__=='__main__':
    details=run()
    issue=dict(severity='prose precision',location='findings paragraph on observed_argv',
               original_claim='four small Python wiring controls separately checked OS command lines',
               correction='The successful river suite independently checks OS cmdline for its two bridge/trace children. The two history/selected transport children check arguments/payload without OS cmdline. The execution suite has a separate OS-attestation control.',
               evidence_source=str(STAGE/'preflop_expected_river_workers_source_check_v2a.py'),
               evidence_source_sha256=sha(STAGE/'preflop_expected_river_workers_source_check_v2a.py'))
    report=dict(format=1,review='native-bounds-publication-independent-review-v1',
                publication_receipt=dict(path=str(ROOT/'publication.json'),sha256=EXPECTED_RECEIPT),
                exact_copy_and_source_review_passed=not FAILURES,runtime_wiring_review_passed=not FAILURES,
                prose_review_passed=False,passed=False,checks=CHECKS,failures=FAILURES,
                prose_issues=[issue],files_hashed=len(HASHES),
                audit_source_sha256=sha(__file__),native_runs=0,control_reruns=0,model_fits=0,
                scientific_runs=0,imports_reexecuted=False,repo_writes=False,
                terminal_unix=time.time(),**details)
    output=HERE/'result.json'
    with output.open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(report,stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(result=str(output),sha256=sha(output),passed=report['passed'],
                         technical_passed=report['exact_copy_and_source_review_passed'],
                         checks=report['checks'],files_hashed=report['files_hashed'],failures=FAILURES,
                         prose_issues=report['prose_issues'])))
