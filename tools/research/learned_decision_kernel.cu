// Research-only range-conditioned value inference. Generated feature expression
// is substituted by learned_decisions.py from the frozen candidate JSON.
typedef unsigned int u32;
__device__ double combos(int h) {return h/13==h%13?6.0:h/13>h%13?4.0:12.0;}
__device__ double compatible(int h,int j) {
 int a=h/13,b=h%13,c=j/13,d=j%13;
 int overlap=(a==c)+(c!=d && a==d)+(a!=b && b==c)+(a!=b && c!=d && b==d);
 double ih=a==b?3.0:a>b?1.0:3.0,ij=c==d?3.0:c>d?1.0:3.0;
 return combos(h)*combos(j)-4.0*overlap*ih*ij+(h==j?combos(h):0.0);
}
extern "C" __global__ void learned_terminal(
 const u32* terms,int p,int np,const int* seats,const double* sprs,
 const float* pots,const float* inv,const u32* reach_src,
 const float* reach,const float* reach_mass,const float* eq,
 const u32* val_slot,float* val) {
 u32 k=blockIdx.x,nd=terms[k];int oop=seats[2*k],ip=seats[2*k+1];
 if(p!=oop && p!=ip)return;
 __shared__ double dist[338],qraw[338],mass[338],correction[338],desc[10],summary[16];
 __shared__ double totals[2],z,center,prob;
 if(threadIdx.x==0){
  totals[0]=reach_mass[reach_src[(size_t)nd*np+oop]];
  totals[1]=reach_mass[reach_src[(size_t)nd*np+ip]];
  prob=1.;for(int s=0;s<np;s++)if(s!=p)prob*=reach_mass[reach_src[(size_t)nd*np+s]];
 }
 __syncthreads();
 // Unsupported zero-arrival contexts retain the ordinary terminal value.
 if(totals[0]<=0 || totals[1]<=0 || prob<=0)return;
 for(int x=threadIdx.x;x<338;x+=blockDim.x){int s=x/169,h=x%169,seat=s?ip:oop;
  dist[x]=(double)reach[(size_t)reach_src[(size_t)nd*np+seat]*169+h]/totals[s];
 }
 __syncthreads();
 if(threadIdx.x<2){int s=threadIdx.x;
  for(int j=0;j<5;j++)desc[s*5+j]=0;
  for(int j=0;j<8;j++)summary[s*8+j]=0;
  double sq=0,t1=0,t2=0,t3=0;
  for(int h=0;h<169;h++){double v=dist[s*169+h];int a=h/13,b=h%13,hi=max(a,b),lo=min(a,b);bool pair=a==b,suit=a>b;
   desc[s*5]+=v*pair;desc[s*5+1]+=v*suit;desc[s*5+2]+=v*(hi+lo)/24.;desc[s*5+3]+=v*(hi==12);desc[s*5+4]+=v*(hi-lo<=2 && !pair);
   if(v>0)summary[s*8]-=v*log(v)/log(169.0);sq+=v*v;
   if(v>t1){t3=t2;t2=t1;t1=v;}else if(v>t2){t3=t2;t2=v;}else if(v>t3)t3=v;
   summary[s*8+4]+=v*(pair && hi>=8);summary[s*8+5]+=v*(pair && hi<8);
   summary[s*8+6]+=v*(!suit && !pair && lo>=8);summary[s*8+7]+=v*(suit && hi-lo<=2);
  }summary[s*8+1]=1./(sq*169.);summary[s*8+2]=t1;summary[s*8+3]=t1+t2+t3;
 }
 for(int x=threadIdx.x;x<338;x+=blockDim.x){int s=x/169,h=x%169;double den=0,num=0;
  for(int j=0;j<169;j++){double w=compatible(h,j)*dist[(1-s)*169+j]/combos(j);den+=w;num+=w*eq[j*169+h];}
  qraw[x]=num/den;mass[x]=dist[x]/combos(h)*den;
 }
 __syncthreads();
 if(threadIdx.x==0){z=0;for(int h=0;h<169;h++)z+=mass[h];}
 __syncthreads();
 if(z<=0)return;
 for(int x=threadIdx.x;x<338;x+=blockDim.x){int s=x/169,h=x%169;
  int a=h/13,b=h%13,hi=max(a,b),lo=min(a,b);double equity=qraw[x],pair=a==b,suited=a>b;
  double high=hi/12.,low=lo/12.,gap=(hi-lo)/12.,ace=hi==12,connected=hi>lo && hi-lo<=2,log_spr=log1p(sprs[k]);
  correction[x]=__FEATURE_EXPRESSION__;
 }
 __syncthreads();
 if(threadIdx.x==0){center=0;for(int x=0;x<338;x++)center+=mass[x]/z*correction[x]/2.;}
 __syncthreads();
 for(int h=threadIdx.x;h<169;h+=blockDim.x){int s=p==ip;double pred=qraw[s*169+h]+correction[s*169+h]-center;
  val[(size_t)val_slot[nd]*169+h]=(float)(prob*(pots[nd]*pred-inv[(size_t)nd*np+p]));
 }
}
