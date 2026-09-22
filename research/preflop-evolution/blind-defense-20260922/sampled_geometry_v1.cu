// Appended to the registered postflop_state_v1.cuh by the probe.
extern "C" __global__ void pf_geometry_probe(int count,const double* cfgs,
 const int* branch,const int* lengths,const int* paths,int* integers,double* numbers) {
 int i=blockIdx.x*blockDim.x+threadIdx.x;if(i>=count)return;
 const double* c=cfgs+4*branch[i];PFConfig cfg={c[0],c[1],c[2],c[3]};PFState s=pf_root(cfg);
 for(int k=0;k<8;k++){integers[i*8+k]=0;numbers[i*8+k]=0;}
 for(int d=0;d<lengths[i];d++){
   int step=paths[i*16+d];
   if(s.kind==1&&step==-1)s=pf_deal(s);
   else if(s.kind==0){PFAction a[3];int n=pf_actions(cfg,s,a);
     if(step<0||step>=n){integers[i*8+7]=1;return;}s=pf_act(cfg,s,a[step]);}
   else {integers[i*8+7]=2;return;}
 }
 integers[i*8]=s.kind;integers[i*8+1]=s.player;integers[i*8+2]=s.street;
 numbers[i*8]=s.put[0];numbers[i*8+1]=s.put[1];
 if(s.kind==0){PFAction a[3];int n=pf_actions(cfg,s,a);integers[i*8+3]=n;
   for(int k=0;k<n;k++){integers[i*8+4+k]=a[k].kind;numbers[i*8+5+k]=a[k].to;}}
 if(s.kind==2||s.kind==3)pf_payouts(cfg,s,numbers+i*8+2);
}
