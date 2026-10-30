struct E106LockArg<'a>(&'a CudaSlice<i64>, bool);
unsafe impl<'a, 'b: 'a> PushKernelArg<E106LockArg<'b>> for cudarc::driver::LaunchArgs<'a> {
    #[inline(always)]
    fn arg(&mut self, value: E106LockArg<'b>) -> &mut Self {
        if value.1 {
            static ABSENT: sys::CUdeviceptr = 0;
            self.arg(&ABSENT)
        } else {
            self.arg(value.0)
        }
    }
}

