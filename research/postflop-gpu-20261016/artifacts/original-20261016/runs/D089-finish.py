"""Replay final assembly proof; this is not numerical or timing qualification."""
import json,re,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();H=ROOT/'runs/D089-zero-scan-codegen';c=old.read(H/'complete.json');P=old.read(H/'protocol.json')
for p,v in c['all_artifacts'].items():old.pin(p,v['sha256'])
for p,h in P['input_sha256'].items():old.pin(p,h)
assert c['compiler_terminal'] and c['native_executions']==c['gpu_executions']==0
e=old.read(H/'build/rustc.exit.json');assert e['returncode']==0 and e['error'] is e['cleanup'] is None
src=next(Path(p) for p in c['assembly_files'] if '.solver-e2d3113d740308c1.' in p);text=src.read_text();symbol='_RNvMNtNtCsifJ2Jc9XidW_6solver3gpu5arenaNtB2_11ArenaLayout6upload';start=text.index(symbol+':');end=text.index('.seh_endproc',start);body=text[start:end]
(H/'ArenaLayout-upload.asm.txt').write_text(body,encoding='utf-8',newline='\n');assert '%ymm' not in body
loops=[]
for label in [41,49,62,70]:
 name='.LBB140_'+str(label);m=re.search(re.escape(name)+r':\n(.*?)(?=^\.LBB)',body,re.M|re.S);assert m
 code=m.group(1);assert len(re.findall(r'^\s*movdqu\s',code,re.M))==2 and len(re.findall(r'^\s*por\s',code,re.M))>=2 and 'addq\t$16' in code and 'jne\t'+name in code
 loops.append({'label':name,'quant_words_per_iteration':16,'load_bytes_per_iteration':32,'independent128bit_ORaccumulators':2,'assembly':code})
old.save(H/'assembly-review.json',{'at':old.now(),'status':'verified_final128bit_zero_OR_code','compiler_terminal':True,'outer_exec_session_id':27425,'outer_exec_chunk_id':'b8adf0','source_sha256':old.BASE,'assembly_path':str(src),'assembly_sha256':old.sha(src),'upload_function_sha256':old.sha(H/'ArenaLayout-upload.asm.txt'),'upload_function_lines':len(body.splitlines()),'four_q_scan_vector_loops':loops,'vector256register_references':0,'scalar_scale_checks_retained':all('cmpl\t$0' in re.search(re.escape('.LBB140_'+str(n))+r':\n(.*?)(?=^\.LBB)',body,re.M|re.S).group(1) for n in [4,10,13,17]),'native_executions':0,'gpu_executions':0,'optimization_accepted':False,'scope':'Final ThinLTO code from exact accepted E051 solver RLIB and unmodified evaluator. New analysis executable was not run and is not asserted byte-identical to timed E051binary. Baseline qscan is already vectorized; no scalar-to-SIMD claim.'})
published={}
for src in H.rglob('*'):
 if not src.is_file() or src.suffix in ['.exe','.pdb','.obj','.lib','.exp'] or '__pycache__' in src.parts:continue
 key=H.name+'/'+src.relative_to(H).as_posix();dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes()
 if dst.exists():assert dst.read_bytes()==data,key
 else:dst.write_bytes(data)
 assert urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=20).read()==data;published[key]=old.sha(src)
old.save(H/'publication.json',{'at':old.now(),'http_byte_verified_files':len(published),'artifact_sha256':published})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(x for x in s['experiments'] if x['id']=='D089');e.update(status='measured',stage='Final codegen verified: existing128bit q scans',accepted=False,reason='Four final qscan loops each use2x128bitloads,2ORaccumulators and16u16words/iteration. No256bitregisters in upload function. Compile-only evidence; no native or speed result.');e['evidence'] +=[{'label':'D089 final machine-code review','url':'evidence/D089-zero-scan-codegen/assembly-review.json'},{'label':'D089 full final upload function assembly','url':'evidence/D089-zero-scan-codegen/ArenaLayout-upload.asm.txt'}];s.update(updated_at=old.now(),stage='D089 verified; consider guarded wide serial probe',activity='Baseline is already128bitSIMD. No parallel/metadata/encoder variant reopened; any wide serial prototype must prove exactness and representative benefit first.',active_experiment=None);old.ar.atomic_json(old.ar.STATUS,s)
print(json.dumps({'status':'verified_final128bit_zero_OR_code','loops':4,'published':len(published),'report_sha256':old.sha(H/'assembly-review.json')}),flush=True)
