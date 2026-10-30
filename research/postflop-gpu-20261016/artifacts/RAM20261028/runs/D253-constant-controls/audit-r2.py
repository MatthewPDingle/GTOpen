import json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D253-constant-controls';P=h.read(H/'protocol.json');O=H/'output';M=h.read(O/'metadata.json');checks=0
for p,d in P['input_sha256'].items():h.pin(p,d)
def ck(v,label):
 global checks
 assert v,label;checks+=1
def u32(f):return struct.unpack('<I',f.read(4))[0]
def words(f):
 n,=struct.unpack('<Q',f.read(8));ck(n<2000,'bounded entire vector');v=list(struct.unpack('<'+'I'*n,f.read(n*4)));ck(len(v)==n,'whole vector');return v
def seed(i,phase,arm,n):return[(0xcd123456^(i*131)&0xffffffff^(phase*0x9e37)&0xffffffff^(arm*0x85ebca6b)&0xffffffff^(j*17)&0xffffffff)&0xffffffff for j in range(n)]
patterns=P['patterns'];launches=guards=active=changes=symbolwords=0
with(O/'raw.bin').open('rb')as f:
 magic=b'D253-CONSTANT-RAW1\0';ck(f.read(len(magic))==magic,'magic');ck(u32(f)==24,'fixed full case count')
 for i,c in enumerate(P['cases']):
  width,n=c['threads'],c['n'];length=17+n+19;ck([u32(f)for _ in range(4)]==[i,width,n,length],'complete original ordered geometry');m=M['cases'][i];ck(m['id']==i and m['threads']==width and m['n']==n and m['output_physical_words']==length,'metadata geometry')
  ck(m['captured_functions'][0]!=m['captured_functions'][1]and m['captured_modules'][0]!=m['captured_modules'][1],'actual independent captured function/module handles');ck(m['kernel_nodes']==2 and m['eager_executions']==2 and m['graph_replays']==8,'actual graph corpus')
  regions=m['symbol_regions']+m['output_regions'];ck([x[1]for x in regions]==[12,12,length*4,length*4],'actual byte extents')
  for j,(a,sz)in enumerate(regions):
   for b,bs in regions[j+1:]:ck(a+sz<=b or b+bs<=a,'actual complete device regions disjoint')
  for phase in range(5):
   ck(u32(f)==phase,'original fixed eager/replay order')
   for arm in range(2):
    pre,post,const=words(f),words(f),words(f);original=seed(i,phase,arm,length);pattern=patterns[(i+phase+arm)%5];expected=original[:];expected[17:17+n]=[pattern[j%3]for j in range(n)];ck(pre==original,'all initial output poison words');ck(const==pattern and len(const)==3,'entire actual post-execution module symbol unchanged');ck(post==expected,'entire actual output including all guards');ck(post[:17]==pre[:17]and post[17+n:]==pre[17+n:],'unowned guard image');changed=sum(a!=b for a,b in zip(pre,post));ck(n==0 or changed>0,'nonvacuous writes');changes+=changed;guards+=36;active+=n;symbolwords+=3;launches+=1
 ck(f.read(1)==b'','whole raw EOF')
ck(launches==M['kernel_executions']==240 and M['case_count']==24 and M['captured_kernel_nodes']==48,'complete original native inventory');ck(changes==M['nonvacuous_output_changes'],'all changed output words');ck(M['fresh_third_module_symbol_words']==[0,0,0],'fresh module initialized zero');h.custody()
D=ROOT/'comparisons/D253-constant-controls';D.mkdir(exist_ok=False);h.save(D/'report.json',{'id':'D253','at':h.now(),'status':'pass_scoped_constant_symbol_module_isolation_and_graph_bit_transport','protocol_sha256':h.sha(H/'protocol.json'),'cases':24,'kernel_executions':launches,'captured_kernel_nodes':48,'reader_checks':checks,'active_output_words':active,'guard_words':guards,'actual_symbol_words':symbolwords,'nonvacuous_output_changes':changes,'raw_sha256':{str(p):h.sha(p)for p in O.iterdir()if p.is_file()},'no_optimizer_or_gain_accepted':True,'solver_or_speed_samples':0,'limits':'Finite float-bit transport only. Same named symbols in two simultaneous modules use distinct actual device regions and graph functions/modules on separate streams. Capture once then update symbols before each eager/replay; whole symbols/outputs/guards exact. Fresh third module zero state checked. No writes overlap a grid reading the same symbol. Not floating-CFR/large-game/solver/actual allocation peak/capacity/latency/performance proof.'});print('D253 whole raw reader passed',checks,flush=True)
