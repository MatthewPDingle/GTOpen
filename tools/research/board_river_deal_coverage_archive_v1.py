"""Small, independently readable case archives with verified scratch cleanup."""
import hashlib
from pathlib import Path
import os
import zipfile
from board_river_deal_coverage_common_v1 import STORE,read,sha
from board_prefix_publication_v1 import atomic_json

MEMBERS=('request.json','export.json','policies.npz','record.json')
MAX_RAW=32_000_000


def read_archive(path,manifest):
    path=Path(path);assert manifest['archive_sha256']==sha(path)
    with zipfile.ZipFile(path,'r') as z:
        infos=z.infolist();assert len(infos)==4 and {i.filename for i in infos}==set(MEMBERS)
        assert sum(i.file_size for i in infos)<=MAX_RAW
        values={}
        for item in infos:
            data=z.read(item.filename);expected=manifest['members'][item.filename]
            assert len(data)==expected['bytes'] and hashlib.sha256(data).hexdigest()==expected['sha256']
            values[item.filename]=data
    return values


def pack(folder,path):
    folder=Path(folder).resolve();path=Path(path).resolve();root=STORE.resolve()
    assert folder.parent in (root/'work',root/'control-v2') and path.parent in (root/'cases',root/'control-v2')
    assert not folder.is_symlink() and folder.is_dir()
    data={}
    for name in MEMBERS:
        source=folder/name
        assert source.resolve().parent==folder and not source.is_symlink()
        assert not source.lstat().st_file_attributes&0x400
        data[name]=source.read_bytes()
    assert sum(map(len,data.values()))<=MAX_RAW
    manifest_path=path.with_suffix('.manifest.json')
    manifest=dict(format=1,archive=path.name,members={name:dict(bytes=len(value),sha256=hashlib.sha256(value).hexdigest()) for name,value in data.items()})
    if path.exists():
        # A finished archive whose marker was interrupted may be recovered only
        # by checking it against every unchanged retained scratch member.
        manifest['archive_sha256']=sha(path);assert read_archive(path,manifest)==data
    else:
        with zipfile.ZipFile(path,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=3) as z:
            for name,value in data.items():z.writestr(name,value)
        with path.open('r+b') as f:os.fsync(f.fileno())
        manifest['archive_sha256']=sha(path);assert read_archive(path,manifest)==data
    if manifest_path.exists():assert read(manifest_path)==manifest
    else:atomic_json(manifest_path,manifest)
    # Only these four exact, owned transient files are removed after readback.
    # No recursive removal, historical deletion, or unverified computed target.
    for name,value in data.items():
        source=folder/name;assert source.resolve().parent==folder and source.read_bytes()==value
        source.unlink()
    return dict(archive_sha256=manifest['archive_sha256'],manifest_sha256=sha(manifest_path),
        compressed_bytes=path.stat().st_size,raw_bytes=sum(map(len,data.values())))
