extern "C" __global__ void compatible_cfr(
    const float* av, const float* bv, float* out, int iterations) {
    const int n=169, h=threadIdx.x, game=blockIdx.x;
    const float* a=av+game*n;
    const float* b=bv+game*n*n;
    __shared__ float x[169], y[169];
    float rf=0.f,rj=0.f,sf=0.f,sc=0.f,sx=0.f,sy=0.f;
    if(h<n){x[h]=.5f;y[h]=.5f;}
    __syncthreads();
    for(int t=1;t<=iterations;++t){
        if(h<n){
            float u=a[h];
            for(int j=0;j<n;++j)u+=b[h*n+j]*y[j];
            const float p=x[h];
            rf=fmaxf(0.f,rf-p*u);rj=fmaxf(0.f,rj+(1.f-p)*u);
            x[h]=(rf+rj)>0.f?rj/(rf+rj):.5f;
        }
        __syncthreads();
        if(h<n){
            float u=0.f;
            for(int i=0;i<n;++i)u-=b[i*n+h]*x[i];
            const float p=y[h];
            sf=fmaxf(0.f,sf-p*u);sc=fmaxf(0.f,sc+(1.f-p)*u);
            y[h]=(sf+sc)>0.f?sc/(sf+sc):.5f;
            sx+=t*x[h];sy+=t*y[h];
        }
        __syncthreads();
    }
    if(h<n){
        const float total=.5f*iterations*(iterations+1.f);
        out[game*338+h]=sx/total;
        out[game*338+169+h]=sy/total;
    }
}
