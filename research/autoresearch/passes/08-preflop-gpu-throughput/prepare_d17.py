"""Add an optional test-only support witness without changing D10 outputs."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parents[3]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    path=LAB/'crates/solver/src/preflop/gpu/terminal_tiles.rs'
    original=path.read_bytes();source=original.decode();nl='\r\n' if '\r\n' in source else '\n'
    source=source.replace('\r\n','\n')
    old='    let mut rows=Vec::new();\n'
    new='''    let mut support_out=std::env::var("PREFLOP_GPU_SUPPORT_WITNESS").ok().map(|path| {
        let mut file=std::io::BufWriter::new(std::fs::OpenOptions::new().create_new(true).write(true).open(path).unwrap());
        file.write_all(b"D17V1\\0\\0\\0").unwrap();
        file.write_all(&(g.np as u32).to_le_bytes()).unwrap();file
    });
    let mut rows=Vec::new();
'''
    assert source.count(old)==1;source=source.replace(old,new)
    old='                if unique>previous {unique_support[support]+=1;}\n'
    new='''                if unique>previous {
                    unique_support[support]+=1;
                    if mode==0 {if let Some(file)=support_out.as_mut() {
                        for x in [mode as u32,p as u32,previous] {file.write_all(&x.to_le_bytes()).unwrap();}
                        let mut mask=[0u64;3];
                        for (h,x) in v.iter().enumerate(){if *x!=0.0 {mask[h/64]|=1u64<<(h%64);}}
                        assert_eq!(mask.iter().map(|x|x.count_ones() as usize).sum::<usize>(),support);
                        for x in mask {file.write_all(&x.to_le_bytes()).unwrap();}
                    }}
                }
'''
    assert source.count(old)==1;source=source.replace(old,new)
    source=source.replace('    out.flush().unwrap();\n','    out.flush().unwrap();\n    if let Some(file)=support_out.as_mut(){file.flush().unwrap();}\n')
    result=source.replace('\n',nl).encode();path.write_bytes(result)
    archive=HERE/'artifacts/d17-v1';archive.mkdir(exist_ok=False)
    (archive/'terminal_tiles.before.rs').write_bytes(original)
    (archive/'terminal_tiles.rs').write_bytes(result)
    (HERE/'artifacts/d17-v1-source-map.json').write_text(json.dumps({str(path.relative_to(LAB)):sha(result)},indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
