"""One registered large GPU run, then an independent saved-game audit."""
import gzip
import json
from run07 import HERE, LAB, RAW, digest, run

NAME='large-normalized-quality-v1'


def main():
    exe=LAB/'target/release/examples/convergence_large_normalized_quality.exe'
    cfg=HERE.parent/'03-preflop-20260910/user-session.json'
    paths=HERE/'broad-paths.json'
    out=LAB/'target/convergence'/NAME
    run(NAME,[exe,cfg,paths,out],10800,[exe,cfg,paths])
    original=out/'result.json'
    packed=RAW/(NAME+'-result.json.gz')
    packed.write_bytes(gzip.compress(original.read_bytes(),mtime=0))
    (RAW/(NAME+'-result-envelope.json')).write_text(json.dumps(dict(
        original_bytes=original.stat().st_size,original_sha256=digest(original),
        gzip_sha256=digest(packed)),indent=2)+'\n',encoding='utf-8')
    audit_exe=LAB/'target/release/examples/convergence_audit_paths.exe'
    saved=out/'final.gtop'
    run(NAME+'-audit',[audit_exe,saved,paths,RAW/(NAME+'-audit.json')],300,
        [audit_exe,saved,paths])


if __name__=='__main__':
    main()
