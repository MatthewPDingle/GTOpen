import json,shutil,sys,urllib.request,zipfile
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();assert shutil.disk_usage(ROOT).free>=54*1024**3
manifest=old.read(H/'redistrib_12.9.1.json');info=manifest['cuda_nvcc']['windows-x86_64'];assert info['sha256']=='227b109663b5e57d2718bcabb24a4ba0d9d4e52d958e327dc476f7c28691be85' and int(info['size'])==126917884
url='https://developer.download.nvidia.com/compute/cuda/redist/'+info['relative_path'];dest=H/'vendor'/Path(info['relative_path']).name;assert not dest.exists()
with urllib.request.urlopen(url,timeout=60) as response,dest.open('xb') as out:shutil.copyfileobj(response,out)
assert old.sha(dest)==info['sha256'] and dest.stat().st_size==int(info['size']);folder=H/'vendor/cuda_nvcc_headers';folder.mkdir()
with zipfile.ZipFile(dest) as archive:
 selected=[x for x in archive.infolist() if '/include/' in x.filename or x.filename.endswith('LICENSE.txt')]
 for item in selected:
  p=(folder/item.filename).resolve();assert p.is_relative_to(folder.resolve())
  archive.extract(item,folder)
old.save(H/'bootstrap-headers.json',{'at':old.now(),'package_url':url,'package_sha256':old.sha(dest),'version':manifest['cuda_nvcc']['version'],'only_headers_and_license_extracted':True,'files':{str(p):old.sha(p) for p in folder.rglob('*') if p.is_file()},'system_installation':False,'native_executions':0})
old.save(H/'build-r2/terminal.json',{'at':old.now(),'returncode':1,'failure':'CUDA runtime headers require crt/host_defines.h from the separate official nvcc redistribution. C++compilation stopped before linking; no native execution.','native_executions':0})
P=old.read(H/'build-plan-r2.json');oldB=P['build_dir'];B=H/'build-r3';P.update(id='D085-build-r3',at=old.now(),build_dir=str(B),private_dll_dirs=[str(B),P['private_dll_dirs'][1]],repair='Add matching official CUDA compiler header tree; preserve source, initial test protocol and all failures.')
for key in ['collector_command','ability_command']:P[key]=[s.replace(oldB,str(B)) for s in P[key]]
include=folder/'cuda_nvcc-windows-x86_64-12.9.86-archive/include';assert (include/'crt/host_defines.h').exists();P['collector_command'].insert(8,'/I'+str(include))
src=(H/'build-r2.py').read_text().replace("'build-plan-r2.json'","'build-plan-r3.json'");script=H/'build-r3.py';script.write_text(src,encoding='utf-8',newline='\n');P['input_sha256']|={str(p):old.sha(p) for p in [script,H/'build-plan-r2.json',H/'bootstrap-headers.json',*list(include.rglob('*.h')),*list((H/'build-r2').glob('*'))] if p.is_file()};old.save(H/'build-plan-r3.json',P)
print(old.sha(H/'build-plan-r3.json'),flush=True)
