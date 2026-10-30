"""Root file-only raw decoder/cross-check; no native work or timing inference."""
import json,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'small-gain-confirmation-plan'));import common as old
P=old.read(HERE/'protocol.json');ROOT=Path(P['output_dir']);S=old.read(ROOT/'evidence.json')
C=old.read(old.ROOT/'runs/E041-control-execution/complete.json');assert C['unit_passed']==86 and C['gpu_selected_passed']==1
OUT=old.ROOT/'comparisons/E041-zero-restore-control';assert not OUT.exists();OUT.mkdir()
checks=0
def require(value,message):
 global checks
 assert value,message
 checks+=1
def decode_host(raw):
 require(raw[:9]==b'E041HOST1','host magic');off=9
 iteration,=struct.unpack_from('<Q',raw,off);off+=8
 iso=raw[off];off+=1;arrays=[]
 for _ in range(4):
  kind,n=struct.unpack_from('<IQ',raw,off);off+=12
  require(kind in [0,1,2] and n>0,'store geometry')
  width=4 if kind==0 else 2
  data=raw[off:off+n*width];off+=n*width
  require(len(data)==n*width,'complete raw arena')
  scale=b''
  if kind:
   ns,=struct.unpack_from('<Q',raw,off);off+=8
   scale=raw[off:off+ns*4];off+=ns*4
   require(len(scale)==ns*4 and ns>0,'complete scales')
  arrays.append((kind,n,data,scale))
 require(off==len(raw),'host exact endpoint');return iteration,iso,arrays
def decode_gpu(raw):
 require(raw[:8]==b'E041GPU1','GPU magic');off=8;arrays=[]
 for _ in range(4):
  n,=struct.unpack_from('<Q',raw,off);off+=8
  data=raw[off:off+n*4];off+=n*4
  require(n>0 and len(data)==n*4,'complete GPU arena');arrays.append((n,data))
 require(off==len(raw),'GPU exact endpoint');return arrays

