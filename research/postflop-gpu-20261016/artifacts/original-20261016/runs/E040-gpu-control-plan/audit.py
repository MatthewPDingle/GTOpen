"""Root file-only raw decoder/cross-check; no native work or timing inference."""
import json,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'small-gain-confirmation-plan'));import common as old
P=old.read(HERE/'protocol.json');ROOT=Path(P['output_dir']);S=old.read(ROOT/'evidence.json')
OUT=old.ROOT/'comparisons/E040-gpu-readback-control';assert not OUT.exists();OUT.mkdir()
checks=0
def require(value,message):
 global checks
 assert value,message
 checks+=1
def decode_host(raw):
 require(raw[:9]==b'E040HOST1','host magic');off=9
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
 require(raw[:8]==b'E040GPU1','GPU magic');off=8;arrays=[]
 for _ in range(4):
  n,=struct.unpack_from('<Q',raw,off);off+=8
  data=raw[off:off+n*4];off+=n*4
  require(n>0 and len(data)==n*4,'complete GPU arena');arrays.append((n,data))
 require(off==len(raw),'GPU exact endpoint');return arrays

inventory={};cases=[]
for index,name in enumerate(P['cases']):
 d=ROOT/name;c=S['cases'][index]
 require(c['compact']==(index%2==1),'layout')
 expected_files={v['file']:v['bytes'] for v in c['files']}
 require(set(p.name for p in d.iterdir())==set(expected_files),'native file inventory')
 pair_count=0
 for n,size in expected_files.items():
  p=d/n;raw=p.read_bytes();require(len(raw)==size,'raw byte count');inventory[str(p)]=old.sha(p)
  if n.endswith('.reference.bin') or n.endswith('.reference.save'):
   other=d/n.replace('.reference.','.candidate.')
   require(raw==other.read_bytes(),'full byte equality '+n);pair_count+=1
  if n.endswith('.host.bin') or '.host.' in n:
   decode_host(raw)
  if n.endswith('.gpu.bin'):decode_gpu(raw)
 poisoned=(d/'poisoned.host.bin').read_bytes();first=(d/'first.host.reference.bin').read_bytes()
 it,iso,arrays=decode_host(first)
 require(it==4 and iso==index%2,'iteration/isomorphism')
 require([a[0] for a in arrays]==([1,1,2,2] if index<2 else [0,0,0,0]),'store variants')
 require(first!=(d/'input.host.bin').read_bytes() and first!=poisoned,'real changed learning state')
 trained=(d/'trained.gpu.bin').read_bytes();g=decode_gpu(trained)
 require([v[0] for v in g]==c['device_elements'],'GPU arena inventory')
 require((d/'final.gpu.bin').read_bytes()==trained,'all GPU learning words unchanged')
 for label in ['repeat','default']+(['mixed'] if index<2 else []):
  require((d/f'{label}.host.candidate.bin').read_bytes()==first,label+' exact first restore')
 materialized=(d/'materialized.host.candidate.bin').read_bytes()
 require((materialized!=first)==c['compact'],'symmetry materialization observation')
 if index<2:
  require(c['forced_pipelined_arenas']==4 and c['mixed_pipelined_arenas']==2,'forced/mixed helper execution')
  for ordinal in [1,2]:
   require((d/f'fault{ordinal}.host.candidate.bin').read_bytes()==poisoned,'pre-encoding fault target untouched')
   require((d/f'fault{ordinal}.gpu.bin').read_bytes()==trained,'fault GPU state unchanged')
   require((d/f'fault{ordinal}.reused.host.candidate.bin').read_bytes()==first,'exact reuse after fault')
 require(c['default_pipelined_arenas']==0,'tiny default falls back')
 cases.append({'name':name,'raw_pairs':pair_count,'raw_files':len(expected_files),'bytes':sum(expected_files.values()),'forced_pipelined_arenas':c['forced_pipelined_arenas'],'faults':len(c['faults'])})
old.custody()
report={'id':'E040-gpu-readback-control','at':old.now(),'status':'pass_scoped_gpu_readback_and_drain_control','root_cross_check_only':True,'checks':checks,'cases':cases,'raw_pairs':sum(v['raw_pairs'] for v in cases),'raw_files':sum(v['raw_files'] for v in cases),'protocol_sha256':old.sha(HERE/'protocol.json'),'audit_script_sha256':old.sha(HERE/'audit.py'),'native_complete_sha256':old.sha(old.ROOT/'runs/E040-gpu-control-execution/complete.json'),'raw_summary_sha256':old.sha(ROOT/'evidence.json'),'raw_file_sha256':inventory,'accepted162_restored':True,'main_live_ptx_unchanged':True,'performance_measured':False,'candidate_accepted':False,'limits':'Scoped deterministic small full/compact fixtures and forced policy; injected Err/unwind confirms drain path and stream readiness. This is not a measured overlap duration, general CUDA failure proof, speedup, statistical result or adoption decision.'}
old.save(OUT/'report.json',report);print(json.dumps({k:report[k] for k in ['status','checks','raw_pairs','raw_files']}));print(old.sha(OUT/'report.json'))
