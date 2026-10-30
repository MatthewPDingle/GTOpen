import sys, struct, itertools, math
from pathlib import Path
import numpy as np
H = Path(__file__).resolve().parent
ROOT = H.parent.parent
sys.path.insert(0, str(ROOT/'epoch'))
import common as h
P = h.read(H/'protocol.json')
for p, digest in P['input_sha256'].items(): h.pin(p,digest)
O = H/'output'
M = h.read(O/'metadata.json')
checks = words = frames = logicalwords = physicalwords = 0
def req(value,label):
    global checks
    assert value, label
    checks += 1
def eq(a,b): return a.shape == b.shape and bool(np.array_equal(a,b))
def frame(path, magic):
    global frames, words
    data = path.read_bytes()
    req(data[:16] == magic, 'frame magic')
    at, fields = 16, {}
    while at < len(data):
        kind, n = struct.unpack_from('<II', data, at); at += 8
        name = data[at:at+n].decode(); at += n
        count = struct.unpack_from('<Q', data, at)[0]; at += 8
        req(name not in fields, 'unique field')
        if kind == 0:
            req(struct.unpack_from('<I', data, at)[0] == 0, 'every represented positive zero'); at += 4
            values = np.zeros(count, dtype='<u4')
        else:
            req(kind in [1,2], 'field kind')
            values = np.frombuffer(data, dtype='<u4', count=count, offset=at); at += count*4
            if kind == 1:
                actual = np.frombuffer(data, dtype='<u4', count=count, offset=at); at += count*4
                req(eq(actual,values), 'all actual vs CPU reference words')
        fields[name] = values
        words += count
    req(at == len(data), 'full frame decoded')
    frames += 1
    return fields
inventory = h.read(ROOT/'runs/D176-cache-engine-control/source-review.json')['device_field_inventory']
gpunames = set(inventory) | {'iteration','algorithm','hands','CFV_logical'}
pattern = np.array([0x7fc01234,0x7f801234,0x7f800000,0xff800000,0xdeadc0de,0xffffffff,0,0x80000000,1,0x80000001,0x3f800000,0xbf800000,0x4b123456,0x00800000,0x7f7fffff,0xff7fffff], dtype='<u4')
gpu_magic = b'D150-GPU-RAW1\0\0\0'
def gpu(path,info):
    global physicalwords, logicalwords
    f = frame(path,gpu_magic)
    req(set(f) == gpunames and len(f) == 70, 'complete actual device inventory')
    physical, logical = f['d_cfv'], f['CFV_logical']
    rows, stride, nh = info['rows'],info['stride'],info['logical_hands']
    req(len(physical) == info['physical_words'] == rows*stride and len(logical) == rows*nh and 0 < nh <= stride, 'full scratch geometry')
    req(eq(physical.reshape(rows,stride)[:,:nh].reshape(-1), logical), 'all logical CFV rows map to retained physical words')
    req(f['hands'][info['logical_player']] == nh, 'logical current player hand count')
    req(int(f['algorithm'][0]) == expected_algo, 'actual algorithm matches declared fixture before and after resume')
    req(requested_iso or not info['actual_iso_active'], 'declared noiso remains actual noiso')
    logicalwords += len(logical); physicalwords += len(physical)
    return f
