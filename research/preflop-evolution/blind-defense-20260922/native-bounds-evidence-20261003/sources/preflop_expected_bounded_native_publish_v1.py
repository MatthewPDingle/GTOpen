"""Create separate research-only native exporters; preserve original sources."""
from pathlib import Path
import hashlib
import json
import time

STAGE = Path(__file__).resolve().parent
REPO = Path(r'T:\Dev\GTOpen')
EXAMPLES = REPO / 'crates/solver/examples'
PROOF = STAGE / 'native-bounded-export-sources-v1'
HELPER = STAGE / 'research_bounded_output_v1.rs'
DEST_HELPER = EXAMPLES / 'research_sampled/research_bounded_output_v1.rs'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def replace_one(source, old, new):
    if source.count(old) != 1:
        raise ValueError(f'Expected one exact source site: {old!r}')
    return source.replace(old, new)

def variants():
    board = (EXAMPLES / 'hu_fixed_board_tree_v1.rs').read_text()
    board = replace_one(board, 'fn main()->Result<(),Box<dyn std::error::Error>> {',
        'fn run_bounded()->Result<(),Box<dyn std::error::Error>> {')
    board = replace_one(board,
        'let args:Vec<_>=std::env::args().skip(1).collect();assert_eq!(args.len(),2);',
        'let (args,output_limit)=research_bounded_output_v1::arguments(2_000_000_000)?;assert_eq!(args.len(),2);')
    board = replace_one(board,
        'println!("{}",json!({"format":1,"board":board,"hands":hands,"ranks":ranks,"branches":branches}));Ok(())',
        'let mut bytes=serde_json::to_vec(&json!({"format":1,"board":board,"hands":hands,"ranks":ranks,"branches":branches}))?;\n    bytes.push(b\'\\n\');research_bounded_output_v1::emit(None,&bytes,&[],output_limit)?;Ok(())')
    bridge = (EXAMPLES / 'hu_sampled_allin_history_bridge_v1.rs').read_text()
    bridge = replace_one(bridge, 'fn main()->Result<(),Box<dyn std::error::Error>>{',
        'fn run_bounded()->Result<(),Box<dyn std::error::Error>>{')
    bridge = replace_one(bridge,
        'let a:Vec<_>=std::env::args().skip(1).collect();assert_eq!(a.len(),5);',
        'let (a,output_limit)=research_bounded_output_v1::arguments(64_000_000)?;assert_eq!(a.len(),5);')
    bridge = replace_one(bridge,
        'std::fs::write(&a[4],serde_json::to_vec(&result)?)?;println!("{}",json!({"mode":a[0],"raw_queries":q.raw_len(),"observations":q.observations.len()}));Ok(())',
        'let bytes=serde_json::to_vec(&result)?;let mut status=serde_json::to_vec(&json!({"mode":a[0],"raw_queries":q.raw_len(),"observations":q.observations.len()}))?;\n status.push(b\'\\n\');research_bounded_output_v1::emit(Some((std::path::Path::new(&a[4]),&bytes)),&status,&[],output_limit)?;Ok(())')
    trace = (EXAMPLES / 'hu_sampled_action_trace_v2.rs').read_text()
    trace = replace_one(trace, 'fn main() -> Result<(), Box<dyn std::error::Error>> {',
        'fn run_bounded() -> Result<(), Box<dyn std::error::Error>> {')
    trace = replace_one(trace,
        'let args: Vec<_> = std::env::args().skip(1).collect();',
        'let (args, output_limit) = research_bounded_output_v1::arguments(64_000_000)?;')
    trace = replace_one(trace,
        'std::fs::write(&args[3], serde_json::to_vec(&result)?)?;',
        'let bytes = serde_json::to_vec(&result)?;\n    research_bounded_output_v1::emit(Some((std::path::Path::new(&args[3]), &bytes)), &[], &[], output_limit)?;')
    river = (EXAMPLES / 'hu_river_two_stage_stream_v1.rs').read_text()
    river = replace_one(river, 'fn main()->Result<(),Box<dyn std::error::Error>> {',
        'fn run_bounded()->Result<(),Box<dyn std::error::Error>> {')
    river = replace_one(river, 'let args:Vec<_>=std::env::args().skip(1).collect();',
        'let (args,output_limit)=research_bounded_output_v1::arguments(MAX_BYTES)?;')
    river = replace_one(river,
        'bytes.push(b\'\\n\');if bytes.len()>MAX_BYTES {return Err("Output byte budget exceeded".into());}\n    let mut output=std::io::stdout().lock();output.write_all(&bytes)?;output.flush()?;\n    eprintln!("{}",json!({"passed":true,"mode":result["mode"],"nodes":result["total_nodes"],\n        "observations":result["queries"]["observations"].as_array().unwrap().len(),"bytes":bytes.len()}));Ok(())',
        'bytes.push(b\'\\n\');let mut status=serde_json::to_vec(&json!({"passed":true,"mode":result["mode"],"nodes":result["total_nodes"],\n        "observations":result["queries"]["observations"].as_array().unwrap().len(),"bytes":bytes.len()}))?;\n    status.push(b\'\\n\');research_bounded_output_v1::emit(None,&bytes,&status,output_limit)?;Ok(())')
    names = [
        ('hu_fixed_board_tree_v1.rs','hu_fixed_board_tree_bounded_v2.rs',board),
        ('hu_sampled_allin_history_bridge_v1.rs','hu_sampled_allin_history_bridge_bounded_v2.rs',bridge),
        ('hu_sampled_action_trace_v2.rs','hu_sampled_action_trace_bounded_v3.rs',trace),
        ('hu_river_two_stage_stream_v1.rs','hu_river_two_stage_stream_bounded_v2.rs',river),
    ]
    return [(old,new,'#[path="research_sampled/research_bounded_output_v1.rs"] mod research_bounded_output_v1;\n'+text+'\nfn main(){research_bounded_output_v1::entry(run_bounded);}\n') for old,new,text in names]

