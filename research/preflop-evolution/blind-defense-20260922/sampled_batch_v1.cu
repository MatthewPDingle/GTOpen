// Research-only finite-tree reference. Full poker traversal is not implemented.
extern "C" __global__ void sampled_traverse(
 int ns,int nn,const int* actor,const int* arity,const int* child,
 const int* player,const int* info,const int* choice,const int* offset,
 const double* sigma,const double* terminal,double* regret,double* average) {
 int s=blockIdx.x*blockDim.x+threadIdx.x;
 if(s>=ns)return;
 double value[128];int visited[128];
 for(int n=0;n<nn;n++){value[n]=terminal[s*nn+n];visited[n]=0;}
 visited[0]=1;
 // Input topology is checked: every child index is larger than its parent.
 for(int n=0;n<nn;n++)if(visited[n]&&arity[n]) {
   if(actor[n]==player[s])for(int a=0;a<arity[n];a++)visited[child[n*3+a]]=1;
   else visited[child[n*3+choice[s*nn+n]]]=1;
 }
 for(int n=nn-1;n>=0;n--)if(visited[n]&&arity[n]) {
   int base=offset[info[s*nn+n]];
   if(actor[n]==player[s]) {
     double v=0;
     for(int a=0;a<arity[n];a++)v+=sigma[base+a]*value[child[n*3+a]];
     value[n]=v;
     for(int a=0;a<arity[n];a++)regret[(s*nn+n)*3+a]=value[child[n*3+a]]-v;
   } else {
     value[n]=value[child[n*3+choice[s*nn+n]]];
     for(int a=0;a<arity[n];a++)average[(s*nn+n)*3+a]=sigma[base+a];
   }
 }
}

extern "C" __global__ void sampled_reduce(
 int ni,int nn,const int* offsets,const int* csr,const int* entries,
 const double* weights,const double* rd,const double* av,
 const double* old_regret,const double* old_average,
 double* delta,double* increment,double* next_regret,double* next_average,
 double* next_policy,double* average_policy) {
 int i=blockIdx.x*blockDim.x+threadIdx.x;if(i>=ni)return;
 int start=offsets[i],na=offsets[i+1]-start;
 double ps=0,as=0;
 for(int a=0;a<na;a++) {
   double r=0,v=0;
   // No floating-point atomics: stable ordering of all duplicate-key updates.
   for(int j=csr[i];j<csr[i+1];j++) {
     int entry=entries[j];double w=weights[entry/nn];
     r+=w*rd[entry*3+a];v+=w*av[entry*3+a];
   }
   delta[start+a]=r;increment[start+a]=v;
   next_regret[start+a]=old_regret[start+a]+r;
   next_average[start+a]=old_average[start+a]+v;
   ps+=next_regret[start+a]>0?next_regret[start+a]:0;
   as+=next_average[start+a];
 }
 for(int a=0;a<na;a++) {
   double r=next_regret[start+a];
   next_policy[start+a]=ps>0?(r>0?r:0)/ps:1./na;
   average_policy[start+a]=as>0?next_average[start+a]/as:1./na;
 }
}
