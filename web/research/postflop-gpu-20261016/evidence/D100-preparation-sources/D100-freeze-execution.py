"""Normalize undefined CUPTI configuration fields before any compiler/native run."""
import ast,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();H=ROOT/'runs/D100-show-cache-configuration';assert not (H/'build').exists() and not (H/'execution').exists()
P=old.read(H/'protocol.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
s=(H/'collector.cpp').read_text(encoding='utf-8')
needle='row.detail=uint32_t(a->cacheConfig.both)|(uint32_t(a->isSharedMemoryCarveoutRequested)<<8)|(uint32_t(a->sharedMemoryCarveoutRequested)<<16);row.bytes=a->sharedMemoryExecuted;';assert s.count(needle)==1
s=s.replace(needle,'const bool carve=a->isSharedMemoryCarveoutRequested!=0;\n            row.detail=uint32_t(carve?0:a->cacheConfig.both)|(uint32_t(carve)<<8)|(uint32_t(carve?a->sharedMemoryCarveoutRequested:0)<<16);row.bytes=a->sharedMemoryExecuted;')
(H/'collector-r2.cpp').write_text(s,encoding='utf-8',newline='\n');ast.parse((H/'execute.py').read_text(encoding='utf-8'))
P.update(at=old.now(),original_protocol_sha256=old.sha(H/'protocol.json'),preparation_revision='Static SDK review: cacheConfignot updated with explicit carveout, and requestpercentonly valid with flag. Normalize invalid cache/request fields to0; retain original collector/protocol before any native outcome. Cache hint/kernel/geometry/resource/raw/decision rules unchanged.')
P['collector_command']=P['collector_command'].replace(str(H/'collector.cpp'),str(H/'collector-r2.cpp'))
P['trace_schema']['kernel_detail']+='; cachebyte normalized0when carveoutflag1, requestpercentnormalized0when flag0'
for p in [H/'collector-r2.cpp',H/'execute.py',H/'protocol.json',Path(__file__)]:P['input_sha256'][str(p)]=old.sha(p)
old.save(H/'protocol-r2.json',P);old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'protocol-r2.json'),'compiler_runs':0,'native_runs':0}),flush=True)
