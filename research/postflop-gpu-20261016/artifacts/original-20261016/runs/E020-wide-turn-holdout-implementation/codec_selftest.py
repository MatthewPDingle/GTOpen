"""Bounded host-only parser/byte-comparison checks; no numerical solver claim."""
from pathlib import Path
import importlib.util,json,struct,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('holdout_runner',HERE/'run.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
OUT=HERE/'codec-selftest';OUT.mkdir(exist_ok=False)
result={'algorithm':'dcfr','iteration':20,'use_isomorphism':True,'exploit_bits':123,
 'state_fingerprint':{'arenas':[]}}
metadata=json.dumps({k:result[k] for k in ['algorithm','iteration','use_isomorphism','exploit_bits']},separators=(',',':')).encode()
data=b'GTO-WIDE-RAW-v1\0'+struct.pack('<Q',len(metadata))+metadata
frame_start=len(data)
for player in (0,1):
    for which,kind in ((0,1),(1,2)):
        result['state_fingerprint']['arenas'].append({'player':player,'arena':'regrets' if which==0 else 'strategy_sums',
            'kind':'i16' if kind==1 else 'u16','entries':3,'scale_entries':2})
        data+=struct.pack('<BBBQQ',player,which,kind,3,2)
        data+=struct.pack('<3H2I',0,0x8000,0xffff,0x80000000,0x7fc01234)
def put(name,value):
    p=OUT/name;p.write_bytes(value);return p
good=put('valid.bin',data);same=put('same.bin',data)
decoded=r.raw_layout(good,result)
assert decoded['bytes']==len(data) and len(decoded['frames'])==4
assert r.binary_equal(good,same)
cases={'bad_magic':b'X'+data[1:], 'truncated_magic':data[:15],
       'truncated_payload':data[:-1],'trailing_byte':data+b'X',
       'wrong_player':data[:frame_start]+bytes([1])+data[frame_start+1:],
       'wrong_kind':data[:frame_start+2]+bytes([0])+data[frame_start+3:],
       'wrong_length':data[:frame_start+3]+struct.pack('<Q',4)+data[frame_start+11:]}
checked=[]
for name,value in cases.items():
    path=put(name+'.bin',value)
    try:r.raw_layout(path,result)
    except (AssertionError,ValueError,struct.error,UnicodeDecodeError):checked.append(name)
    else:raise AssertionError('corruption escaped: '+name)
changed=bytearray(data);changed[frame_start+19]^=1
different=put('changed_word.bin',bytes(changed))
r.raw_layout(different,result) # Same schema; the full byte comparison must reject.
assert not r.binary_equal(good,different)
wrong={**result,'iteration':40}
try:r.raw_layout(good,wrong)
except AssertionError:checked.append('metadata_mismatch')
else:raise AssertionError('metadata mismatch escaped')
r.save(OUT/'report.json',{'status':'pass','scope':'host parser and exact-file comparator only',
    'valid_four_store_decode':True,'equal_files_pass':True,'changed_word_rejected_by_full_compare':True,
    'required_corruptions_rejected':checked,'magic_bytes':16,'gpu_jobs':0,'native_solver_runs':0,
    'note':'Draft read(15) bug corrected to read(len(magic)) before freeze; no failed/replaced native sample.'})
print(json.dumps({'status':'pass','rejected_corruptions':len(checked),'magic_bytes':16}))
