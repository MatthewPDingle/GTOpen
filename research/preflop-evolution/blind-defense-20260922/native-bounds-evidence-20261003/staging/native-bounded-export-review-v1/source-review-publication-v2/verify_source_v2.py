"""Independent read-only verification of the corrected exclusive publication."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import time

OUT = Path(__file__).resolve().parent
PLAN = OUT.parent
STAGE = PLAN.parent
V1 = PLAN/'source-review-publication-v1'
PUB = STAGE/'native-bounded-export-sources-v2/publication.json'
HELPER = '#[path="research_sampled/research_bounded_output_v1.rs"] mod research_bounded_output_v1;\n'
WRAPPER = '\nfn main(){research_bounded_output_v1::entry(run_bounded);}\n'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def save(name,value):
    with (OUT/name).open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,sort_keys=True,indent=2,allow_nan=False);stream.write('\n')


def replace_once(source,old,new):
    assert source.count(old)==1,old
    return source.replace(old,new)


def main():
    began=time.monotonic()
    assert not (OUT/'result.json').exists()
    assert sha(PLAN/'plan.json')=='400e26658f2780e82f034959166e89c073edbe0092c9a78aa08ba0a7150d099c'
    assert sha(V1/'source-review.json')=='793df555026888cc5e72767a945f8d05e7011a235b3e00612e6e36942e387c56'
    assert sha(V1/'boundary-plan-v2.json')=='99b857ed320bc187cf35e24603186bdba66aee89210afb7574360c1b36cda1a7'
    review1=json.loads((V1/'source-review.json').read_bytes())
    assert sha(V1/'review_source_v1.py')==review1['review_source_sha256']
    # Read, rather than execute, the already-pinned exact inverse rules.
    code=ast.parse((V1/'review_source_v1.py').read_text())
    assignment=next(node for node in ast.walk(code) if isinstance(node,ast.Assign)
        and any(isinstance(target,ast.Name) and target.id=='inverses' for target in node.targets))
    inverses=ast.literal_eval(assignment.value)
    publication=json.loads(PUB.read_bytes())
    oldpub=json.loads((V1/'publication.json.snapshot').read_bytes())
    assert publication['previous_publication']['sha256']==sha(V1/'publication.json.snapshot')
    assert sha(publication['previous_publication']['path'])==publication['previous_publication']['sha256']
    assert publication['failure_reserve']==256 and publication['board_ceiling']==2_000_000_000
    assert publication['transport_ceiling']==64_000_000
    assert publication['helper']==oldpub['helper']
    sources=[];complete_diffs=[];correction_diffs=[]
    for row in publication['sources']:
        oldrow=next(v for v in oldpub['sources'] if v['new']==row['new'])
        name=Path(row['new']).name
        v1=(V1/('published-'+name+'.snapshot')).read_text(encoding='utf-8')
        assert row['previous_uncompiled_sha256']==oldrow['new_sha256']==hashlib.sha256(v1.encode()).hexdigest()
        current=Path(row['new']).read_bytes()
        assert hashlib.sha256(current).hexdigest()==row['new_sha256']
        assert sha(row['original'])==row['original_sha256']==oldrow['original_sha256']
        base=replace_once(v1,HELPER,'')
        lines=base.splitlines(keepends=True);index=0
        while index<len(lines) and (lines[index].startswith('//!') or lines[index].startswith('#!')):index+=1
        expected=''.join(lines[:index])+HELPER+''.join(lines[index:])
        text=current.decode()
        assert text==expected,'Corrected source contains more than the exact module-declaration move'
        assert text.splitlines()[index]==HELPER.rstrip('\n')
        assert not any(line.startswith('//!') or line.startswith('#!') for line in text.splitlines()[index+1:])
        restored=replace_once(text,HELPER,'');restored=replace_once(restored,WRAPPER,'')
        for before,after in inverses[name]:restored=replace_once(restored,before,after)
        restored_sha=hashlib.sha256(restored.encode()).hexdigest()
        assert restored_sha==row['original_sha256'],'Corrected exact inverse differs from original'
        destination=OUT/('corrected-'+name+'.snapshot')
        with destination.open('xb') as stream:stream.write(current)
        assert sha(destination)==row['new_sha256']
        original=Path(row['original']).read_bytes()
        with (OUT/('original-'+Path(row['original']).name+'.snapshot')).open('xb') as stream:stream.write(original)
        correction_diffs.append(''.join(difflib.unified_diff(v1.splitlines(keepends=True),
            text.splitlines(keepends=True),fromfile='publication-v1/'+name,tofile='publication-v2/'+name)))
        complete_diffs.append(''.join(difflib.unified_diff(original.decode().splitlines(keepends=True),
            text.splitlines(keepends=True),fromfile=row['original'],tofile=row['new'])))
        sources.append(dict(**row,only_header_declaration_move_from_v1=True,
            original_docs_and_attributes_precede_items=True,reconstructed_original_sha256=restored_sha,
            source_inverse_all_remaining_bytes_exact=True,snapshot=str(destination)))
    helper=Path(publication['helper']['path']);assert sha(helper)==publication['helper']['sha256']
    assert helper.read_bytes()==(V1/'published-helper.rs.snapshot').read_bytes()
    with (OUT/'helper.rs.snapshot').open('xb') as stream:stream.write(helper.read_bytes())
    with (OUT/'publication.json.snapshot').open('xb') as stream:stream.write(PUB.read_bytes())
    for name,content in [('correction-only-diffs.txt',correction_diffs),('complete-original-diffs.txt',complete_diffs)]:
        with (OUT/name).open('x',encoding='utf-8',newline='') as stream:stream.write('\n'.join(content))
    original_plan=json.loads((PLAN/'plan.json').read_bytes())
    pins=original_plan['source_pins']
    assert len(pins)==848
    for path,identity in pins.items():assert sha(path)==identity,path
    for row in sources:
        assert sha(row['new'])==row['new_sha256']
        assert sha(row['original'])==row['original_sha256']
    assert sha(helper)==publication['helper']['sha256']
    save('result.json',dict(source_review_passed=True,compilation_can_proceed=True,
        no_remaining_source_blocker_identified=True,actual_compilation_not_performed=True,
        native_executed=False,scientific_accuracy_qualified=False,
        publication=dict(path=str(PUB),sha256=sha(PUB)),previous_source_defect_preserved=True,
        prior_source_review=dict(path=str(V1/'source-review.json'),sha256=sha(V1/'source-review.json')),
        originals_and_registered_binaries_unchanged=True,original_source_evidence_pins_rechecked=848,
        corrected_sources=sources,helper_unchanged_from_reviewed_v1=publication['helper'],
        complete_calculation_source_inverse_proofs=4,
        matching_feature_graphs={role:value['observed_solver_features'] for role,value in original_plan['compilation_evidence'].items()},
        boundary_plan=dict(path=str(V1/'boundary-plan-v2.json'),sha256=sha(V1/'boundary-plan-v2.json')),
        build_conditions=['New offline isolated target directories and separately pinned build argv/features/logs/binaries.',
            'Board/bridge/trace solver features=[]; river continuation-transfer-research graph with serde_json/float_roundtrip.',
            'Empty Rust flags and normal unwind behavior for the source-reviewed fixed catch_unwind panic diagnostics.',
            'Original source and binary identities checked before and after isolated builds.',
            'No native launch, poker/science, production wiring or fit authorized by this source-only result.'],
        qualification_limits=review1['limitations'],review_source_sha256=sha(__file__),seconds=time.monotonic()-began))
    print(json.dumps(dict(compilation_can_proceed=True,source_inverse_proofs=4,
        original_pins_rechecked=848,compiled=False,native_executed=False,result=str(OUT/'result.json'),
        result_sha256=sha(OUT/'result.json')),sort_keys=True))


if __name__=='__main__':main()
