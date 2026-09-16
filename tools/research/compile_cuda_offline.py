"""Compile research CUDA source with NVRTC without creating a GPU context."""
import ctypes as c
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]


def compile_source(source,output):
    source=Path(source).resolve();output=Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
    directory=ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin'
    os.environ['PATH']=str(directory)+os.pathsep+os.environ.get('PATH','')
    with os.add_dll_directory(str(directory)):
        library=c.CDLL(str(directory/'nvrtc64_120_0.dll'))
        signatures={
            'nvrtcVersion':[c.POINTER(c.c_int),c.POINTER(c.c_int)],
            'nvrtcCreateProgram':[c.POINTER(c.c_void_p),c.c_char_p,c.c_char_p,c.c_int,c.POINTER(c.c_char_p),c.POINTER(c.c_char_p)],
            'nvrtcCompileProgram':[c.c_void_p,c.c_int,c.POINTER(c.c_char_p)],
            'nvrtcGetProgramLogSize':[c.c_void_p,c.POINTER(c.c_size_t)],
            'nvrtcGetProgramLog':[c.c_void_p,c.c_char_p],
            'nvrtcGetPTXSize':[c.c_void_p,c.POINTER(c.c_size_t)],
            'nvrtcGetPTX':[c.c_void_p,c.c_char_p],
            'nvrtcDestroyProgram':[c.POINTER(c.c_void_p)],
        }
        for name,args in signatures.items():
            function=getattr(library,name);function.argtypes=args;function.restype=c.c_int
        major=c.c_int();minor=c.c_int();assert library.nvrtcVersion(c.byref(major),c.byref(minor))==0
        program=c.c_void_p();contents=source.read_bytes()
        assert library.nvrtcCreateProgram(c.byref(program),contents,source.name.encode(),0,None,None)==0
        try:
            options=[b'--gpu-architecture=compute_86']
            code=library.nvrtcCompileProgram(program,len(options),(c.c_char_p*len(options))(*options))
            size=c.c_size_t();assert library.nvrtcGetProgramLogSize(program,c.byref(size))==0
            log=c.create_string_buffer(size.value);assert library.nvrtcGetProgramLog(program,log)==0
            (output/'compile.log').write_bytes(log.value)
            record=dict(compiler=f'NVRTC {major.value}.{minor.value}',options=[v.decode() for v in options],
                source_sha256=hashlib.sha256(contents).hexdigest(),compile_exit_code=code,gpu_executed=False,
                note='Compilation only. No GPU context, kernel execution, accuracy or timing validation.')
            if code==0:
                assert library.nvrtcGetPTXSize(program,c.byref(size))==0
                ptx=c.create_string_buffer(size.value);assert library.nvrtcGetPTX(program,ptx)==0
                (output/'compiled.ptx').write_bytes(ptx.value)
                record.update(ptx_bytes=len(ptx.value),ptx_sha256=hashlib.sha256(ptx.value).hexdigest())
            (output/'compilation.json').write_bytes((json.dumps(record,indent=2)+'\n').encode())
            assert code==0,log.value.decode(errors='replace')
            print(json.dumps(record),flush=True)
            return record
        finally:
            library.nvrtcDestroyProgram(c.byref(program))


if __name__=='__main__':compile_source(sys.argv[1],sys.argv[2])
