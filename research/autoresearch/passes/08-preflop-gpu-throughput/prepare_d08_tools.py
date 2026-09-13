"""Download and verify one portable official profiling component, no installer."""
import hashlib,json,time,urllib.request,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parents[3]
BASE='https://developer.download.nvidia.com/compute/cuda/redist/'
def main():
    root=LAB/'target/research-tools';root.mkdir(exist_ok=True)
    source=BASE+'redistrib_13.1.1.json';manifest=urllib.request.urlopen(source,timeout=30).read()
    x=json.loads(manifest)['nsight_compute'];assert x['version']=='2025.4.1.2'
    spec=x['windows-x86_64'];assert spec['sha256']=='cb26a33427f34606b063166538f00f8eced3e0bc1c5bc21c1385d0e270ceefab'
    archive=root/Path(spec['relative_path']).name;assert not archive.exists()
    started=time.monotonic();h=hashlib.sha256();size=0
    with urllib.request.urlopen(BASE+spec['relative_path'],timeout=30) as response,archive.open('xb') as out:
        while data:=response.read(1024*1024):
            assert time.monotonic()-started<240,'download time cap'
            out.write(data);h.update(data);size+=len(data)
    assert h.hexdigest()==spec['sha256'] and size==int(spec['size'])
    destination=root/'nsight-compute-2025.4.1.2';assert not destination.exists();destination.mkdir()
    with zipfile.ZipFile(archive) as z:
        for info in z.infolist():
            resolved=(destination/info.filename).resolve();assert resolved.is_relative_to(destination.resolve()),info.filename
        z.extractall(destination)
    executables=list(destination.rglob('ncu.exe'));assert len(executables)==1
    result=dict(manifest_url=source,manifest_sha256=hashlib.sha256(manifest).hexdigest(),version=x['version'],
        download_url=BASE+spec['relative_path'],archive_sha256=h.hexdigest(),archive_bytes=size,
        directory=str(destination),executable=str(executables[0]),executable_sha256=hashlib.sha256(executables[0].read_bytes()).hexdigest())
    raw=HERE/'raw';(raw/'d08-redistribution-manifest.json').write_bytes(manifest)
    (raw/'d08-tool-provenance.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)
if __name__=='__main__':main()
