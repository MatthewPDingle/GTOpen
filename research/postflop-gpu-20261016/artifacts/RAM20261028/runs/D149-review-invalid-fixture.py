import sys, struct, json, itertools
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
H = ROOT/'runs/D149-CFV-liveness'
O = H/'output'
P = h.read(H/'protocol.json')
for p,digest in P['input_sha256'].items(): h.pin(p,digest)
h.custody()
assert h.read(H/'execution/rustc.exit.json')['returncode'] == 0
assert h.read(H/'execution/probe.exit.json')['returncode'] == 101
assert not (H/'execution/audit.exit.json').exists() and not (O/'metadata.json').exists()
err = (H/'execution/probe.stderr.log').read_text(encoding='utf-8')
assert 'research continuation requires p=0/1, t>0, CFR+ and no isomorphism' in err
checks = frames = words = changed = 0
def req(x,s):
    global checks
    assert x,s
    checks += 1
def frame(p):
    global frames, words
    raw = p.read_bytes()
    req(raw[:16] in [b'D149-GPU-RAW1\0\0\0',b'D149-FRAME-v1\0\0\0',b'D149-STATE-v1\0\0\0'],'magic')
    at = 16; out = {}
    while at < len(raw):
        kind,n = struct.unpack_from('<II',raw,at); at += 8
        name=raw[at:at+n].decode(); at += n
        count=struct.unpack_from('<Q',raw,at)[0]; at += 8
        req(name not in out,'unique field')
        if kind == 0:
            req(struct.unpack_from('<I',raw,at)[0] == 0,'positivezero run');at += 4
            v = np.zeros(count,dtype='<u4')
        else:
            req(kind in [1,2],'kind')
            v = np.frombuffer(raw,dtype='<u4',count=count,offset=at);at += count*4
            if kind == 1:
                a=np.frombuffer(raw,dtype='<u4',count=count,offset=at);at += count*4
                req(np.array_equal(a,v),'all CPU-reference actual words')
        out[name] = v;words += count
    req(at == len(raw),'full frame');frames += 1
    return out
inventory=set(h.read(H/'source-review.json')['device_field_inventory'])|{'iteration','algorithm','hands','CFV_logical'}
def gpu(p,player):
    f=frame(p);req(set(f)==inventory and len(f)==70,'all70 fields')
    stride=int(max(f['hands']));nh=int(f['hands'][player]);phys=f['d_cfv']
    req(len(phys)%stride==0,'physical stride')
    req(np.array_equal(phys.reshape(-1,stride)[:,:nh].reshape(-1),f['CFV_logical']),'all logical physical mappings')
    return f
ordinary=['train-first','train-capture','train-replay','strategy-sync','eval-eager','eval-capture','eval-replay','full-sync','train-after-sync','locked-train','locked-eval-eager','locked-eval-capture','unlocked-train','unlocked-eval','before-save','resumed-train','resumed-eval-eager','resumed-eval-capture','resumed-eval-replay','resumed-full-sync']
skip={'strategy-sync','full-sync','before-save','resumed-full-sync'}
pattern=np.array([0x7fc01234,0x7f801234,0x7f800000,0xff800000,0xdeadc0de,0xffffffff,0,0x80000000,1,0x80000001,0x3f800000,0xbf800000,0x4b123456,0x00800000,0x7f7fffff,0xff7fffff],dtype='<u4')
epoch=paircount=0
actual_algorithms=[]
for case in range(9):
    algos=[]
    for stage in ordinary + (['continuation-0-p0'] if case==8 else []):
        epoch += 1;p=0 if stage.startswith('continuation') else 1
        before=gpu(O/f'clobber-{case:02}-{stage}-before.gpu.bin',p)
        after=gpu(O/f'clobber-{case:02}-{stage}-after.gpu.bin',p)
        req(np.array_equal(after['d_cfv'],np.resize(np.roll(pattern,-epoch%16),len(after['d_cfv']))),'all actual clobber words')
        n=int(np.count_nonzero(before['d_cfv']!=after['d_cfv']));req(n>0,'actual changed CFV');changed += n
        for name in inventory-{'d_cfv','CFV_logical'}:req(np.array_equal(before[name],after[name]),'all other fields unchanged')
        del before,after
        if stage.startswith('continuation'):
            req(not (O/f'baseline-{case:02}-{stage}.gpu.bin').exists(),'rejected request produced no phase output')
            continue
        b=gpu(O/f'baseline-{case:02}-{stage}.gpu.bin',1);c=gpu(O/f'clobbered-{case:02}-{stage}.gpu.bin',1)
        for name in inventory-{'d_cfv'}:
            if name=='CFV_logical' and stage in skip:continue
            req(np.array_equal(b[name],c[name]),'all completed phase words exact')
        algos.append({'stage':stage,'actual_algorithm':int(b['algorithm'][0])})
        paircount += 1
        del b,c
    actual_algorithms.append({'case':case,'stages':algos})
