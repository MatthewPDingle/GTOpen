// Research transition functions for the registered BB experiment only:
// 50% bets/donks, 100% pot raises, one raise/street, no added jam option.
struct PFConfig { double pot,stack,rake,cap; };
struct PFAction { int kind; double to; }; // fold/check/call/bet/raise = 0..4
struct PFState {
 int kind,player,street,raises,aggressor,checked,runout;
 double put[2],bet[2],increment;
};
__device__ PFState pf_root(PFConfig c) {
 PFState s={};s.put[0]=s.put[1]=c.pot/2.;s.aggressor=-1;return s;
}
__device__ int pf_actions(PFConfig c,PFState s,PFAction* a) {
 int me=s.player,opp=1-me;double stack=c.stack-(s.put[me]-c.pot/2.);
 double facing=s.bet[opp]-s.bet[me];
 if(facing>1e-9) {
   a[0]={0,0};a[1]={2,s.bet[opp]};
   if(stack<=facing+1e-9||s.raises>=1)return 2;
   double max_to=s.bet[me]+stack;
   double to=s.bet[opp]+(s.put[0]+s.put[1]+facing);
   double min_to=s.bet[opp]+(s.increment>1e-9?s.increment:1e-9);
   if(to<min_to)to=min_to;
   if(to>=max_to-1e-9||to>=.85*max_to-1e-9)to=max_to;
   if(to>s.bet[opp]+1e-9){a[2]={4,to};return 3;}return 2;
 }
 a[0]={1,0};if(stack<=1e-9)return 1;
 double to=.5*(s.put[0]+s.put[1]);if(to<=1e-9)return 1;
 if(to>=stack-1e-9||to>=.85*stack-1e-9)to=stack;
 a[1]={3,to};return 2;
}
__device__ PFState pf_end(PFState s,int aggressor,int allin) {
 if(s.street==2){s.kind=3;s.player=0;return s;}
 s.kind=1;s.street++;s.player=0;s.bet[0]=s.bet[1]=0;s.increment=0;
 s.raises=0;s.aggressor=aggressor;s.checked=0;s.runout=allin;return s;
}
__device__ PFState pf_act(PFConfig c,PFState s,PFAction a) {
 int me=s.player,opp=1-me;
 if(a.kind==0){s.kind=2;return s;}
 if(a.kind==1){if(s.checked)return pf_end(s,-1,0);s.player^=1;s.checked=1;return s;}
 if(a.kind==2){s.put[me]+=a.to-s.bet[me];double total=c.stack+c.pot/2.;
   return pf_end(s,opp,(total-s.put[me]<=1e-9||total-s.put[opp]<=1e-9));}
 double prior=s.bet[opp]>s.bet[me]?s.bet[opp]:s.bet[me];
 s.put[me]+=a.to-s.bet[me];s.bet[me]=a.to;
 double increment=a.to-prior;if(increment>s.increment)s.increment=increment;
 s.raises+=(a.kind==4);s.player^=1;return s;
}
__device__ PFState pf_deal(PFState s) {
 if(s.runout){if(s.street==2)s.kind=3;else s.street++;}else s.kind=0;return s;
}
__device__ void pf_payouts(PFConfig c,PFState s,double* out) {
 double amount=s.kind==2?s.put[s.player]:s.put[0];
 double rake=c.rake*2.*amount;if(c.cap>0&&rake>c.cap)rake=c.cap;
 out[0]=amount-rake;out[1]=-amount;out[2]=s.kind==3?-rake/2.:0;
}
