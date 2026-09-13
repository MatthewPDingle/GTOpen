"""Guarded C19 standalone prefix/compiler qualification only."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'07-large-refinement-20260912'))
import run07
run07.RAW=HERE/'raw'
if __name__=='__main__':
    run07.run('c19-prefix-v1',['cargo','test','--release','-p','solver','--features','gpu,preflop-research',
        '--lib','preflop::gpu::cdf_interleave::interleaved_writer_matches_retained_prefix',
        '--','--exact','--ignored','--nocapture','--test-threads=1'],300,
        [HERE/'C19_PROTOCOL.md',HERE/'prepare_c19.py',Path(__file__),HERE/'artifacts/c19-v1-source-map.json'],
        {'PREFLOP_GPU_CDF_INTERLEAVE_OUTPUT':str(HERE/'raw/c19-prefix-v1')})
