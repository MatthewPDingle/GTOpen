import hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D217-nullable-lock-direct';P=h.read(H/'protocol.json');category=sys.argv[1];assert category in P['category_order'];D=H/category;O=D/'output';checks=outwords=immwords=guardwords=0
for p,d in P['input_sha256'].items():h.pin(p,d)
def req(v,label):
 global checks
 assert v,label;checks+=1
def vector(f):
 b=f.read(8);req(len(b)==8,'whole vector header');n=struct.unpack('<Q',b)[0];req(n<10**7,'bounded vector');b=f.read(4*n);req(len(b)==4*n,'whole vector');return b
def ident(f,i):req(f.read(4)==struct.pack('<I',i),'fixed case index')
def guard(actual,seed,lo,hi):
 global guardwords
 req(len(actual)==len(seed) and 0<=lo<=hi<=len(seed)//4,'same whole output extent');req(actual[:lo*4]==seed[:lo*4] and actual[hi*4:]==seed[hi*4:],'every unowned/guard bit');guardwords+=lo+len(seed)//4-hi
def mutation_detected(fn):
 try:fn()
 except AssertionError:return
 raise AssertionError('negative calibration not detected')
seed=struct.pack('<8I',*range(8));changed=bytearray(seed);changed[0]^=1;mutation_detected(lambda:guard(bytes(changed),seed,2,5));changed=bytearray(seed);changed[28]^=1;mutation_detected(lambda:guard(bytes(changed),seed,2,5));guardwords=checks=0
corpus=h.read(D/'corpus.json');cases=corpus['cases'] if category=='up' else corpus;req(len(cases)==P['cases'][category],'entire declared corpus')
prefix='E106_UP' if category=='up' else 'E106_DOWN';files={n:(O/(n+'.bin')).open('rb') for n in ['inputs','baseline','candidate','baseline-inputs','candidate-inputs']}
for n,f in files.items():
 suffix='_IN1' if n=='inputs' else '_OUT1' if n in ['baseline','candidate'] else '_IM1';magic=(prefix+suffix).encode();req(f.read(len(magic))==magic,'new full format magic')
nulls=present=0;kindcounts={};coverage={}
for i,c in enumerate(cases):
 for f in files.values():ident(f,i)
 desc=vector(files['inputs']);req(desc==struct.pack('<'+'I'*len(c['descriptor']),*c['descriptor']),'exact case descriptor and argument flags');immutable=[vector(files['inputs']) for _ in range(12)];seeds=[vector(files['inputs']) for _ in range(3 if category=='up' else 2)];outputs={arm:[vector(files[arm]) for _ in seeds] for arm in ['baseline','candidate']};post={arm:[vector(files[arm+'-inputs']) for _ in range(12)] for arm in ['baseline','candidate']}
 req(outputs['baseline']==outputs['candidate'],'every physical output word exact');req(post['baseline']==post['candidate']==immutable,'all actual immutable input words exact');outwords+=2*sum(len(x)//4 for x in outputs['baseline']);immwords+=2*sum(len(x)//4 for x in immutable)
 null=c['nullable'];nulls+=int(null);present+=int(not null);lock=immutable[8 if category=='up' else 10];req(len(lock)%8==0,'full i64 lock image')
 if null:req(all(v[0]==-1 for v in struct.iter_unpack('<q',lock)),'null only for actual all-unlocked offsets')
 if category=='up':
  nh,na,off,parent,stride=c['hands'],c['actions'],c['descriptor'][12],c['descriptor'][11],c['descriptor'][9];kind=c['kernel_kind'];kindcounts[kind]=kindcounts.get(kind,0)+1
  for arm,result in outputs.items():
   for j,v in enumerate(result):
    lo,hi=(off,off+na*nh) if j<2 and c['count'] and kind==0 and c['role']==0 else (parent*stride,parent*stride+nh) if j==2 and c['count'] else (0,0);guard(v,seeds[j],lo,hi)
 else:
  ns=c['descriptor'][:2];actor=c['actor'];nh=ns[actor];na=c['na']
  for arm,result in outputs.items():
   for j,v in enumerate(result):
    lo,hi=(5*nh,(5+na)*nh) if c['count'] and j==actor and nh>0 else (0,0);guard(v,seeds[j],lo,hi)
 for key in ['nullable','kernel_kind','role','p','actions','threads','value_mode','nh','na','block','actor','lock_mode','regret_mode','reach_mode','reuse_zero','count']:
  if key in c:coverage.setdefault(key,set()).add(c[key])
for n,f in files.items():req(f.read(1)==b'','complete endpoint '+n);f.close()
req(nulls>0 and present>0,'both pointer contracts');req(nulls+present==len(cases),'whole count');
if category=='up':req(kindcounts=={0:1365,1:1365,2:1365},'training and both evaluation modes')
logs=(H/'execution'/(category+'.stdout.log')).read_text(encoding='utf-8');marker=prefix+' ';rows=[json.loads(x.split(marker,1)[1]) for x in logs.splitlines() if marker in x];req(len(rows)==len(cases)+1 and rows[-1]['stage']=='complete','all native markers');summary=rows[-1];req(summary['cases']==len(cases) and summary['kernel_launches']==2*len(cases),'all actual launches');req(summary['output_words_both_arms']==outwords and summary['immutable_words_both_arms']==immwords and summary['guard_words_both_arms']==guardwords,'reader/native raw counts agree')
for i,x in enumerate(rows[:-1]):req(x['id']==i and x['stage']=='case','every original native case in order')
req(sum(p.stat().st_size for p in O.iterdir() if p.is_file())<=P['raw_reservation_bytes'],'bounded raw output');h.custody();h.save(D/'report.json',{'id':'D217-'+category,'at':h.now(),'status':'pass_direct_full_raw_nullable_lock_equivalence','cases':len(cases),'kernel_launches':2*len(cases),'null_cases':nulls,'nonnull_cases':present,'kernel_mode_counts':kindcounts,'output_words_both_arms':outwords,'immutable_words_both_arms':immwords,'guard_words_both_arms':guardwords,'reader_checks':checks,'coverage':{k:sorted(v) for k,v in coverage.items()},'raw_sha256':{str(p):h.sha(p) for p in O.iterdir() if p.is_file()},'source_native_immutable_guard_assertions_passed':True,'all_case_records_retained':True,'source_or_compiler_or_shader_changed':False,'candidate_accepted':False,'performance_samples':0,'limits':'Finite direct corpus only. Whole raw outputs/immutable snapshots/unowned guards exact; no universal IEEE payload/illegal alias/arbitrary bounds, host predicate/graphs/fullcanonical/paging/material/capacity/complete speed/adoption proof.'});print(json.dumps({'category':category,'cases':len(cases),'checks':checks,'null_cases':nulls,'output_words':outwords}),flush=True)
