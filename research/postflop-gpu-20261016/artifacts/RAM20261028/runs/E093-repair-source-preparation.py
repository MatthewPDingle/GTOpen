import sys,ast,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists();original=ROOT/'runs/E093-prepare-source-build.py';failed=ROOT/'runs/E093-source'
assert not(failed/'manifest.json').exists() and not(ROOT/'runs/E093-build-plan').exists() and not(ROOT/'runs/E093-build.py').exists()
manifest=(h.REPO/'crates/solver/Cargo.toml').read_bytes();crlf=manifest.count(b'\r\n');lf=manifest.count(b'\n')-crlf;assert crlf>0 and lf>0
assert h.read(failed/'preparation-failure.json')['status']=='invalid_source_packager_line_ending_normalization_preserved'
text=original.read_text(encoding='utf-8');text=text.replace("S=ROOT/'runs/E093-source'","S=ROOT/'runs/E093-source-r2'",1)
start=text.index('for name in basefiles:');end=text.index("\nnew='crates/solver/src/gpu/nvrtc13.rs'",start)
body=r'''for name in basefiles:
    original=(h.REPO/name).read_bytes();base=S/'base'/name;candidate=S/'candidate'/name;base.parent.mkdir(parents=True,exist_ok=True);candidate.parent.mkdir(parents=True,exist_ok=True);base.write_bytes(original)
    text=original;edits=[]
    def apply(data,old,new):
        assert data.count(old)==1;edits.append((old,new));return data.replace(old,new,1)
    def after_line(data,token):
        assert data.count(token)==1;pos=data.index(token)+len(token)
        nl=b'\r\n' if data[pos:pos+2]==b'\r\n' else b'\n';assert data[pos:pos+len(nl)]==nl;return token+nl,nl
    if name=='Cargo.lock':
        old=b'name = "solver"\nversion = "0.1.0"\ndependencies = [\n "cudarc",\n'
        text=apply(text,old,old+b' "libloading",\n')
    elif name.endswith('Cargo.toml'):
        old,nl=after_line(text,b'mimalloc = "0.1"');text=apply(text,old,old+b'libloading = { version = "0.9", optional = true }'+nl)
        text=apply(text,b'gpu = ["dep:cudarc"]',b'gpu = ["dep:cudarc", "dep:libloading"]')
    else:
        old,nl=after_line(text,b'mod arena;');text=apply(text,old,old+b'#[cfg(all(target_os = "windows", target_pointer_width = "64"))]'+nl+b'mod nvrtc13;'+nl)
        old,nl=after_line(text,b'            .get_or_init(|| {')
        addition=b'                #[cfg(all(target_os = "windows", target_pointer_width = "64"))]'+nl+b'                if let Some(ptx) = nvrtc13::try_compile(arch, include_str!("kernels.cu")) {'+nl+b'                    return Ok(ptx);'+nl+b'                }'+nl
        text=apply(text,old,old+addition)
    reverse=text
    for old,new in reversed(edits):assert reverse.count(new)==1;reverse=reverse.replace(new,old,1)
    assert reverse==original;candidate.write_bytes(text);changed[name]=h.sha(candidate);reversals[name]=True
    owned[name]={'base':str(base),'base_sha256':BASE[name],'candidate':str(candidate),'candidate_sha256':changed[name]}
'''
# Raw replacement already contains the correct literal byte-string escapes.
text=text[:start]+body.rstrip()+text[end:]
text=text.replace("'status':'isolated_source_frozen_not_activated'","'status':'isolated_source_frozen_not_activated','original_preparation_invalid_preserved':True,'packager_repair':'Byte-local inserts preserve mixed line endings;runtime helper and intended dependency/cache choices unchanged'",1)
text=text.replace("files=[Path(__file__),ROOT/'runs/E093-build-template.py'","files=[Path(__file__),ROOT/'runs/E093-repair-source-preparation.py',ROOT/'runs/E093-source/preparation-failure.json',ROOT/'runs/E093-build-template.py'",1)
script=ROOT/'runs/E093-prepare-source-build-r2.py';assert not script.exists();ast.parse(text);script.write_bytes(text.encode())
h.save(failed/'repair-review.json',{'at':h.now(),'status':'mechanical_pre_activation_byte_preservation_repair','failed_attempt_remains_invalid':True,'new_script_sha256':h.sha(script),'changes':'Only sourcepackager byte-local replacements andseparateR2artifactfolder. Exactsame helper and intended Cargo/module/cache diff. All3reverse checks now compareoriginalbytes without lineendingnormalization. Originalpartialfiles/failure retained. No appactivation/Cargo/native/numerical/performance observation repeated.'})
subprocess.run([sys.executable,str(script)],cwd=h.REPO,check=True)
