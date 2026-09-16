// Frozen conditional predictions converted to counterfactual values under a
// legal-pair prior anchored at the first heads-up node. No common EV offset.
typedef unsigned int u32;
__device__ double combos(int h){return h/13==h%13?6.:h/13>h%13?4.:12.;}
__device__ double incidence(int h){return h/13==h%13?3.:h/13>h%13?1.:3.;}
__device__ double compatible(int h,int j){
 int a=h/13,b=h%13,c=j/13,d=j%13;
 int overlap=(a==c)+(c!=d && a==d)+(a!=b && b==c)+(a!=b && c!=d && b==d);
 return combos(h)*combos(j)-4.*overlap*incidence(h)*incidence(j)+(h==j?combos(h):0.);
}
__device__ void ranks(const double* d,double* r){
 for(int j=0;j<13;j++)r[j]=0.;
 for(int h=0;h<169;h++){double w=d[h]*incidence(h)/combos(h);r[h/13]+=w;if(h/13!=h%13)r[h%13]+=w;}
}
__device__ double legal(int h,const double* d,const double* r){
 return 1.-4.*incidence(h)/combos(h)*(r[h/13]+(h/13!=h%13?r[h%13]:0.))+d[h]/combos(h);
}
extern "C" __global__ void interface_prepare(const u32* entries,const int* seats,int np,
 const u32* src,const float* reach,const float* totals,double* z){
 u32 ctx=blockIdx.x,nd=entries[ctx];
 __shared__ double d[338],r[13],sum[256];
 for(int x=threadIdx.x;x<338;x+=blockDim.x){int p=seats[ctx*2+x/169];u32 b=src[(size_t)nd*np+p];
  // Off-path normalization is explicitly defined by a uniform class prior.
  d[x]=totals[b]>0?(double)reach[(size_t)b*169+x%169]/totals[b]:combos(x%169)/1326.;}
 __syncthreads();if(threadIdx.x==0)ranks(d+169,r);__syncthreads();
 int h=threadIdx.x;sum[h]=h<169?d[h]*legal(h,d+169,r):0.;__syncthreads();
 for(int step=128;step;step/=2){if(h<step)sum[h]+=sum[h+step];__syncthreads();}
 if(h==0)z[ctx]=sum[0];
}
extern "C" __global__ void interface_terminal(
 const u32* terms,const u32* contexts,const int* seats,const double* entry_z,
 int p,int np,int use_learned,const int* kind,const int* winner,const double* sprs,
 const float* pots,const float* inv,const float* rw,const u32* src,const float* reach,
 const float* reach_mass,const float* eq,const u32* slots,float* val){
 u32 nd=terms[blockIdx.x],ctx=contexts[nd];int oop=seats[ctx*2],ip=seats[ctx*2+1];
 __shared__ double d[338],rankmass[26],qraw[338],mass[338],correction[338],desc[10],summary[16];
 __shared__ double totals[2],prob,z,center,ez;
 if(threadIdx.x==0){totals[0]=reach_mass[src[(size_t)nd*np+oop]];totals[1]=reach_mass[src[(size_t)nd*np+ip]];
  prob=1.;for(int q=0;q<np;q++)if(q!=p)prob*=reach_mass[src[(size_t)nd*np+q]];ez=entry_z[ctx];}
 __syncthreads();if(prob<=0.){for(int h=threadIdx.x;h<169;h+=blockDim.x)val[(size_t)slots[nd]*169+h]=0.;return;}
 for(int x=threadIdx.x;x<338;x+=blockDim.x){int s=x/169,seat=s?ip:oop;u32 b=src[(size_t)nd*np+seat];
  d[x]=totals[s]>0?(double)reach[(size_t)b*169+x%169]/totals[s]:combos(x%169)/1326.;}
 __syncthreads();if(threadIdx.x<2)ranks(d+threadIdx.x*169,rankmass+threadIdx.x*13);__syncthreads();
 if(threadIdx.x==0){z=0.;for(int h=0;h<169;h++)z+=d[h]*legal(h,d+169,rankmass+13);}
 __syncthreads();
 if(p!=oop && p!=ip){
  // Folded seats' sunk costs use the SAME terminal pair probability.
  for(int h=threadIdx.x;h<169;h+=blockDim.x)val[(size_t)slots[nd]*169+h]=(float)(-prob*inv[(size_t)nd*np+p]*z/ez);return;
 }
 int side=p==ip;
 if(kind[nd]==1){for(int h=threadIdx.x;h<169;h+=blockDim.x){
   double weight=legal(h,d+(1-side)*169,rankmass+(1-side)*13)/ez;
   val[(size_t)slots[nd]*169+h]=(float)(prob*weight*(pots[nd]*(winner[nd]==p)-inv[(size_t)nd*np+p]));}return;}
 bool learned=use_learned && sprs[nd]>=1. && sprs[nd]<=20. && totals[0]>0. && totals[1]>0.;
 if(!learned){
  for(int h=threadIdx.x;h<169;h+=blockDim.x){double raw=0.,balanced=0.;
   for(int j=0;j<169;j++){double w=compatible(h,j)/combos(h)/combos(j)*d[(1-side)*169+j];
    raw+=w*eq[j*169+h];balanced+=w*eq[(side?2:1)*169*169+j*169+h];}
   double den=legal(h,d+(1-side)*169,rankmass+(1-side)*13);
   double blend=fmin(1.,fabs((double)rw[(size_t)nd*np+p]-1.)/.08);
   double share=raw+blend*(balanced-raw);
   val[(size_t)slots[nd]*169+h]=(float)(prob/ez*(pots[nd]*share-inv[(size_t)nd*np+p]*den));
  }return;
 }
 // Unchanged frozen feature encoder and compatible-mass centering.
 if(threadIdx.x<2){int s=threadIdx.x;for(int j=0;j<5;j++)desc[s*5+j]=0.;for(int j=0;j<8;j++)summary[s*8+j]=0.;
  double sq=0.,t1=0.,t2=0.,t3=0.;
  for(int h=0;h<169;h++){double v=d[s*169+h];int a=h/13,b=h%13,hi=max(a,b),lo=min(a,b);bool pair=a==b,suit=a>b;
   desc[s*5]+=v*pair;desc[s*5+1]+=v*suit;desc[s*5+2]+=v*(hi+lo)/24.;desc[s*5+3]+=v*(hi==12);desc[s*5+4]+=v*(hi-lo<=2 && !pair);
   if(v>0)summary[s*8]-=v*log(v)/log(169.);sq+=v*v;
   if(v>t1){t3=t2;t2=t1;t1=v;}else if(v>t2){t3=t2;t2=v;}else if(v>t3)t3=v;
   summary[s*8+4]+=v*(pair && hi>=8);summary[s*8+5]+=v*(pair && hi<8);
   summary[s*8+6]+=v*(!suit && !pair && lo>=8);summary[s*8+7]+=v*(suit && hi-lo<=2);
  }summary[s*8+1]=1./(sq*169.);summary[s*8+2]=t1;summary[s*8+3]=t1+t2+t3;
 }
 for(int x=threadIdx.x;x<338;x+=blockDim.x){int s=x/169,h=x%169;double den=0.,num=0.;
  for(int j=0;j<169;j++){double w=compatible(h,j)*d[(1-s)*169+j]/combos(j);den+=w;num+=w*eq[j*169+h];}
  qraw[x]=num/den;mass[x]=d[x]/combos(h)*den;
 }
 __syncthreads();
 for(int x=threadIdx.x;x<338;x+=blockDim.x){int s=x/169,h=x%169,a=h/13,b=h%13,hi=max(a,b),lo=min(a,b);
  double equity=qraw[x],pair=a==b,suited=a>b,high=hi/12.,low=lo/12.,gap=(hi-lo)/12.,ace=hi==12,connected=hi>lo && hi-lo<=2,log_spr=log1p(sprs[nd]);
  // Export substitutes dist references with d, preserving every coefficient.
  correction[x]=__FEATURE_EXPRESSION__;
 }
 __syncthreads();if(threadIdx.x==0){center=0.;for(int x=0;x<338;x++)center+=mass[x]/z*correction[x]/2.;}__syncthreads();
 for(int h=threadIdx.x;h<169;h+=blockDim.x){double pred=qraw[side*169+h]+correction[side*169+h]-center;
  double weight=legal(h,d+(1-side)*169,rankmass+(1-side)*13)/ez;
  val[(size_t)slots[nd]*169+h]=(float)(prob*weight*(pots[nd]*pred-inv[(size_t)nd*np+p]));}
}