pairs=constructors=0
for p in sorted(O.glob('baseline-*')):
    if p.name.endswith('.gpu.bin'):continue
    q=O/p.name.replace('baseline-','clobbered-',1)
    req(p.read_bytes()==q.read_bytes(),'full retained CPU/query/save/constructor pair')
    if p.suffix=='.bin':
        a,b=frame(p),frame(q)
        req(set(a)==set(b) and all(np.array_equal(a[k],b[k]) for k in a),'all retained frame words exact')
        if p.name.endswith('-constructor.bin'):req(len(a)==66,'all66 constructor buffers');constructors += 1
    pairs += 1
assert paircount==180 and epoch==181 and constructors==9 and frames==848
assert actual_algorithms[8]['stages'][0]['actual_algorithm']==1
assert actual_algorithms[8]['stages'][15]['actual_algorithm']==0
D=ROOT/'comparisons/D149-invalid-fixture'
D.mkdir(exist_ok=False)
report={'id':'D149','at':h.now(),'status':'invalid_control_fixture_stopped_not_passed','protocol_sha256':h.sha(H/'protocol.json'),'original_protocol_and_all_source_unchanged':True,'rustc_exit':0,'native_exit':101,'expected36case_metadata_absent':True,'complete_case_events_before_stop':8,'completed_ordinary_phase_pairs_retained':paircount,'CFV_clobbers_retained':epoch,'constructor_pairs_retained':constructors,'CPU_query_save_constructor_file_pairs_retained':pairs,'raw_frames':frames,'represented_words':words,'raw_reader_checks':checks,'actual_changed_CFV_words':changed,'actual_algorithms_by_stage':actual_algorithms,'failure_cause':'Fixture assumed save/load preserved experimental algorithm and use_isomorphism. Actual load uses Solver::with_storage defaults Dcfr and true, and does not restore either flag. At case8 after resume the first intended plain CfrPlus/noiso continuation request is rejected by the original pre-launch guard. No continuation sweep is executed for that request. Both arms match in completed observations; intended36case coverage did not complete.','safety_gate_passed':False,'optimization_or_speed_candidate_existed':False,'source_main_live_PTX_custody_pass':True,'all_owned_children_terminal':True,'packing_implementation_created':False,'scope':'Independent retained-only partial raw reader; not the original frozen full-cohort audit, no sampling extension, performance score or positive full-cohort decision. All original files, exit101 and closed invalid status retained.'}
h.save(D/'report.json',report)
refs=[h.REPO/'crates/solver/src/save.rs',h.REPO/'crates/solver/src/cfr.rs',h.REPO/'crates/solver/src/gpu/mod.rs',Path(__file__),D/'report.json']
h.save(D/'fixture-repair-review.json',{'at':h.now(),'status':'prospective_new_correctness_cohort_only','D149_remains_closed_invalid':True,'evidence_sha256':{str(p):h.sha(p) for p in refs},'interpretation':'The rejection is a test-fixture setup defect, not a failed equivalence assertion or failed performance screen. The no-variant rule continues to prohibit changing production/numerical source, shader, gates or case matrix to rescue a scientific failure. A separately named full correctness cohort may explicitly restore the originally declared algorithm/iso fixture flags after load. Preserve D149 and never relabel its partial output as a pass; do not pool it. No optimization candidate exists to rescue.','bounded_repair':'Keep accepted application source exact, all36 cases/752 clobbers and all original word-level gates. Only set the two fixture controls on both loaded CPU solvers before GPU construction, and assert defaults/actual configured algorithm and noiso state. Add metadata for that setup. New native cohort remains correctness only, with no timing result.'})
print(json.dumps({'D149_status':report['status'],'partial_phase_pairs':paircount,'raw_frames':frames,'reader_checks':checks}),flush=True)
