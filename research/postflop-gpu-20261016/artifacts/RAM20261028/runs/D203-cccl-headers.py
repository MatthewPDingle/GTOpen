import hashlib,json,shutil,sys,urllib.request,zipfile
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists() and not(ROOT/'epoch-sequence.lock').exists()
assert h.read(ROOT/'runs/D202-cooperative-scope/report.json')['attributes']['cooperative_launch']==1
H=ROOT/'runs/D203-cccl-header-bootstrap';H.mkdir(exist_ok=False)
filename='nvidia_cuda_cccl_cu12-12.9.27-py3-none-win_amd64.whl';digest='72106f95a9bb3be18472806b4f663ebf0f9248a86d14b4ae3305725b855d9d92';size=3152175
url='https://files.pythonhosted.org/packages/ce/9b/1daf405620c7ac371b76b823c6336dd742673d41a150d9a04eec2c690379/'+filename
h.save(H/'protocol.json',{'id':'D203-cccl','at':h.now(),'status':'FROZEN_PRE_PRIVATE_HEADER_WHEEL_DOWNLOAD','source_script_sha256':h.sha(__file__),'package':'nvidia-cuda-cccl-cu12','version':'12.9.27','platform':'win_amd64','wheel_filename':filename,'wheel_sha256':digest,'wheel_bytes':size,'url':url,'metadata_source':'https://pypi.org/pypi/nvidia-cuda-cccl-cu12/12.9.27/json','official_distribution_docs':'https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/index.html','scope':'Download exactNVIDIA-ownedPyPIwheel andextract only unmodifiedincludeheaders anddistributionmetadata/licenses onX,not DLLs. No pipinstall/globalPATH/systemCUDA/runtime/NVRTC/dependency/sourcechange,compiler/native/GPU query/kernel. Headeravailabilitydoesnotproveprimitivecompileorperformance. Preservewheel/sha/inventory;do notpublishvendorheadercode.','required_X_free_bytes':64*1024**3,'peak_output_reservation_bytes':256*1024**2})
assert shutil.disk_usage(ROOT).free>=64*1024**3
wheel=H/filename;assert not wheel.exists()
with urllib.request.urlopen(url,timeout=60) as response, wheel.open('xb') as out:shutil.copyfileobj(response,out)
assert wheel.stat().st_size==size;h.pin(wheel,digest)
out=H/'package';out.mkdir(exist_ok=False);selected=[];skipped=[]
with zipfile.ZipFile(wheel) as z:
 for entry in z.infolist():
  if entry.is_dir():continue
  relative=PurePosixPath(entry.filename);assert not relative.is_absolute() and '..' not in relative.parts and entry.file_size<16*1024**2
  name=relative.as_posix();keep=name.startswith('nvidia/cuda_cccl/include/') or '.dist-info/' in name
  if not keep:skipped.append(name);continue
  target=out.joinpath(*relative.parts);assert target.resolve().is_relative_to(out.resolve());target.parent.mkdir(parents=True,exist_ok=True);assert not target.exists();target.write_bytes(z.read(entry));selected.append({'path':name,'bytes':target.stat().st_size,'sha256':h.sha(target)})
assert any(x['path']=='nvidia/cuda_cccl/include/nv/target' for x in selected)
assert not list(out.rglob('*.dll')) and not list(out.rglob('*.lib'))
h.save(H/'report.json',{'id':'D203-cccl','at':h.now(),'status':'private_verified_12_9_headers_available','protocol_sha256':h.sha(H/'protocol.json'),'wheel_sha256':h.sha(wheel),'include_directory':str(out/'nvidia/cuda_cccl/include'),'selected_files':selected,'skipped_native_library_paths':skipped,'extracted_bytes':sum(x['bytes'] for x in selected),'global_or_project_changes':0,'compiler_or_native_GPU_processes':0,'new_gain_accepted':False,'scope':'Exactvendorheaderspluslicenses/metadata only, no runtimeDLLloaded/installed. No CUDA12.9compile/barrier/kernel/solverclaim. Main/live/accepted source/oldPTXunchanged.'})
h.custody();print(json.dumps({'status':'private_headers_verified','header_and_metadata_files':len(selected),'bytes':sum(x['bytes'] for x in selected),'nv_target':True,'native_libraries_extracted':0}),flush=True)
