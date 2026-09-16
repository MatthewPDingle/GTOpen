// The same range statistics as the serial encoder, reduced within a warp.
__device__ void summary_insert(double v,double& a,double& b,double& c){
 if(v>a){c=b;b=a;a=v;}else if(v>b){c=b;b=v;}else if(v>c)c=v;
}
__device__ void describe_warp(int s,int lane,const double* d,double* desc,double* summary){
 double v0=0.,v1=0.,v2=0.,v3=0.,v4=0.,ent=0.,sq=0.,hp=0.,lp=0.,ob=0.,sc=0.;
 double t1=0.,t2=0.,t3=0.;
 for(int h=lane;h<169;h+=32){
  double v=d[s*169+h];int a=h/13,b=h%13,hi=max(a,b),lo=min(a,b);bool pair=a==b,suit=a>b;
  v0+=v*pair;v1+=v*suit;v2+=v*(hi+lo)/24.;v3+=v*(hi==12);v4+=v*(hi-lo<=2 && !pair);
  if(v>0.)ent-=v*log(v)/log(169.);sq+=v*v;
  hp+=v*(pair && hi>=8);lp+=v*(pair && hi<8);
  ob+=v*(!suit && !pair && lo>=8);sc+=v*(suit && hi-lo<=2);
  summary_insert(v,t1,t2,t3);
 }
 for(int offset=16;offset;offset/=2){
  v0+=__shfl_down_sync(0xffffffff,v0,offset);v1+=__shfl_down_sync(0xffffffff,v1,offset);
  v2+=__shfl_down_sync(0xffffffff,v2,offset);v3+=__shfl_down_sync(0xffffffff,v3,offset);
  v4+=__shfl_down_sync(0xffffffff,v4,offset);ent+=__shfl_down_sync(0xffffffff,ent,offset);
  sq+=__shfl_down_sync(0xffffffff,sq,offset);hp+=__shfl_down_sync(0xffffffff,hp,offset);
  lp+=__shfl_down_sync(0xffffffff,lp,offset);ob+=__shfl_down_sync(0xffffffff,ob,offset);
  sc+=__shfl_down_sync(0xffffffff,sc,offset);
  double u1=__shfl_down_sync(0xffffffff,t1,offset),u2=__shfl_down_sync(0xffffffff,t2,offset),u3=__shfl_down_sync(0xffffffff,t3,offset);
  if(lane+offset<32){summary_insert(u1,t1,t2,t3);summary_insert(u2,t1,t2,t3);summary_insert(u3,t1,t2,t3);}
 }
 if(lane==0){
  desc[s*5]=v0;desc[s*5+1]=v1;desc[s*5+2]=v2;desc[s*5+3]=v3;desc[s*5+4]=v4;
  summary[s*8]=ent;summary[s*8+1]=1./(sq*169.);summary[s*8+2]=t1;summary[s*8+3]=t1+t2+t3;
  summary[s*8+4]=hp;summary[s*8+5]=lp;summary[s*8+6]=ob;summary[s*8+7]=sc;
 }
}
