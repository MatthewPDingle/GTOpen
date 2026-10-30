import ctypes as c,os,sys,json,time,hashlib
from pathlib import Path
assert len(sys.argv)==5
library=Path(sys.argv[1]);source=Path(sys.argv[2]);output=Path(sys.argv[3]);expected_version=json.loads(sys.argv[4])
assert library.is_absolute() and source.is_absolute() and output.is_absolute()
assert c.sizeof(c.c_void_p)==8 and c.sizeof(c.c_size_t)==8 and c.sizeof(c.c_int)==4
start=time.perf_counter_ns()
# Only this child process's dependency lookup changes; absolute primary DLL.
directory=os.add_dll_directory(str(library.parent));dll=c.CDLL(str(library))
def bind(name,args):
    f=getattr(dll,name);f.argtypes=args;f.restype=c.c_int;return f
version=bind('nvrtcVersion',[c.POINTER(c.c_int),c.POINTER(c.c_int)])
num_archs=bind('nvrtcGetNumSupportedArchs',[c.POINTER(c.c_int)])
archs=bind('nvrtcGetSupportedArchs',[c.POINTER(c.c_int)])
create=bind('nvrtcCreateProgram',[c.POINTER(c.c_void_p),c.c_char_p,c.c_char_p,c.c_int,c.POINTER(c.c_char_p),c.POINTER(c.c_char_p)])
compile_=bind('nvrtcCompileProgram',[c.c_void_p,c.c_int,c.POINTER(c.c_char_p)])
ptx_size=bind('nvrtcGetPTXSize',[c.c_void_p,c.POINTER(c.c_size_t)])
ptx_get=bind('nvrtcGetPTX',[c.c_void_p,c.c_void_p])
log_size=bind('nvrtcGetProgramLogSize',[c.c_void_p,c.POINTER(c.c_size_t)])
log_get=bind('nvrtcGetProgramLog',[c.c_void_p,c.c_void_p])
destroy=bind('nvrtcDestroyProgram',[c.POINTER(c.c_void_p)])
calls=[]
def checked(name,fn,*args):
    result=fn(*args);calls.append({'api':name,'returncode':result});assert result==0,(name,result)
a=c.c_int();b=c.c_int();checked('nvrtcVersion',version,c.byref(a),c.byref(b));actual=[a.value,b.value];assert actual==expected_version
n=c.c_int();checked('nvrtcGetNumSupportedArchs',num_archs,c.byref(n));assert 0<n.value<1000
supported=(c.c_int*n.value)();checked('nvrtcGetSupportedArchs',archs,supported);assert 120 in supported
program=c.c_void_p();src=source.read_bytes();assert b'\0' not in src
options=[b'--gpu-architecture=compute_120'];opt=(c.c_char_p*len(options))(*options)
checked('nvrtcCreateProgram',create,c.byref(program),src,None,0,None,None);assert program.value
compile_result=None;log=b'';ptx=b''
try:
    compile_result=compile_(program,len(options),opt);calls.append({'api':'nvrtcCompileProgram','returncode':compile_result})
    size=c.c_size_t();checked('nvrtcGetProgramLogSize',log_size,program,c.byref(size));assert 0<size.value<1024*1024
    data=c.create_string_buffer(size.value);checked('nvrtcGetProgramLog',log_get,program,data);log=data.raw;assert log.endswith(b'\0')
    with output.with_suffix('.compiler.log').open('xb') as f:f.write(log)
    assert compile_result==0,log.decode('utf-8',errors='replace')
    checked('nvrtcGetPTXSize',ptx_size,program,c.byref(size));assert 0<size.value<8*1024*1024
    data=c.create_string_buffer(size.value);checked('nvrtcGetPTX',ptx_get,program,data);ptx=data.raw;assert ptx.endswith(b'\0') and b'\0' not in ptx[:-1]
finally:
    checked('nvrtcDestroyProgram',destroy,c.byref(program));destroy_cleared_handle=program.value is None
    # Successful destruction ends ownership even if the API does not clear it.
    program.value=None
acquisition_ns=time.perf_counter_ns()-start
with output.open('xb') as f:f.write(ptx[:-1])
record={'DLL_path':str(library),'DLL_sha256':hashlib.sha256(library.read_bytes()).hexdigest(),'version':actual,'supported_architectures':list(supported),'source_sha256':hashlib.sha256(src).hexdigest(),'program_name':None,'headers':0,'options':[x.decode() for x in options],'API_calls':calls,'program_destroyed_and_pointer_null':program.value is None,'API_itself_cleared_handle':destroy_cleared_handle,'PTX_bytes_without_NUL':len(ptx)-1,'PTX_sha256':hashlib.sha256(ptx[:-1]).hexdigest(),'standalone_acquisition_ns_diagnostic_only':acquisition_ns,'GPU_context_or_kernel_calls':0,'scope':'One original compile in fresh CPU-only child through exact header-bound C API. Diagnostic cold acquisition includes query adapter work;not comparable solver timing or speed score.'}
with output.with_suffix('.compile.json').open('x',encoding='utf-8') as f:json.dump(record,f,indent=2)
print(json.dumps({k:record[k] for k in ['version','options','program_destroyed_and_pointer_null','PTX_bytes_without_NUL','PTX_sha256','GPU_context_or_kernel_calls']}),flush=True)
