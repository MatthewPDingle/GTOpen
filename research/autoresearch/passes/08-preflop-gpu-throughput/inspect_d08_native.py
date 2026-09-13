"""Driver-linked disassembly diagnostic. No kernel launches or counter access."""
import ctypes as C
import hashlib,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw'
def main():
    out=RAW/'d08-native-v2';assert not out.exists();out.mkdir()
    tool=json.loads((RAW/'d08-disasm-provenance.json').read_text())['executable']
    dll=C.WinDLL('C:/Windows/System32/nvcuda.dll');P=C.c_void_p;I=C.c_int;U=C.c_uint;S=C.c_size_t
    def bind(name,args):
        f=getattr(dll,name);f.argtypes=args;f.restype=I
        def call(*args):
            rc=f(*args)
            if rc:raise RuntimeError(f'{name}: CUDA error {rc}')
        return call
    init=bind('cuInit',[U]);device_get=bind('cuDeviceGet',[C.POINTER(I),I]);version=bind('cuDriverGetVersion',[C.POINTER(I)])
    create=bind('cuCtxCreate_v2',[C.POINTER(P),U,I]);destroy=bind('cuCtxDestroy_v2',[P])
    link_create=bind('cuLinkCreate_v2',[U,C.POINTER(I),C.POINTER(P),C.POINTER(P)])
    link_add=bind('cuLinkAddData_v2',[P,I,P,S,C.c_char_p,U,C.POINTER(I),C.POINTER(P)])
    link_complete=bind('cuLinkComplete',[P,C.POINTER(P),C.POINTER(S)]);link_destroy=bind('cuLinkDestroy',[P])
    module_load=bind('cuModuleLoadData',[C.POINTER(P),P]);module_unload=bind('cuModuleUnload',[P])
    function=bind('cuModuleGetFunction',[C.POINTER(P),P,C.c_char_p]);attribute=bind('cuFuncGetAttribute',[C.POINTER(I),I,P])
    init(0);dev=I();device_get(C.byref(dev),0);ctx=P();create(C.byref(ctx),0,dev);v=I();version(C.byref(v))
    records=[]
    try:
        for label,path,names in [
            ('c09-exact',RAW/'c10-runtime-compiler-v1/exact-2.ptx',['pf_exact_reuse_cdf','pf_exact_reuse_terminal']),
            ('c09-cohort',RAW/'c10-runtime-compiler-v1/cohort-2.ptx',['pf_cohort_terminal']),
            ('c12-reference',RAW/'c12-compiler-v1/reference.ptx',['pf_predicated_cdf']),
            ('c12-candidate',RAW/'c12-compiler-v1/candidate.ptx',['pf_predicated_cdf'])]:
            ptx=path.read_bytes();buffer=C.create_string_buffer(ptx);link=P();link_create(0,None,None,C.byref(link))
            try:
                link_add(link,1,C.cast(buffer,P),len(ptx)+1,b'diagnostic.ptx',0,None,None)
                result=P();size=S();link_complete(link,C.byref(result),C.byref(size));cubin=C.string_at(result,size.value)
            finally:link_destroy(link)
            target=out/(label+'.cubin');target.write_bytes(cubin)
            resources={}
            for kind,data in [('direct_ptx',ptx),('linked_cubin',cubin)]:
                b=C.create_string_buffer(data);module=P();module_load(C.byref(module),C.cast(b,P))
                try:
                    resources[kind]={}
                    for name in names:
                        f=P();function(C.byref(f),module,name.encode());values={}
                        for key,index in [('registers',4),('local_bytes',3),('shared_bytes',1)]:
                            val=I();attribute(C.byref(val),index,f);values[key]=val.value
                        resources[kind][name]=values
                finally:module_unload(module)
            r=subprocess.run([tool,'--print-code','--print-instruction-encoding',str(target)],capture_output=True,text=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
            assert r.returncode==0,r.stderr;(out/(label+'.sass')).write_text(r.stdout,encoding='utf8')
            records.append(dict(label=label,ptx_file=str(path.relative_to(RAW)),ptx_sha256=hashlib.sha256(ptx).hexdigest(),
                cubin_sha256=hashlib.sha256(cubin).hexdigest(),cubin_bytes=len(cubin),sass_sha256=hashlib.sha256(r.stdout.encode()).hexdigest(),resources=resources,direct_and_linked_resources_equal=resources['direct_ptx']==resources['linked_cubin']))
            print(json.dumps(records[-1]),flush=True)
    finally:destroy(ctx)
    (out/'manifest.json').write_text(json.dumps(dict(cuda_driver_api_version=v.value,records=records,
        scope='Static driver-link diagnostic, no kernel execution or hardware counters. Linked/direct module resource attributes are recorded separately; code generation can differ. No claim about the exact runtime machine code.'),indent=2)+'\n')
if __name__=='__main__':main()
