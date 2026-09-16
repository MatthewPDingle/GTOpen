// Fixed 256-thread interface launch. Every thread must enter this function.
__device__ double pair_block_sum(double value){
 __shared__ double partial[8];
 int lane=threadIdx.x%32,warp=threadIdx.x/32;
 for(int offset=16;offset;offset/=2)value+=__shfl_down_sync(0xffffffff,value,offset);
 if(lane==0)partial[warp]=value;
 __syncthreads();
 if(warp==0){
  value=lane<8?partial[lane]:0.;
  for(int offset=16;offset;offset/=2)value+=__shfl_down_sync(0xffffffff,value,offset);
  if(lane==0)partial[0]=value;
 }
 __syncthreads();
 return partial[0];
}
// Pair incidence is 3/6; suited and offsuit incidence are 1/4 and 3/12.
// One thread sums the 25 classes that contain one particular rank.
__device__ double pair_rank_mass(int rank,const double* d){
 double value=.5*d[rank*14];
 for(int other=0;other<13;other++)if(other!=rank){
  value+=.25*d[rank*13+other];
  value+=.25*d[other*13+rank];
 }
 return value;
}
