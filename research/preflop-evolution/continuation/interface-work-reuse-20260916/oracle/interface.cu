// Frozen model 83f23c43b18bdb6cf4c461ee7435b7a2d3c4ce24d6a43d4e012e07a200d650ac
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
  correction[x]=-0.50514721569124788
+(0.00020559759081685048)*(1.0)
+(-0.18466969744640105)*(equity)
+(1.318312318109691)*((equity*equity))
+(-0.018124136817192257)*(pair)
+(0.084084898791450133)*(suited)
+(-0.031953781512962534)*(high)
+(-0.026062917851732748)*(low)
+(0.0031346092352737653)*(gap)
+(0.017232107253317239)*(ace)
+(0.028057455248446626)*(connected)
+(0.38140340949857932)*((equity*pair))
+(-0.057889968807813302)*((equity*suited))
+(0.11511124179693807)*(((double)s))
+(0.16073342190651613)*(log_spr)
+(0.17811256198656339)*(desc[s*5+0])
+(-0.091663664514508372)*(desc[s*5+1])
+(0.70566902643579832)*(desc[s*5+2])
+(-0.086332335730141999)*(desc[s*5+3])
+(-0.25337858650912282)*(desc[s*5+4])
+(0.04882126539586084)*(desc[(1-s)*5+0])
+(-0.0045479951117381578)*(desc[(1-s)*5+1])
+(0.098830185588627689)*(desc[(1-s)*5+2])
+(-0.16991853910341909)*(desc[(1-s)*5+3])
+(0.087264278291657588)*(desc[(1-s)*5+4])
+(-0.070729571041616285)*((equity*((double)s)))
+(-0.35336172905548008)*((equity*log_spr))
+(-0.39558288129625407)*((equity*desc[s*5+0]))
+(-0.37381007308465725)*((equity*desc[(1-s)*5+0]))
+(-1.0782125705733974)*((equity*desc[s*5+2]))
+(1.0511333465440411)*((equity*desc[(1-s)*5+2]))
+(-0.037302366885673725)*((pair*((double)s)))
+(-0.06479506883511936)*((pair*log_spr))
+(-0.070514927915439896)*((pair*desc[s*5+0]))
+(-0.029939548328579698)*((pair*desc[(1-s)*5+0]))
+(-0.15008090092813711)*((pair*desc[s*5+2]))
+(0.16606772261731903)*((pair*desc[(1-s)*5+2]))
+(-0.0057161837145283147)*((suited*((double)s)))
+(0.019311640793749422)*((suited*log_spr))
+(-0.034121095152276071)*((suited*desc[s*5+0]))
+(0.015152478418964355)*((suited*desc[(1-s)*5+0]))
+(0.082791552896430864)*((suited*desc[s*5+2]))
+(-0.1087748594298618)*((suited*desc[(1-s)*5+2]))
+(-0.03456762156954412)*((low*((double)s)))
+(0.037074408040519091)*((low*log_spr))
+(0.17714972801975679)*((low*desc[s*5+0]))
+(-0.046103846606006832)*((low*desc[(1-s)*5+0]))
+(-0.13523598668563799)*((low*desc[s*5+2]))
+(0.023919456313101932)*((low*desc[(1-s)*5+2]))
+(0.0010549860688718782)*((ace*((double)s)))
+(0.0044321101501016268)*((ace*log_spr))
+(0.10791933912280081)*((ace*desc[s*5+0]))
+(0.056193393421437143)*((ace*desc[(1-s)*5+0]))
+(-0.00054911891334712213)*((ace*desc[s*5+2]))
+(-0.1491286056260272)*((ace*desc[(1-s)*5+2]))
+(-0.16209108755670804)*(summary[s*8+0])
+(0.63151846806887446)*((summary[s*8+0]*equity))
+(0.46517871671927191)*((summary[s*8+0]*pair))
+(-0.26627444587731725)*(summary[s*8+1])
+(-0.15308085322109091)*((summary[s*8+1]*equity))
+(-0.42708267982394971)*((summary[s*8+1]*pair))
+(0.040799883097949595)*(summary[s*8+2])
+(0.11547437694809116)*((summary[s*8+2]*equity))
+(0.11410150895939045)*((summary[s*8+2]*pair))
+(0.17222757454375448)*(summary[s*8+3])
+(-0.34748745116608099)*((summary[s*8+3]*equity))
+(-0.15683246759281802)*((summary[s*8+3]*pair))
+(0.12898419527398869)*(summary[s*8+4])
+(-0.30078804538208265)*((summary[s*8+4]*equity))
+(-0.06357087922857356)*((summary[s*8+4]*pair))
+(0.16217652617795886)*(summary[s*8+5])
+(-0.60165627369150465)*((summary[s*8+5]*equity))
+(-0.23965275972119285)*((summary[s*8+5]*pair))
+(-0.3389950119131005)*(summary[s*8+6])
+(0.45989769234815886)*((summary[s*8+6]*equity))
+(0.38921977051606654)*((summary[s*8+6]*pair))
+(-0.078836547798726384)*(summary[s*8+7])
+(0.66307996946537562)*((summary[s*8+7]*equity))
+(0.22069143966539953)*((summary[s*8+7]*pair))
+(-0.25046712414813005)*(summary[(1-s)*8+0])
+(-0.1579128537069007)*((summary[(1-s)*8+0]*equity))
+(-0.050897100967743518)*((summary[(1-s)*8+0]*pair))
+(0.56859877265281056)*(summary[(1-s)*8+1])
+(-0.11445398409236997)*((summary[(1-s)*8+1]*equity))
+(-0.066304047302488497)*((summary[(1-s)*8+1]*pair))
+(0.46381746065637691)*(summary[(1-s)*8+2])
+(-0.16070814669575947)*((summary[(1-s)*8+2]*equity))
+(0.1040158291865763)*((summary[(1-s)*8+2]*pair))
+(0.011505603631783148)*(summary[(1-s)*8+3])
+(-0.27796523057732037)*((summary[(1-s)*8+3]*equity))
+(-0.18344858070155354)*((summary[(1-s)*8+3]*pair))
+(-0.004093484177211169)*(summary[(1-s)*8+4])
+(-0.27346676102098427)*((summary[(1-s)*8+4]*equity))
+(0.01108764841618474)*((summary[(1-s)*8+4]*pair))
+(0.66390648411395592)*(summary[(1-s)*8+5])
+(-0.54126947347764731)*((summary[(1-s)*8+5]*equity))
+(-0.65357287906354111)*((summary[(1-s)*8+5]*pair))
+(-0.19875615248053732)*(summary[(1-s)*8+6])
+(0.31747468870061724)*((summary[(1-s)*8+6]*equity))
+(-0.22591766530991103)*((summary[(1-s)*8+6]*pair))
+(-0.49340405254073783)*(summary[(1-s)*8+7])
+(0.7899069613914248)*((summary[(1-s)*8+7]*equity))
+(-0.13260501286187762)*((summary[(1-s)*8+7]*pair))
+(-0.24508119447807139)*(d[x])
+(0.084960786747226485)*(d[(1-s)*169+h])
;
 }
 __syncthreads();if(threadIdx.x==0){center=0.;for(int x=0;x<338;x++)center+=mass[x]/z*correction[x]/2.;}__syncthreads();
 for(int h=threadIdx.x;h<169;h+=blockDim.x){double pred=qraw[side*169+h]+correction[side*169+h]-center;
  double weight=legal(h,d+(1-side)*169,rankmass+(1-side)*13)/ez;
  val[(size_t)slots[nd]*169+h]=(float)(prob*weight*(pots[nd]*pred-inv[(size_t)nd*np+p]));}
}
