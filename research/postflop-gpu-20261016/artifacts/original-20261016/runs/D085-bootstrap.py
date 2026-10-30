"""Fetch checksum-pinned NVIDIA profiling headers/libraries into research storage only."""
import hashlib,json,shutil,sys,urllib.request,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();assert shutil.disk_usage(ROOT).free>=54*1024**3
H=ROOT/'runs/D085-cupti-activity';assert not H.exists();H.mkdir();V=H/'vendor';V.mkdir()
base='https://developer.download.nvidia.com/compute/cuda/redist/';manifest_url=base+'redistrib_12.9.1.json'
data=urllib.request.urlopen(manifest_url,timeout=30).read();(H/'redistrib_12.9.1.json').write_bytes(data);manifest=json.loads(data)
expected={'cuda_cupti':('12.9.79','c96018456dc4db6af6d69d6db0170a2ccc656ddde8c8ce6ee05682c2c5569daa',13359912),'cuda_cudart':('12.9.79','179e9c43b0735ffe67207b3da556eb5a0c50f3047961882b7657d3b822d34ef8',3521238)}
packages={}
for name,(version,digest,size) in expected.items():
 info=manifest[name]['windows-x86_64'];assert manifest[name]['version']==version and info['sha256']==digest and int(info['size'])==size
 url=base+info['relative_path'];dest=V/Path(info['relative_path']).name;assert not dest.exists()
 with urllib.request.urlopen(url,timeout=60) as response,dest.open('xb') as output:shutil.copyfileobj(response,output)
 assert dest.stat().st_size==size and old.sha(dest)==digest
 out=V/name;out.mkdir();total=0
 with zipfile.ZipFile(dest) as archive:
  for member in archive.infolist():
   target=(out/member.filename).resolve();assert target.is_relative_to(out.resolve()) and not member.filename.startswith(('/','\\'));total+=member.file_size
  assert total<256*1024**2
  archive.extractall(out)
 files={str(p.relative_to(out)):{'sha256':old.sha(p),'bytes':p.stat().st_size} for p in out.rglob('*') if p.is_file()}
 packages[name]={'url':url,'version':version,'archive':str(dest),'sha256':digest,'bytes':size,'unpacked_bytes':total,'files':files}
 print(name,'downloaded, hash verified and extracted locally.',flush=True)
docs={}
for name,url in [('cupti12.9-usage.html','https://docs.nvidia.com/cupti/12.9.1/main/main.html'),('cupti12.9-activity.html','https://docs.nvidia.com/cupti/12.9.1/api/group__CUPTI__ACTIVITY__API.html'),('nsight-current-guide.html','https://docs.nvidia.com/nsight-systems/UserGuide/index.html')]:
 data=urllib.request.urlopen(url,timeout=30).read();(H/name).write_bytes(data);docs[name]={'url':url,'sha256':old.sha(H/name)}
old.save(H/'bootstrap.json',{'at':old.now(),'status':'official_components_ready_local_only','manifest_url':manifest_url,'manifest_sha256':old.sha(H/'redistrib_12.9.1.json'),'packages':packages,'docs':docs,'system_installation':False,'privilege_or_driver_change':False,'global_environment_change':False,'kernel_launches':0,'solver_executions':0,'performance_measured':False,'accepted_source':'E051','goal_active':True})
old.custody();print('D085 components ready; no installation, profiling or solver launch.',flush=True)
