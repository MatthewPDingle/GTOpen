"""Serial registered large-game follow-up, guarded against live user work."""
from run_experiment import run, HERE, ROOT
if __name__=='__main__':
    config=ROOT/'research/autoresearch/passes/03-preflop-20260910/user-session.json'
    # Sampled candidate first to learn whether the smaller-tree result scales.
    run('eight-s128-a',config,'dcfr',128,42,2000,50,3600)
    run('eight-native-a',config,'native',1024,42,2000,50,10800)
    run('eight-s64-a',config,'dcfr',64,42,2000,50,3600)
    run('eight-s128-b',config,'dcfr',128,314159,2000,50,3600)
    fixture=ROOT/'target/autoresearch/preflop-20260910/target/fixtures/fresh-coupled-validated.gtop'
    run('modeled-native-a',fixture,'native',1024,42,1500,50,10800)
    run('modeled-s128-a',fixture,'dcfr',128,42,1500,50,3600)
