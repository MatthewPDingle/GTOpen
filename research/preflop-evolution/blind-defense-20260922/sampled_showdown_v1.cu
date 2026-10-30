extern "C" __global__ void pf_showdown_probe(int n,const unsigned char* cards,unsigned* values){
 int i=blockIdx.x*blockDim.x+threadIdx.x;if(i<n)values[i]=pf_eval7(cards+i*7);
}
