"""Host-only deterministic adaptation of frozen D051; never launches native/CUDA work."""
from pathlib import Path
import copy,hashlib,json
P=Path(__file__).resolve().parent
OLD_SHA="a68daeefff0fd2cd968c8124e089586b62a91703a646030d3229c2ee53f68bf8"
GUARD=0x4b123456;SENTINEL=0xffffffff

def dense(g):
 a=g["arrays"];pb=a["p_off"][1];m=g["m_p"];nh=g["nh_p"]
 present=a["p_idx"][pb:pb+m];lower=a["p_lower"][pb:pb+m];upper=a["p_upper"][pb:pb+m]
 assert len(set(present))==m and all(0<=i<nh for i in present)
 missing=[i for i in range(nh) if i not in set(present)]
 a.update(p_off=[0,m],p_cnt=[m,m],p_idx=present*2+[SENTINEL]*3,p_lower=lower*2+[SENTINEL]*3,p_upper=upper*2+[SENTINEL]*3,p_missing_idx=missing*2+[SENTINEL]*3 if missing else [0])
 for slot in range(2):
  start=slot*nh-a["p_off"][slot];count=nh-a["p_cnt"][slot]
  got=a["p_missing_idx"][start:start+count]
  assert got==missing and set(present).isdisjoint(got) and sorted(present+got)==list(range(nh))
 g["complement_shape"]="empty-own" if m==0 else "full-own" if m==nh else "partial-own"
 return g

def full_own(old):
 g=copy.deepcopy(old);a=g["arrays"];pb=a["p_off"][1];mp=g["m_p"]
 keep=[i for i,s in enumerate(g["strengths_p"]) if s!=SENTINEL];mapping={i:j for j,i in enumerate(keep)}
 g["id"]+="-full-own";g["hands_p"]=[g["hands_p"][i] for i in keep];g["strengths_p"]=[g["strengths_p"][i] for i in keep];g["nh_p"]=len(keep)
 present=[mapping[i] for i in a["p_idx"][pb:pb+mp]]
 a["p_idx"]=[SENTINEL]*pb+present+[SENTINEL]*3
 for key in ["same_p","pc1","pc2"]:a[key]=[a[key][i] for i in keep]+[SENTINEL]*3
 if g["rounding_witness_own_index"] is not None:g["rounding_witness_own_index"]=mapping[g["rounding_witness_own_index"]]
 g["output_active"]=[False]*len(g["output_initial"])
 for node in [2,5]:
  start=a["cfv_slot"][node]*g["nh_max"];g["output_active"][start:start+g["nh_p"]]=[True]*g["nh_p"]
 g["coverage"]["blocked_own"]=0;g["coverage"]["same_present"]=sum(x!=SENTINEL for x in a["same_p"][:g["nh_p"]]);g["coverage"]["same_absent"]=g["nh_p"]-g["coverage"]["same_present"]
 assert g["nh_p"]==g["m_p"]==257
 return dense(g)

def main():
 raw=(P/"original-d051-corpus.json").read_bytes();assert hashlib.sha256(raw).hexdigest()==OLD_SHA
 original=json.loads(raw);data=copy.deepcopy(original);data["id"]="E029-direct"
 data["geometries"]=[dense(g) for g in data["geometries"]]
 for board in ["Ks7h2dQhTc","AsKsQsJsTs"]:
  for player in [0,1]:
   base=next(g for g in original["geometries"] if g["board_text"]==board and g["target_m"]==257 and g["player"]==player)
   g=full_own(base);data["geometries"].append(g)
   c=copy.deepcopy(next(c for c in original["cases"] if c["geometry"]==base["id"] and c["profile"]=="seeded_ordinary" and c["count"]==2));c.update(id=g["id"]+"-seeded_ordinary",geometry=g["id"]);data["cases"].append(c)
 assert len(data["geometries"])==40 and len(data["cases"])==152
 assert data["cases"][:148]==original["cases"]
 changed_arrays={"p_off","p_cnt","p_idx","p_lower","p_upper"}
 for old,new in zip(original["geometries"],data["geometries"][:36]):
  assert {k:v for k,v in old.items() if k!="arrays"}=={k:v for k,v in new.items() if k not in {"arrays","complement_shape"}}
  assert {k:v for k,v in old["arrays"].items() if k not in changed_arrays}=={k:v for k,v in new["arrays"].items() if k not in changed_arrays|{"p_missing_idx"}}
  for key in ["p_idx","p_lower","p_upper"]:assert old["arrays"][key][old["arrays"]["p_off"][1]:old["arrays"]["p_off"][1]+old["m_p"]]==new["arrays"][key][new["arrays"]["p_off"][1]:new["arrays"]["p_off"][1]+new["m_p"]]
 payload=(json.dumps(data,separators=(",",":"),allow_nan=False)+"\n").encode()
 with (P/"corpus.json").open("xb") as f:f.write(payload)
 gs={g["id"]:g for g in data["geometries"]};active=guards=iw=0
 for c in data["cases"]:
  g=gs[c["geometry"]];ac=sum(g["output_active"]) if c["count"] else 0;active+=ac;guards+=2*(len(g["output_initial"])-ac)
  common=sum(len(v) for k,v in g["arrays"].items() if k!="p_missing_idx")+len(c["reach_o_bits"]);iw+=2*common+len(g["arrays"]["p_missing_idx"])
 summary={"id":"E029-direct-corpus","corpus_sha256":hashlib.sha256(payload).hexdigest(),"original_corpus_sha256":OLD_SHA,"bytes":len(payload),"geometry_count":40,"comparison_pairs":152,"kernel_launches":304,"inherited_pairs":148,"extra_full_own_pairs":4,"regular_pairs":148,"zero_count_pairs":4,"active_words_compared":active,"output_guard_word_checks":guards,"input_buffers_per_arm":[21,22],"device_input_buffer_checks":152*43,"device_input_word_checks":iw,"rounding_witness_checks":2,"stdout_markers":155,"raw_result_records":152,"inherited_active_data_exact":True,"dense_slot_complements_checked":80,"complement_shapes":{shape:sum(g["complement_shape"]==shape for g in gs.values()) for shape in ["empty-own","partial-own","full-own"]},"nonzero_missing_start_geometries":sum(g["nh_p"]-g["arrays"]["p_off"][1]>0 for g in gs.values()),"native_execution":False}
 with (P/"corpus-summary.json").open("x",encoding="utf-8",newline="\n") as f:json.dump(summary,f,indent=2);f.write("\n")
 print(json.dumps(summary))
if __name__=="__main__":main()
