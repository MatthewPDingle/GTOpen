import array,struct,sys
from pathlib import Path
def vec(raw,code):
 n,=struct.unpack_from('<Q',raw);v=array.array(code);v.frombytes(raw[8:]);assert len(v)==n
 if sys.byteorder!='little':v.byteswap()
 return v
def plans(path,fields):
 out={}
 with Path(path).open('rb')as f:
  assert f.read(17)==b'D183_PLAN_RAW1\0\0\0'
  for expected in fields:
   n,=struct.unpack('<I',f.read(4));name=f.read(n).decode();assert name==expected;size,=struct.unpack('<Q',f.read(8));out[name]=f.read(size);assert len(out[name])==size
  assert not f.read(1)
 return out
def gpu_metadata(path):
 out={}
 with Path(path).open('rb')as f:
  assert f.read(16)==b'D166-GPU-RAW1\0\0\0'
  for _ in range(69):
   kind,n=struct.unpack('<II',f.read(8));name=f.read(n).decode();words,=struct.unpack('<Q',f.read(8));assert kind in[0,2]
   if name in ['d_children','d_lock_off']:
    width=4 if name=='d_children'else8;assert words*4%width==0
    data=b'\0'*(words*4)if kind==0 else f.read(words*4)
    if kind==0:assert f.read(4)==b'\0'*4
    v=array.array('I'if width==4 else'Q');v.frombytes(data);out[name]=v
   elif kind==0:assert f.read(4)==b'\0'*4
   else:f.seek(words*4,1)
  assert not f.read(1)
 assert set(out)=={'d_children','d_lock_off'};return out
def spans(raw):
 n,=struct.unpack_from('<Q',raw);assert len(raw)==8+8*n;return list(struct.Struct('<II').iter_unpack(raw[8:]))
def nested(raw):
 n,=struct.unpack_from('<Q',raw);assert n==2;at=8;out=[]
 for _ in range(2):
  size=8+4*struct.unpack_from('<Q',raw,at)[0];out.append(vec(raw[at:at+size],'I'));at+=size
 assert at==len(raw);return out
def write_projection(path,fields):
 with Path(path).open('xb')as f:
  f.write(b'D267-MODEL-v1\0\0\0');f.write(struct.pack('<I',len(fields)))
  for name,v in fields.items():
   b=name.encode();f.write(struct.pack('<I',len(b)));f.write(b);f.write(struct.pack('<IQ',v.itemsize,len(v)));f.write(v.tobytes())
def read_projection(path):
 out={}
 with Path(path).open('rb')as f:
  assert f.read(16)==b'D267-MODEL-v1\0\0\0';n,=struct.unpack('<I',f.read(4))
  for _ in range(n):
   size,=struct.unpack('<I',f.read(4));name=f.read(size).decode();width,count=struct.unpack('<IQ',f.read(12));assert width in[4,8]and name not in out;v=array.array('I'if width==4 else'Q');v.frombytes(f.read(width*count));assert len(v)==count;out[name]=v
  assert not f.read(1)
 return out
