// Exact integer seven-card showdown evaluator; higher values win.
__device__ int pf_straight(unsigned mask) {
 for(int high=12;high>=4;high--)if((mask&(31u<<(high-4)))==(31u<<(high-4)))return high;
 return (mask&0x100fu)==0x100fu?3:-1;
}
__device__ unsigned pf_value(int category,int a=0,int b=0,int c=0,int d=0,int e=0){
 return ((unsigned)category<<20)|((unsigned)a<<16)|((unsigned)b<<12)|((unsigned)c<<8)|((unsigned)d<<4)|(unsigned)e;
}
__device__ void pf_top(unsigned mask,int* top,int needed) {
 int n=0;for(int r=12;r>=0&&n<needed;r--)if(mask&(1u<<r))top[n++]=r;
}
__device__ unsigned pf_eval7(const unsigned char* cards) {
 unsigned mask=0,suits[4]={0,0,0,0};int counts[13]={0};
 for(int i=0;i<7;i++){int r=cards[i]>>2;mask|=1u<<r;suits[cards[i]&3]|=1u<<r;counts[r]++;}
 int flush=-1;for(int i=0;i<4;i++)if(__popc(suits[i])>=5){flush=i;break;}
 if(flush>=0){int st=pf_straight(suits[flush]);if(st>=0)return pf_value(8,st);}
 int quads=-1,trips[2]={-1,-1},pairs[3]={-1,-1,-1},nt=0,np=0;
 for(int r=12;r>=0;r--){if(counts[r]==4)quads=r;else if(counts[r]==3)trips[nt++]=r;else if(counts[r]==2)pairs[np++]=r;}
 int top[5]={0,0,0,0,0};
 if(quads>=0){pf_top(mask&~(1u<<quads),top,1);return pf_value(7,quads,top[0]);}
 if(nt){int pair=nt>1?trips[1]:(np?pairs[0]:-1);if(pair>=0)return pf_value(6,trips[0],pair);}
 if(flush>=0){pf_top(suits[flush],top,5);return pf_value(5,top[0],top[1],top[2],top[3],top[4]);}
 int st=pf_straight(mask);if(st>=0)return pf_value(4,st);
 if(nt){pf_top(mask&~(1u<<trips[0]),top,2);return pf_value(3,trips[0],top[0],top[1]);}
 if(np>=2){pf_top(mask&~(1u<<pairs[0])&~(1u<<pairs[1]),top,1);return pf_value(2,pairs[0],pairs[1],top[0]);}
 if(np){pf_top(mask&~(1u<<pairs[0]),top,3);return pf_value(1,pairs[0],top[0],top[1],top[2]);}
 pf_top(mask,top,5);return pf_value(0,top[0],top[1],top[2],top[3],top[4]);
}
