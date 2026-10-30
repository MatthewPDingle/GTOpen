#[path="research_bounded_output_v1.rs"] mod research_bounded_output_v1;
use std::error::Error;
use std::path::Path;
fn run()->Result<(),Box<dyn Error>> {
    let (args,limit)=research_bounded_output_v1::arguments(2048)?;
    assert_eq!(args.len(),3);
    match args[0].as_str() {
        "bytes" => {
            let bytes=std::fs::read(&args[1])?;
            research_bounded_output_v1::emit(Some((Path::new(&args[2]),&bytes)),b"out\n",b"note\n",limit)
        },
        "stdio" => {
            let bytes=std::fs::read(&args[1])?;
            research_bounded_output_v1::emit(None,&bytes,b"note\n",limit)
        },
        "empty" => research_bounded_output_v1::emit(Some((Path::new(&args[2]),&[])),&[],&[],limit),
        "large-error" => Err("error".repeat(200_000).into()),
        "large-panic" => panic!("{}","panic".repeat(200_000)),
        _ => Err("Unknown software fixture mode".into()),
    }
}
fn main(){research_bounded_output_v1::entry(run);}
