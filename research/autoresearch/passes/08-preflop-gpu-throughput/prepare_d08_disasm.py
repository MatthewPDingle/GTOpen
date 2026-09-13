"""Local official nvdisasm component only; no driver or global installation."""
import hashlib,json,urllib.request,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parents[3]
def main():
    root=LAB/'target/research-tools';manifest=json.loads((HERE/'raw/d08-redistribution-manifest.json').read_text())
    spec=manifest['cuda_nvdisasm']['windows-x86_64'];assert spec['sha256']=='3313278cb452427954a271cc9971b9e8e0688b2d09906b8c2f5e8176b990d011'
    url='https://developer.download.nvidia.com/compute/cuda/redist/'+spec['relative_path']
    data=urllib.request.urlopen(url,timeout=30).read();assert len(data)==int(spec['size']) and hashlib.sha256(data).hexdigest()==spec['sha256']
    archive=root/Path(spec['relative_path']).name;assert not archive.exists();archive.write_bytes(data)
    target=root/'nvdisasm-13.1.115';assert not target.exists();target.mkdir()
    with zipfile.ZipFile(archive) as z:
        for member in z.infolist():assert (target/member.filename).resolve().is_relative_to(target.resolve())
        z.extractall(target)
    exe=list(target.rglob('nvdisasm.exe'));assert len(exe)==1
    r=dict(download_url=url,archive_sha256=spec['sha256'],archive_bytes=len(data),executable=str(exe[0]),executable_sha256=hashlib.sha256(exe[0].read_bytes()).hexdigest())
    (HERE/'raw/d08-disasm-provenance.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
if __name__=='__main__':main()
