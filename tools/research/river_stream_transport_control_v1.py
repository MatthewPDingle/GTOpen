"""Exact stdin/stdout replay and compact target evidence on qualified cases."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import hashlib,json,subprocess,sys,time,traceback
from pathlib import Path
import numpy as np
import psutil
from river_training_overlay_targets_stream_v1 import generate
from river_policy_batch_v1 import CPUCurrentPolicy
from weighted_deal_binding_v1 import DealWeightGeneration
from board_training_checkpoint_v1 import model_document
from preflop_allin_matrix_v1 import AllinMatrix
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import PAIRS
from bounded_parallel_evaluation_archive_v2 import production_available

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='river-stream-transport-control-v1';STORE=OUT/NAME
REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json');FAILURE=OUT/(NAME+'-failure.json')
CONTEXT=OUT/'bb-context-candidate.json';PLAN=OUT/'RIVER-STREAM-TRANSPORT-PLAN.md';LIMIT=8_000_000
EXE=ROOT/'target/release/examples/hu_river_two_stage_stream_v1.exe'
BAD=['unknown-mode','history-selection','missing-selection','empty-selection','oversized-selection','duplicate-pair','unsorted-pairs','blocked-pair','repeated-card','invalid-card','duplicate-target']

def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bytes_under(p):return sum(f.stat().st_size for f in p.rglob('*') if f.is_file())
def save(p,x):
    raw=(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode();assert bytes_under(STORE)+len(raw)<LIMIT
    with Path(p).open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
def guard():
    assert production_available() and psutil.virtual_memory().available>24_000_000_000
    assert psutil.Process().memory_info().rss<16_000_000_000 and bytes_under(STORE)<LIMIT
def verify(inputs):
    for p,h in inputs.items():assert sha(p)==h,p

def main():
    assert not any(p.exists() for p in (STORE,REG,RESULT,FAILURE));STORE.mkdir();start=time.monotonic();guard()
    prior_name='river-weighted-overlay-control-v2';prior=OUT/prior_name
    rp=OUT/(prior_name+'-registration.json');ep=OUT/(prior_name+'-result.json');reg=read(rp);result=read(ep)
    assert result['passed'] and result['registration_sha256']==sha(rp)
    inputs=dict(reg['inputs']);paths=[Path(__file__),PLAN,EXE,ROOT/'crates/solver/examples/hu_river_two_stage_stream_v1.rs',rp,ep,prior/'source-generation.json']
    assert sha(prior/'source-generation.json')==result['source_generation_sha256']
    for case in result['cases']:
        assert read(prior/case['case']/'result.json')==case
        for name,h in case['artifacts'].items():
            p=prior/case['case']/name;assert sha(p)==h;paths.append(p)
    badroot=OUT/'river-posterior64-native-control-v1'
    paths.extend(badroot/('bad-'+n+'.json') for n in BAD)
    for module in list(sys.modules.values()):
        p=getattr(module,'__file__',None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix=='.py':paths.append(Path(p))
    inputs.update({str(p):sha(p) for p in paths});verify(inputs)
    save(REG,dict(format=1,inputs=inputs,cases=[c['case'] for c in result['cases']],maximum_seconds=180,maximum_bytes=LIMIT,gpu_used=False,training=False))
    try:
        source=CONTEXT.read_text();cp=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json');mp=OUT/'preflop-allin-matrix-control-v1-matrix.json'
        weights=PhysicalDeals(source,mode='full_deck',seed=0).weights;entry=[{tuple(map(int,p)):float(w) for p,w in zip(PAIRS,r)} for r in weights]
        generation=DealWeightGeneration(read(prior/'source-generation.json'),source);mass=AllinMatrix(read(mp),source).btn_mass;engines={}
        for b in reg['policies']:
            args=dict(catalog_source=cp.read_text(),matrix_sha256=sha(mp),entry_mass=mass,root_config=b['root_config'])
            model=model_document(b['folder'],b['reference'],context_source=source,**args);engines[b['policy_id']]=CPUCurrentPolicy(model,source,**args)
        reports=[]
        for case in result['cases']:
            guard();original=prior/case['case'];old=original/'conditional';folder=STORE/case['case'];folder.mkdir()
            original_overlay=read(old/'overlay.json');original_evidence=read(old/'evidence.json');identity=original_evidence['policy_id'];began=time.perf_counter()
            overlay,evidence=generate(read(original/'queries.json'),read(original/'updates.json'),read(original/'policies.json'),read(original/'trace.json'),
                generation=generation,start=case['source_offset'],iteration=78,policy_id=identity,case_id=original_evidence['case_id'],engine=engines[identity],entry=entry,
                executable=EXE,context_path=CONTEXT,folder=folder/'conditional',guard=guard,write=save)
            generation_seconds=time.perf_counter()-began
            for key in ('format','method','K','binding','rows'):assert overlay[key]==original_overlay[key],key
            replay=[];new=folder/'conditional'
            for request in sorted(new.glob('*-request.json')):
                name=request.name.removesuffix('-request.json');expected=old/(name+'-export.json')
                log=read(new/(name+'-process.json'));raw=expected.read_bytes()
                assert request.read_bytes()==(old/request.name).read_bytes()
                assert log['stdout_sha256']==sha(expected) and log['stdout_bytes']==len(raw)
                # Independent native replay also compares literal bytes and decoded structure.
                process=subprocess.run([str(EXE),str(CONTEXT)],input=request.read_bytes(),capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
                assert process.returncode==0 and process.stdout==raw and json.loads(process.stdout)==json.loads(raw)
                replay.append(dict(request=request.name,output_bytes=len(raw),output_sha256=sha(expected),byte_identical=True,decoded_structure_identical=True))
            for path in new.glob('*-policies.npz'):
                with np.load(path,allow_pickle=False) as a,np.load(old/path.name,allow_pickle=False) as b:
                    assert set(a.files)==set(b.files)
                    for key in a.files:assert np.array_equal(a[key],b[key])
            assert not list(new.glob('*-export.json'))
            report=dict(case=case['case'],river_rows=len(overlay['rows']),identical_rows_and_policies=True,native_outputs=replay,
                        old_conditional_bytes=bytes_under(old),new_conditional_bytes=bytes_under(new),generation_seconds=generation_seconds,
                        artifacts={str(p.relative_to(folder)):sha(p) for p in folder.rglob('*') if p.is_file()})
            save(folder/'result.json',report);reports.append(report)
            print(json.dumps(dict(case=case['case'],stored_bytes=report['new_conditional_bytes'])),flush=True)
            assert time.monotonic()-start<180
        negatives=[]
        cases=[(name,(badroot/('bad-'+name+'.json')).read_bytes(),[]) for name in BAD]
        cases.extend([('empty-input',b'',[]),('oversized-input',b' '*65537,[]),('wrong-argc',b'', ['unexpected'])])
        for name,data,extra in cases:
            p=subprocess.run([str(EXE),str(CONTEXT),*extra],input=data,capture_output=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
            assert p.returncode!=0 and not p.stdout
            item=dict(name=name,rejected=True,stdout_bytes=0,stderr=p.stderr.decode('utf-8'),request_sha256=hashlib.sha256(data).hexdigest())
            save(STORE/('bad-'+name+'.json'),item);negatives.append(name)
        verify(inputs);guard();oldbytes=sum(c['old_conditional_bytes'] for c in reports);newbytes=sum(c['new_conditional_bytes'] for c in reports)
        save(RESULT,dict(passed=True,complete=True,registration_sha256=sha(REG),cases=reports,negative_controls=negatives,
            old_conditional_bytes=oldbytes,new_conditional_bytes=newbytes,retained_fraction=newbytes/oldbytes,
            seconds=time.monotonic()-start,retained_bytes_before_result=bytes_under(STORE),gpu_used=False,training=False,production_modified=False,
            scope='Byte-identical memory transport and unchanged target/policy evidence on qualified training slices; no quality or end-to-end training speed claim.'))
        print(json.dumps(dict(passed=True,retained_fraction=newbytes/oldbytes,seconds=time.monotonic()-start)),flush=True)
    except Exception as e:save(FAILURE,dict(error=repr(e),traceback=traceback.format_exc(),seconds=time.monotonic()-start));raise

if __name__=='__main__':main()
