// Existing finite oracle game, dynamic frozen policies, deterministic reduction.
typedef unsigned long long U64;
__device__ double conv_uniform(U64* state){*state+=0x9e3779b97f4a7c15ULL;U64 z=*state;
 z=(z^(z>>30))*0xbf58476d1ce4e5b9ULL;z=(z^(z>>27))*0x94d049bb133111ebULL;
 return (double)((z^(z>>31))>>11)*(1./9007199254740992.);}
extern "C" __global__ void conv_full(const int* actors,const int* arity,const int* children,const int* infos,
 const int* offsets,const double* policy,const double* utilities,const double* chance,double* delta,double* average){
 int d=blockIdx.x*blockDim.x+threadIdx.x;if(d>=24)return;double reach[19][2]={},value[19][2]={};reach[0][0]=reach[0][1]=1.;
 for(int a=0;a<128;a++){delta[d*128+a]=0.;average[d*128+a]=0.;}
 for(int n=0;n<19;n++){int k=arity[n];if(!k)continue;int p=actors[n],o=offsets[infos[d*19+n]];
  for(int a=0;a<k;a++){int c=children[n*3+a];reach[c][p]=reach[n][p]*policy[o+a];reach[c][1-p]=reach[n][1-p];
   average[d*128+o+a]=chance[d]*reach[n][p]*policy[o+a];}}
 for(int n=18;n>=0;n--){int k=arity[n];if(!k){for(int p=0;p<2;p++)value[n][p]=utilities[(d*19+n)*2+p];continue;}
  int p=actors[n],o=offsets[infos[d*19+n]];
  for(int a=0;a<k;a++)for(int q=0;q<2;q++)value[n][q]+=policy[o+a]*value[children[n*3+a]][q];
  for(int a=0;a<k;a++)delta[d*128+o+a]=chance[d]*reach[n][1-p]*(value[children[n*3+a]][p]-value[n][p]);
 }
}
extern "C" __global__ void conv_sample(int count,U64 seed,const int* actors,const int* arity,const int* children,const int* infos,
 const int* offsets,const double* policy,const double* utilities,const double* chance,double* delta,double* average){
 int t=blockIdx.x*blockDim.x+threadIdx.x;if(t>=count)return;int updater=t&1;
 U64 rng=seed^((U64)t*0xd1342543de82ef95ULL);double x=conv_uniform(&rng),sum=0.;int d=23;
 for(int i=0;i<24;i++){sum+=chance[i];if(x<sum){d=i;break;}}
 int reached[19]={},choice[19]={};double value[19]={};reached[0]=1;
 for(int a=0;a<128;a++){delta[t*128+a]=0.;average[t*128+a]=0.;}
 for(int n=0;n<19;n++){if(!reached[n]||!arity[n])continue;int o=offsets[infos[d*19+n]];
  if(actors[n]==updater){for(int a=0;a<arity[n];a++)reached[children[n*3+a]]=1;}
  else{x=conv_uniform(&rng);sum=0.;int selected=arity[n]-1;
   for(int a=0;a<arity[n];a++){sum+=policy[o+a];if(x<sum){selected=a;break;}}
   // All probabilities belong in the average, not only the sampled prefix.
   for(int a=0;a<arity[n];a++)average[t*128+o+a]=policy[o+a];
   choice[n]=selected;reached[children[n*3+selected]]=1;}
 }
 for(int n=18;n>=0;n--){if(!reached[n])continue;int k=arity[n];if(!k){value[n]=utilities[(d*19+n)*2+updater];continue;}
  int o=offsets[infos[d*19+n]];if(actors[n]!=updater){value[n]=value[children[n*3+choice[n]]];continue;}
  for(int a=0;a<k;a++)value[n]+=policy[o+a]*value[children[n*3+a]];
  for(int a=0;a<k;a++)delta[t*128+o+a]=value[children[n*3+a]]-value[n];
 }
}
extern "C" __global__ void conv_reduce(int samples,double scale,const int* offsets,const double* delta,const double* increment,
 double* regret,double* average,double* policy){
 int info=blockIdx.x*blockDim.x+threadIdx.x;if(info>=60)return;int lo=offsets[info],hi=offsets[info+1];double total=0.;
 for(int a=lo;a<hi;a++){double r=0.,av=0.;for(int s=0;s<samples;s++){r+=delta[s*128+a];av+=increment[s*128+a];}
  regret[a]+=scale*r;average[a]+=scale*av;double v=regret[a];if(v>0.)total+=v;}
 for(int a=lo;a<hi;a++)policy[a]=total>0.?(regret[a]>0.?regret[a]/total:0.):1./(hi-lo);
}
