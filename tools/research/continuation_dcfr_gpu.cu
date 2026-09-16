// Fixture for the full-precision continuation value-transfer expression.
// Three distinct toy cards, not Hold'em classes. Production down/up/discount
// kernels compile separately from their original, unmodified 169-lane source.
extern "C" __global__ void toy_transfer(
    const int* leaves, int count, const int* refs, const float* reach,
    const double* pred, const double* cost, int player, float* val)
{
    if (blockIdx.x >= count) return;
    int n = leaves[blockIdx.x], h = threadIdx.x;
    if (h >= 169) return;
    if (h >= 3) { val[n*169+h] = 0.f; return; }
    const float* opp = reach + refs[n*2+1-player]*169;
    double total = (double)opp[0] + opp[1] + opp[2];
    double legal = 0.;
    if (total > 0.) for (int j=0; j<3; ++j) if (j != h) legal += opp[j]/total;
    double entry_z = 2./3.;
    double pot = cost[n]*2., invested = cost[n];
    // Same normalization/units as N20's full-precision interface; do not clip
    // pot shares to [0,1], since future investments can exceed the entry pot.
    val[n*169+h] = (float)(total*(legal/entry_z)*(pot*pred[n*3+h]-invested));
}