expected = list(itertools.product(['Compressed','F32'], ['Dcfr','CfrPlus'], [False,True],[False,True],[False,True]))
expected += [('Compressed', algo, False, iso, False) for board in ['Ks7s2d','Ks7s2dQhTc'] for algo,iso in [('Dcfr',False),('CfrPlus',True)]]
expected += list(itertools.product(['Compressed','F32'], ['Dcfr','CfrPlus'], [False,True],[False,True],[False,True]))
ordinary = ['train-first','train-capture','train-replay','strategy-sync','eval-eager','eval-capture','eval-replay','full-sync','train-after-sync','locked-train','locked-eval-eager','locked-eval-capture','unlocked-train','unlocked-eval','before-save','resumed-train','resumed-eval-eager','resumed-eval-capture','resumed-eval-replay','resumed-full-sync']
scratchdiff = {'strategy-sync','full-sync','before-save','resumed-full-sync'}
epoch = phases = roots = evs = changedwords = regenerated = intentionally_retained = 0
req(len(M['cases']) == 68 and not M['performance_measurement'] and not M['packing_implementation_created'], 'fixed native matrix')
for ident, (row, dims) in enumerate(zip(M['cases'], expected)):
    req(row['case'] == ident and row['resume_fixture_flags_explicitly_restored'], 'case order and explicit resume fixture controls')
    req((row['storage'],row['algorithm'],row['reverse_ranges'],row['isomorphism'],row['warm_CPU_start']) == dims, 'fixed dimensions')
    req(row['extra_board'] == (None if ident < 32 or ident >= 36 else ['Ks7s2d','Ks7s2dQhTc'][(ident-32)//2]), 'fixed extra boards')
    req(row['paired_fixture'] == (ident>=36), 'original versus appended paired fixtures')
    if ident>=36: req(row['actual_hands']==([12,18] if row['reverse_ranges'] else [18,12]),'actual paired dimensions')
    expected_algo = 0 if dims[1] == 'Dcfr' else 1
    requested_iso = dims[3]
    stages = ordinary + ([f'continuation-{i}-p{p}' for i,p in enumerate([0,1,0,1])] if dims[1] == 'CfrPlus' and not dims[3] else [])
    req([x['stage'] for x in row['phases']] == [x['stage'] for x in row['clobbers']] == stages, 'complete ordered phases and clobbers')
    req(len(row['exploit_bits']) == 9, 'all EV pairs')
    req(all(math.isfinite(struct.unpack('<d',struct.pack('<Q',x))[0]) for x in row['exploit_bits']), 'finite EVs')
    evs += 9
    req(len(row['continuation_root_bits']) == len(stages)-20, 'all continuation roots')
    for values in row['continuation_root_bits']:
        req(all(math.isfinite(struct.unpack('<f',struct.pack('<I',x))[0]) for x in values), 'finite continuation roots')
        roots += 1
    for phase, witness in zip(row['phases'],row['clobbers']):
        stage, proof = phase['stage'], witness['proof']
        epoch += 1
        req(proof['epoch'] == epoch and proof['rotation'] == epoch%16 and proof['pattern'] == pattern.tolist(), 'fixed clobber seed')
        info = proof['info']
        before = gpu(O/f'clobber-{ident:02}-{stage}-before.gpu.bin', info)
        after = gpu(O/f'clobber-{ident:02}-{stage}-after.gpu.bin', info)
        seeded = np.resize(np.roll(pattern,-epoch%16), len(after['d_cfv']))
        req(eq(after['d_cfv'],seeded), 'every physical CFV word replaced by exact rotated seed')
        changed = int(np.count_nonzero(before['d_cfv'] != after['d_cfv']))
        req(changed > 0 and changed == proof['changed_words'] and len(seeded) == proof['words'], 'complete actual changed-word count')
        changedwords += changed
        for name in gpunames - {'d_cfv','CFV_logical'}:
            req(eq(before[name],after[name]), 'clobber leaves every other field exact '+name)
        del before, after, seeded
        info = phase['info']
        b = gpu(O/f'baseline-{ident:02}-{stage}.gpu.bin',info)
        c = gpu(O/f'clobbered-{ident:02}-{stage}.gpu.bin',info)
        regen = stage not in scratchdiff
        req(phase['CFV_regenerated'] == regen, 'declared regeneration contract')
        for name in gpunames - {'d_cfv'}:
            if name == 'CFV_logical' and not regen: continue
            req(eq(b[name],c[name]), 'every phase field/logical CFV exact '+name)
        regenerated += regen; intentionally_retained += not regen
        phases += 1
        del b,c
    print('D150 raw reader case',ident,'complete',flush=True)
pairs = constructors = cpu = 0
for p in sorted(O.glob('baseline-*')):
    if p.name.endswith('.gpu.bin'): continue
    q = O/p.name.replace('baseline-','clobbered-',1)
    req(p.read_bytes() == q.read_bytes(), 'whole CPU/query/save/constructor files')
    pairs += 1
    if p.name.endswith('-constructor.bin'):
        a = frame(p,b'D150-FRAME-v1\0\0\0'); b = frame(q,b'D150-FRAME-v1\0\0\0')
        req(set(a) == set(b) and len(a) == 66 and all(eq(a[k],b[k]) for k in a), 'all66 complete constructor fields')
        constructors += 1
    elif p.name.endswith('.cpu.bin'):
        a = frame(p,b'D150-STATE-v1\0\0\0'); b = frame(q,b'D150-STATE-v1\0\0\0')
        req(set(a) == set(b) and all(eq(a[k],b[k]) for k in a), 'every CPU store scale and state word')
        cpu += 1
req(constructors == 68 and evs == 612 and roots == 64 and phases == epoch == 1424 and regenerated == 1152 and intentionally_retained == 272, 'complete native raw inventory')
req(M['clobbers'] == M['phase_pairs'] == 1424 and M['constructor_pairs'] == 68 and M['exploitability_pairs'] == 612 and M['continuation_root_pairs'] == 64, 'native metadata inventory')

logs=(H/'execution/probe.stdout.log').read_text();binds=[__import__('json').loads(x.split('D185_PAIR_BIND ',1)[1]) for x in logs.splitlines() if 'D185_PAIR_BIND ' in x];ptx=[__import__('json').loads(x.split('D185_PTX_BIND ',1)[1]) for x in logs.splitlines() if 'D185_PTX_BIND ' in x];req(len(binds)==272 and len(ptx)==272,'all constructor binding markers');req(sum(x['paired'] for x in binds)==64,'64 actual paired constructors');req(sum(x['arm']==0 for x in binds)==sum(x['arm']==1 for x in binds)==136,'per-arm constructor count')
for x in binds:
    want=x['arm']==1 and all(n>0 and n%2==0 for n in x['hands']);req(x['paired']==want and x['down_name']==('down_action_pair2' if want else 'down_action') and x['up_name']==('up_action_pair2' if want else 'up_action'),'literal kernel binding selection')

h.custody()
D = ROOT/'comparisons/D185-paired-engine-controls'
D.mkdir(exist_ok=False)
report = {'id':'D185', 'at':h.now(), 'status':'pass_scoped_paired_action_engine_raw_lifecycle_equivalence', 'protocol_sha256':h.sha(H/'protocol.json'), 'binary_sha256':h.sha(H/'probe.exe'), 'cases':68, 'constructor_pairs':constructors, 'phase_pairs':phases, 'CFV_clobbers':epoch, 'fully_regenerated_logical_CFV_pairs':regenerated, 'CFV_intentionally_retained_readback_pairs':intentionally_retained, 'exploitability_pairs':evs, 'continuation_root_pairs':roots, 'full_CPU_query_save_constructor_file_pairs':pairs, 'CPU_frames_pairs':cpu, 'raw_frames':frames, 'represented_raw_words':words, 'logical_CFV_words_checked':logicalwords, 'physical_CFV_words_retained_and_checked':physicalwords, 'actual_changed_CFV_words':changedwords, 'reader_checks':checks, 'all65_other_device_arrays_and_host_scalars_exact':True, 'all_CPU_q_scales_queries_saves_resume_exact':True, 'all66_constructor_images_match_CPU_reference':True, 'source_main_live_PTX_custody_pass':True, 'performance_measurement':False, 'candidate_accepted':False, 'packing_implementation_created':False, 'scope':'Finite68case ordinary/graph/locked/save/resume matrix plus64 plain changing-range CfrPlus continuation sweeps. Every actual device field retained; all physical seed words checked, all65 other arrays exact, and all current-player logical CFV words exact only after regeneration. Scratch/padding physical equality between arms is not claimed. The two instances use sealedoriginal/paired-actionPTX;original action and2newpaired entry bindings are exercised in unchanged ordinary/graph/eval/lock/save/resume/plain-continuation workflows; not every module entry is claimed dynamically executed. Actual paged/stored wrappers,canonical large cases,all generic menus,large canonical verification,capacity/material and speed remain unproven.'}
h.save(D/'report.json',report)
print({k:report[k] for k in ['status','cases','phase_pairs','raw_frames','reader_checks']},flush=True)
