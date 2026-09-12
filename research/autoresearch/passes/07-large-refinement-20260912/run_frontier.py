"""Read-only GPU frontier diagnosis after retained comparisons are terminal."""
from run07 import *
if __name__=='__main__':
    for variant in ('sampled','native'):
        p=json.loads((RAW/f'large-eight-{variant}-joint-retained-v1-broad-exit.json').read_text())
        if p['returncode'] or p['reason']:raise RuntimeError('Retained comparison not complete')
    run('frontier-tests-v2',['cargo','test','--release','-p','solver','--features','preflop-research',
        '--lib','frontier_gpu_values_match','--','--nocapture','--test-threads=1'],600)
    run('frontier-build-v1',['cargo','build','--release','-p','solver','--features','preflop-research',
        '--example','convergence_frontier'])
    exe=LAB/'target/release/examples/convergence_frontier.exe'
    for source_name,name in [('followup-eight-gamma15-s64-42','sampled-original'),
        ('large-eight-sampled-compact-v1','sampled-compact'),
        ('large-eight-sampled-joint-retained-v1','sampled-retained'),
        ('large-eight-native-joint-retained-v1','native-retained')]:
        source=LAB/'target/convergence'/source_name/'final.gtop'
        run('frontier-'+name+'-v1',[exe,source,HERE/'broad-paths.json',RAW/('frontier-'+name+'-v1.json')],
            240,[source,HERE/'broad-paths.json'])
