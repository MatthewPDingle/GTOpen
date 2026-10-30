// Frozen-table traversal of the complete registered BB subtree, actual cards.
typedef unsigned long long U64;
__device__ double poker_uniform(U64* state){
 *state+=0x9e3779b97f4a7c15ULL;U64 z=*state;
 z=(z^(z>>30))*0xbf58476d1ce4e5b9ULL;z=(z^(z>>27))*0x94d049bb133111ebULL;
 return (double)((z^(z>>31))>>11)*(1./9007199254740992.);
}
__device__ void poker_key(const unsigned char* cards,int player,int pre,int branch,int street,U64 history,U64* hi,U64* lo){
 unsigned char c[7];c[0]=cards[player*2];c[1]=cards[player*2+1];
 if(c[0]>c[1]){unsigned char t=c[0];c[0]=c[1];c[1]=t;}
 for(int i=2;i<7;i++)c[i]=63;
 if(pre<0){for(int i=0;i<3;i++)c[i+2]=cards[i+4];
  for(int i=2;i<5;i++)for(int j=i+1;j<5;j++)if(c[i]>c[j]){unsigned char t=c[i];c[i]=c[j];c[j]=t;}
  if(street>=1)c[5]=cards[7];if(street>=2)c[6]=cards[8];}
 *lo=((U64)player)<<42;for(int i=0;i<7;i++)*lo|=((U64)c[i])<<(6*i);
 *hi=pre>=0?(U64)(pre+1):((1ULL<<63)|(history<<4)|(U64)branch);
}
__device__ void poker_policy(U64 hi,U64 lo,int n,int nt,const U64* keys,const double* table,double* p){
 int left=0,right=nt;while(left<right){int m=left+(right-left)/2;U64 h=keys[m*2],l=keys[m*2+1];
  if(h<hi||(h==hi&&l<lo))left=m+1;else right=m;}
 bool found=left<nt&&keys[left*2]==hi&&keys[left*2+1]==lo;
 for(int a=0;a<4;a++)p[a]=a<n?(found?table[left*4+a]:1./n):0.;
}
struct PokerFrame {int pre,branch,stage,actor,n,selected,processed,record;U64 history;PFState state;double p[4],values[4];};
extern "C" __global__ void poker_walk(int samples,int cap,int nt,U64 seed,const unsigned char* deals,
 const int* kinds,const int* actors,const int* arities,const int* children,const double* configs,const double* offsets,
 const U64* keys,const double* table,U64* outkeys,int* tags,double* deltas,int* counts,double* roots){
 int tid=blockIdx.x*blockDim.x+threadIdx.x;if(tid>=samples)return;int updater=tid&1;
 const unsigned char* cards=deals+(tid/2)*9;U64 rng=seed^((U64)tid*0xd1342543de82ef95ULL);
 unsigned char seven[7];unsigned ranks[2];for(int p=0;p<2;p++){seven[0]=cards[p*2];seven[1]=cards[p*2+1];for(int i=0;i<5;i++)seven[i+2]=cards[i+4];ranks[p]=pf_eval7(seven);}
 int winner=ranks[0]==ranks[1]?-1:(ranks[1]>ranks[0]);
 PokerFrame stack[20];stack[0]={};stack[0].pre=0;int depth=0,used=0;double last=0.;
 while(depth>=0){PokerFrame* f=&stack[depth];
  if(f->stage==0){
   if(f->pre>=0){int node=f->pre,kind=kinds[node];
    if(kind==1){last=offsets[node*2+updater];depth--;continue;}
    if(kind==3){double amount=configs[node*4]/2.,rake=configs[node*4+2]*2.*amount,capr=configs[node*4+3];if(capr>0&&rake>capr)rake=capr;
     last=(winner<0?-rake/2.:(winner==updater?amount-rake:-amount))+offsets[node*2+updater];depth--;continue;}
    if(kind==2){f->branch=node;f->pre=-1;f->history=1;PFConfig cfg={configs[node*4],configs[node*4+1],configs[node*4+2],configs[node*4+3]};f->state=pf_root(cfg);}
   }
   if(f->pre<0){int b=f->branch;PFConfig cfg={configs[b*4],configs[b*4+1],configs[b*4+2],configs[b*4+3]};
    while(f->state.kind==1){f->state=pf_deal(f->state);f->history=(f->history<<3)|5ULL;}
    if(f->state.kind>=2){double payout[3];pf_payouts(cfg,f->state,payout);
     last=(f->state.kind==2?(updater==f->state.player?payout[1]:payout[0]):(winner<0?payout[2]:(updater==winner?payout[0]:payout[1])))+offsets[b*2+updater];depth--;continue;}
    PFAction actions[3];f->n=pf_actions(cfg,f->state,actions);f->actor=f->state.player;
   }else{f->n=arities[f->pre];f->actor=actors[f->pre];}
   if(used>=cap){counts[tid]=-1;return;}
   f->record=tid*cap+used++;U64 hi,lo;poker_key(cards,f->actor,f->pre,f->branch,f->state.street,f->history,&hi,&lo);
   outkeys[f->record*2]=hi;outkeys[f->record*2+1]=lo;tags[f->record]=(f->actor==updater?f->n:-f->n);
   poker_policy(hi,lo,f->n,nt,keys,table,f->p);f->selected=-1;
   if(f->actor!=updater){double x=poker_uniform(&rng),sum=0.;f->selected=f->n-1;
    for(int a=0;a<f->n;a++){sum+=f->p[a];if(x<sum){f->selected=a;break;}}}
   for(int a=0;a<4;a++)f->values[a]=0.;f->processed=0;f->stage=1;
  }
  if(f->stage==2){int a=f->selected<0?f->processed:f->selected;f->values[a]=last;f->processed++;f->stage=1;}
  int limit=f->selected<0?f->n:1;
  if(f->processed<limit){
   if(depth+1>=20){counts[tid]=-2;return;}
   int a=f->selected<0?f->processed:f->selected;PokerFrame child={};
   if(f->pre>=0){child.pre=children[f->pre*4+a];}
   else{int b=f->branch;PFConfig cfg={configs[b*4],configs[b*4+1],configs[b*4+2],configs[b*4+3]};PFAction actions[3];pf_actions(cfg,f->state,actions);
    child.pre=-1;child.branch=b;child.history=(f->history<<3)|(U64)(a+1);child.state=pf_act(cfg,f->state,actions[a]);}
   f->stage=2;stack[++depth]=child;continue;
  }
  last=0.;if(f->selected>=0){last=f->values[f->selected];for(int a=0;a<4;a++)deltas[f->record*4+a]=f->p[a];}
  else{for(int a=0;a<f->n;a++)last+=f->p[a]*f->values[a];for(int a=0;a<4;a++)deltas[f->record*4+a]=a<f->n?f->values[a]-last:0.;}
  depth--;
 }
 counts[tid]=used;roots[tid]=last;
}
