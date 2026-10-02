"""Source-only proof against preserved publication v1; no native/build calls."""
import difflib
import hashlib
import json
from pathlib import Path
import re

OUT = Path(__file__).resolve().parent
PLAN = OUT.parent
ROOT = Path(r'T:\Dev\GTOpen')
HELPER_LINE = '#[path="research_sampled/research_bounded_output_v1.rs"] mod research_bounded_output_v1;\n'
WRAPPER = '\nfn main(){research_bounded_output_v1::entry(run_bounded);}\n'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(name,value):
    with (OUT/name).open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,sort_keys=True,indent=2,allow_nan=False)
        stream.write('\n')


def replace_once(source,old,new):
    assert source.count(old)==1,old
    return source.replace(old,new)


def main():
    assert not (OUT/'source-review.json').exists()
    publication=json.loads((OUT/'publication.json.snapshot').read_bytes())
    pinread=json.loads((OUT/'initial-pin-readback.json').read_bytes())
    assert sha(OUT/'publication.json.snapshot')==pinread['publication_sha256']
    inverses={
        'hu_fixed_board_tree_bounded_v2.rs':[
            ('fn run_bounded()->Result<(),Box<dyn std::error::Error>> {','fn main()->Result<(),Box<dyn std::error::Error>> {'),
            ('    let (args,output_limit)=research_bounded_output_v1::arguments(2_000_000_000)?;assert_eq!(args.len(),2);','    let args:Vec<_>=std::env::args().skip(1).collect();assert_eq!(args.len(),2);'),
            ('''    let mut bytes=serde_json::to_vec(&json!({"format":1,"board":board,"hands":hands,"ranks":ranks,"branches":branches}))?;
    bytes.push(b'\\n');research_bounded_output_v1::emit(None,&bytes,&[],output_limit)?;Ok(())''','''    println!("{}",json!({"format":1,"board":board,"hands":hands,"ranks":ranks,"branches":branches}));Ok(())''')],
        'hu_sampled_allin_history_bridge_bounded_v2.rs':[
            ('fn run_bounded()->Result<(),Box<dyn std::error::Error>>{','fn main()->Result<(),Box<dyn std::error::Error>>{'),
            (' let (a,output_limit)=research_bounded_output_v1::arguments(64_000_000)?;assert_eq!(a.len(),5);assert!(!std::path::Path::new(&a[4]).exists());',' let a:Vec<_>=std::env::args().skip(1).collect();assert_eq!(a.len(),5);assert!(!std::path::Path::new(&a[4]).exists());'),
            (''' let bytes=serde_json::to_vec(&result)?;let mut status=serde_json::to_vec(&json!({"mode":a[0],"raw_queries":q.raw_len(),"observations":q.observations.len()}))?;
 status.push(b'\\n');research_bounded_output_v1::emit(Some((std::path::Path::new(&a[4]),&bytes)),&status,&[],output_limit)?;Ok(())''',''' std::fs::write(&a[4],serde_json::to_vec(&result)?)?;println!("{}",json!({"mode":a[0],"raw_queries":q.raw_len(),"observations":q.observations.len()}));Ok(())''')],
        'hu_sampled_action_trace_bounded_v3.rs':[
            ('fn run_bounded() -> Result<(), Box<dyn std::error::Error>> {','fn main() -> Result<(), Box<dyn std::error::Error>> {'),
            ('    let (args, output_limit) = research_bounded_output_v1::arguments(64_000_000)?;','    let args: Vec<_> = std::env::args().skip(1).collect();'),
            ('''    let bytes = serde_json::to_vec(&result)?;
    research_bounded_output_v1::emit(Some((std::path::Path::new(&args[3]), &bytes)), &[], &[], output_limit)?;''','''    std::fs::write(&args[3], serde_json::to_vec(&result)?)?;''')],
        'hu_river_two_stage_stream_bounded_v2.rs':[
            ('fn run_bounded()->Result<(),Box<dyn std::error::Error>> {','fn main()->Result<(),Box<dyn std::error::Error>> {'),
            ('    let (args,output_limit)=research_bounded_output_v1::arguments(MAX_BYTES)?;','    let args:Vec<_>=std::env::args().skip(1).collect();'),
            ('''    bytes.push(b'\\n');let mut status=serde_json::to_vec(&json!({"passed":true,"mode":result["mode"],"nodes":result["total_nodes"],
        "observations":result["queries"]["observations"].as_array().unwrap().len(),"bytes":bytes.len()}))?;
    status.push(b'\\n');research_bounded_output_v1::emit(None,&bytes,&status,output_limit)?;Ok(())''','''    bytes.push(b'\\n');if bytes.len()>MAX_BYTES {return Err("Output byte budget exceeded".into());}
    let mut output=std::io::stdout().lock();output.write_all(&bytes)?;output.flush()?;
    eprintln!("{}",json!({"passed":true,"mode":result["mode"],"nodes":result["total_nodes"],
        "observations":result["queries"]["observations"].as_array().unwrap().len(),"bytes":bytes.len()}));Ok(())''')]
    }
    math_proof=[]
    compile_defects=[]
    for row in publication['sources']:
        name=Path(row['new']).name
        source=(OUT/('published-'+name+'.snapshot')).read_text(encoding='utf-8')
        assert source.startswith(HELPER_LINE+'//!')
        assert sha(OUT/('published-'+name+'.snapshot'))==row['new_sha256']
        assert sha(row['original'])==row['original_sha256']
        restored=replace_once(source,HELPER_LINE,'')
        restored=replace_once(restored,WRAPPER,'')
        for old,new in inverses[name]:restored=replace_once(restored,old,new)
        identity=hashlib.sha256(restored.encode()).hexdigest()
        assert identity==row['original_sha256'],''.join(difflib.unified_diff(
            (OUT/('original-'+Path(row['original']).name+'.snapshot')).read_text().splitlines(),restored.splitlines()))
        math_proof.append(dict(new=row['new'],new_sha256=row['new_sha256'],
            reconstructed_original_sha256=identity,allowed_inverse_replacements=len(inverses[name])+2,
            all_remaining_source_bytes_exact=True,compiled=False,native_executed=False))
        compile_defects.append(dict(path=row['new'],line=1,
            message='The new helper mod item precedes original //! inner documentation; Rust requires inner docs before items. River also leaves #![allow(dead_code)] after that item.',
            correction='Move the helper declaration after all original leading inner documentation/crate attributes in a new publication; preserve this failed source publication.'))
    sourceplan=json.loads((PLAN/'plan.json').read_bytes())
    transitives={p:h for p,h in sourceplan['source_pins'].items()
        if p.endswith('.rs') and ('research_sampled' in p or '\\crates\\solver\\src\\' in p)}
    print_pattern=re.compile(r'\b(?:print|println|eprint|eprintln)!|(?:stdout|stderr)\s*\(|process::(?:exit|abort)|fs::write|write_all\s*\(')
    output_sites={}
    for path,identity in transitives.items():
        assert sha(path)==identity,path
        matches=[dict(line=i,text=line) for i,line in enumerate(Path(path).read_text().splitlines(),1)
            if print_pattern.search(line)]
        assert not matches,(path,matches)
        output_sites[path]=matches
    helper=(OUT/'published-helper.rs.snapshot').read_text()
    assert sha(OUT/'published-helper.rs.snapshot')==publication['helper']['sha256']
    assert 'direct_len.checked_add(stdout.len())' in helper
    assert '.and_then(|bytes| bytes.checked_add(stderr.len()))' in helper
    assert '.and_then(|bytes| bytes.checked_add(FAILURE_RESERVE))' in helper
    assert helper.index('if complete > limit')<helper.index('create_new(true).open(path)')<helper.index('output.write_all(bytes)')
    assert helper.index('if complete > limit')<helper.index('output.write_all(stdout)')
    assert 'std::panic::set_hook(Box::new(|_| {}));' in helper
    assert helper.count('write_all(ERROR)')==helper.count('write_all(PANIC)')==1
    error=b'Research exporter failed\n';panic=b'Research exporter panicked\n'
    assert len(error)==25 and len(panic)==27 and max(len(error),len(panic))<=256
    controls=json.loads((PLAN/'representative-controls.json').read_bytes())['primary']
    boundary=[]
    for r in controls:
        direct=r['expected_payload']['bytes'] if r['group'] in ('bridge-queries','bridge-verify','trace') else 0
        success=direct+r['expected_stdout']['bytes']+r['expected_stderr']['bytes']
        threshold=success+256
        boundary.append(dict(group=r['group'],original_payload=r['expected_payload'],
            direct_bytes=direct,stdout_bytes=r['expected_stdout']['bytes'],stderr_bytes=r['expected_stderr']['bytes'],
            success_data_and_stdio_bytes=success,failure_reserve=256,
            accept_limit=threshold,reject_limit=threshold-1,extra_accept_limit=threshold+1,
            reject_expected_stdout=b''.decode(),reject_expected_stderr=error.decode(),reject_expected_returncode=1,
            reject_expected_direct_output_absent=direct>0,
            original_inputs=r['request_inputs'],prospective_not_run=True))
    save('boundary-plan-v2.json',dict(method='aggregate-payload-stdio-plus-reserve-boundaries-v2',
        prior_plan_preserved=True,valid_argument_range='256 <= requested_limit <= fixed role ceiling',
        board_ceiling=2_000_000_000,transport_ceiling=64_000_000,controls=boundary,
        invalid_argument_errors='Invalid/zero/below-256/above-ceiling/malformed overrides reject with one fixed error. Their requested values are outside the valid bound contract.',
        collision_controls='New owned sentinel/file/directory only. Existing-path assertion may produce the 27-byte panic message; a race caught by create_new returns the 25-byte error. Preserve sentinel hash, size and physical identity.',
        input_cap_scope='Only river has the retained 16 MiB context / 64 KiB stdin bounds. Board/bridge/trace retain their unbounded file reads; no input cap qualification is claimed.'))
    save('source-review.json',dict(format=1,publication=pinread,
        source_only_review_complete=True,native_executed=False,compiled=False,
        calculation_invariance_proof=math_proof,
        source_compilability_blocked=True,concrete_defects=compile_defects,
        helper=dict(pinned_sha256=publication['helper']['sha256'],
            complete_size_checked_before_direct_and_stdio_writes=True,
            overflow_checked_adds=True,create_new_direct_output=True,
            fixed_error_bytes=len(error),fixed_panic_bytes=len(panic),failure_reserve=256,
            preserves_capacity_for_partial_io_failure_diagnostic=True,
            valid_limit_range_only=True,requires_panic_unwind_build_for_expected_caught_panic_exit=True),
        reachable_calculation_module_output_sites=output_sites,
        boundary_plan_sha256=sha(OUT/'boundary-plan-v2.json'),
        review_source_sha256=sha(__file__),
        limitations=['Actual compilation and byte parity have not run.',
            'Complete result and serialized buffers are constructed before the byte gate; memory and input bounds are separate.',
            'An I/O failure after size admission may retain a bounded partial file or stdio payload; a byte-budget rejection must occur before any payload write.',
            'New success aggregate limit intentionally includes stdio and 256 reserve, tightening the original river payload-only cap.',
            'Only bridge queries/verify are covered by retained primary fixtures; bridge walk is not yet byte-parity qualified.',
            'Output-site scan covers the referenced research calculation modules and directly used solver lib/tree/evaluator/cards, not all unused modules in the solver crate.']))
    print(json.dumps(dict(source_review_complete=True,source_compilability_blocked=True,
        exact_calculation_invariance_reconstructions=4,transitive_modules=len(transitives),
        boundary_thresholds=[dict(group=r['group'],limit=r['accept_limit']) for r in boundary],
        findings_sha256=sha(OUT/'source-review.json'),boundary_sha256=sha(OUT/'boundary-plan-v2.json'))))


if __name__=='__main__':main()