def main():
    intended = variants()
    for destination in [DEST_HELPER,*[EXAMPLES/new for _,new,_ in intended]]:
        if destination.exists(): raise FileExistsError(destination)
    if PROOF.exists(): raise FileExistsError(PROOF)
    review = STAGE / 'native-export-bounds-review-v1/source-pins.json'
    original_pins = json.loads(review.read_text())['source_identities']
    for path, digest in original_pins.items():
        if sha(path) != digest: raise ValueError(f'Original pin changed: {path}')
    PROOF.mkdir()
    before = {str(EXAMPLES/old):sha(EXAMPLES/old) for old,_,_ in intended}
    records = []
    for old,new,text in intended:
        raw = text.encode('utf-8')
        destination = EXAMPLES / new
        with destination.open('xb') as file: file.write(raw)
        (PROOF/new).write_bytes(raw)
        records.append(dict(original=str(EXAMPLES/old),original_sha256=before[str(EXAMPLES/old)],
            new=str(destination),new_sha256=sha(destination)))
    with DEST_HELPER.open('xb') as file: file.write(HELPER.read_bytes())
    (PROOF/HELPER.name).write_bytes(HELPER.read_bytes())
    for path,digest in before.items():
        if sha(path) != digest: raise ValueError(f'Original source mutated: {path}')
    result = dict(format=1,method='research-export-only-bounded-sources-v1',created=time.time(),
        originals_preserved=True,sources=records,helper=dict(path=str(DEST_HELPER),sha256=sha(DEST_HELPER)),
        failure_reserve=256,board_ceiling=2_000_000_000,transport_ceiling=64_000_000,
        optional_final_limit_argument='--output-byte-limit=',
        scope='Serialization/resource boundary only; no poker calculation, native run or accuracy evidence.')
    with (PROOF/'publication.json').open('x') as file: json.dump(result,file,indent=2)
    print(json.dumps(result,indent=2))

if __name__ == '__main__': main()
