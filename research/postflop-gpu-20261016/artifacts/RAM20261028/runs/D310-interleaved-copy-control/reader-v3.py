"""Independent complete typed raw-image reader; never selects or reruns native samples."""
import hashlib, json, struct, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
H = ROOT / 'runs/D310-interleaved-copy-control'
P = h.read(H / 'reader-protocol-v3.json')
assert len(sys.argv) == 2
h.pin(H / 'reader-protocol-v3.json', sys.argv[1])
for path, digest in P['input_sha256'].items():
    h.pin(path, digest)
O = H / 'execution-v2/native-output'
MASK = np.uint64(0xffffffff)
SPECIAL = np.array([0x00000000,0x80000000,0x00000001,0x80000001,0x007fffff,0x00800000,0x3f800000,0x7f7fffff,0x7f800000,0xff800000,0x7fc12345,0x7fa12345,0xffc54321], dtype=np.uint32)

def pattern(index, field, seed):
    """uint64 modular arithmetic independently maps each logical input word."""
    index = np.asarray(index, dtype=np.uint64)
    field = np.asarray(field, dtype=np.uint64)
    salt = np.uint64(seed) ^ ((field * np.uint64(0x85ebca6b)) & MASK)
    x = (index * np.uint64(0x9e3779b9) + salt) & MASK
    expected = (((x * np.uint64(128)) & MASK) | (x // np.uint64(1 << 25))) ^ np.uint64(0xa5a55a5a)
    small = index < 13
    selected = (index + field * 5 + seed % 13) % 13
    return np.where(small, SPECIAL[selected.astype(np.intp)], expected).astype(np.uint32)

def guard(index, field, right):
    return (((np.asarray(index,dtype=np.uint64) + (0x78563412 if right else 0xd34db33f)) & MASK) ^ np.uint64(field * 0x01010101)).astype(np.uint32)

def expected_words(index, kind, field, seed, logical):
    index = np.asarray(index,dtype=np.uint64)
    if kind == 0:
        return pattern(index, field, seed)
    count = (logical if kind == 1 else 2 * logical) + 128
    left, right = index < 64, index >= count - 64
    # All three expression branches are defined even at guards; mask to avoid unsigned underflow.
    middle = np.maximum(index, np.uint64(64)) - np.uint64(64)
    body = pattern(middle if kind == 1 else middle // 2, field if kind == 1 else middle % 2, seed)
    return np.where(left, guard(index,field,False), np.where(right, guard(np.maximum(index,np.uint64(count-64))-np.uint64(count-64),field,True),body)).astype(np.uint32)

def verify_array(actual, kind, field, seed, logical):
    assert len(actual) == (logical if kind == 0 else (logical if kind == 1 else 2 * logical) + 128)
    for begin in range(0,len(actual),1 << 20):
        end = min(begin + (1 << 20),len(actual))
        expected = expected_words(np.arange(begin,end,dtype=np.uint64),kind,field,seed,logical)
        assert np.array_equal(actual[begin:end],expected), (kind,field,begin,logical)

negative = []
seed = 0x243f6a88
valid = expected_words(np.arange(162,dtype=np.uint64),2,2,seed,17)
verify_array(valid,2,2,seed,17)
for name, mutate in [
    ('one_payload_bit',lambda a:a.__setitem__(64+7,int(a[64+7])^1)),
    ('left_guard_bit',lambda a:a.__setitem__(0,int(a[0])^1)),
    ('right_guard_bit',lambda a:a.__setitem__(-1,int(a[-1])^1)),
    ('swapped_regret_strategy_word',lambda a:a.__setitem__(slice(64,66),a[64:66][::-1])),
]:
    corrupt = valid.copy()
    mutate(corrupt)
    try:
        verify_array(corrupt,2,2,seed,17)
    except AssertionError:
        negative.append(name)
    else:
        raise AssertionError('reader accepted corrupted ' + name)
assert len(negative) == 4
files, cases, checked = [], [], 0
expected_files = []
for fixture_index, case in enumerate(P['cases']):
    name, logical = case['fixture'], case['words']
    seed = 0x243f6a88 ^ ((fixture_index * 0x85ebca6b) & 0xffffffff)
    specs = []
    for stage in [0,2]:
        for field in [0,1]:
            specs.append((f'{name}-physical-baseline-{field}-stage{stage}.bin',1,field,stage,logical+128))
        specs.append((f'{name}-physical-interleaved-stage{stage}.bin',2,2,stage,2*logical+128))
    for arm in [0,1]:
        for field in [0,1]:
            specs.append((f'{name}-output-arm{arm}-field{field}.bin',0,field,1,logical))
    for filename, kind, field, stage, words in specs:
        path = O / filename
        expected_files.append(filename)
        assert path.stat().st_size == 64 + words*4
        with path.open('rb') as file:
            header = file.read(64)
        assert struct.unpack('<8sQ6I3Q',header) == (b'D310RAW1',words,kind,field,fixture_index,seed,stage,0,words*4,0 if kind==0 else 64,logical)
        view = np.memmap(path,dtype='<u4',offset=64,mode='r',shape=(words,))
        verify_array(view,kind,field,seed,logical)
        del view
        files.append({'path':str(path),'bytes':path.stat().st_size,'sha256':h.sha(path),'whole_words_checked':words,'kind':kind,'field':field,'stage':stage})
        checked += words
    cases.append({'fixture':name,'words':logical,'full_raw_files':10,'all_physical_before_after_and_logical_outputs_exact':True})
    print('D310_READER_CASE',json.dumps(cases[-1]),flush=True)
assert sorted(x.name for x in O.iterdir()) == sorted(expected_files)
assert checked == sum(12 * c['words'] + 768 for c in P['cases'])
h.save(H / 'reader-report.json',{'id':'D310-reader','at':h.now(),'status':'all90_full_raw_files_words_headers_and_guards_exact',
    'cases':cases,'negative_reader_fixtures_rejected':negative,'files':files,'full_physical_and_output_words_checked':checked,
    'all_original_native_files_preserved':True,'source_protocol_sha256':sys.argv[1],
    'scope':'Transport bitwise exactness only. No CFR kernel, solver, convergence, speed, CPU/GPU engine equivalence or adoption claim.'})
print(json.dumps({'files':len(files),'all_words':checked,'negative_fixtures':len(negative)}),flush=True)
