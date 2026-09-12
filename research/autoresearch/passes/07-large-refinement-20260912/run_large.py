from run07 import HERE,LAB,RAW,run,digest
import json,shutil
if __name__=='__main__':
    exe=LAB/'target/release/examples/convergence_refine_large.exe'
    local=LAB/'target/release/examples/convergence_local.exe'
    for label,source_name,audit in [
        ('native','eight-native-a',HERE.parent/'05-preflop-convergence-20260911/raw/eight-native-a-local-v3.json'),
        ('sampled','followup-eight-gamma15-s64-42',HERE.parent/'06-preflop-followup-20260911/raw/followup-eight-gamma15-s64-42-local-v3.json')]:
        source=LAB/'target/convergence'/source_name/'final.gtop'
        name=f'large-eight-{label}-local1000'
        out=LAB/'target/convergence'/name
        run(name,[exe,source,audit,'1000',out],3600,[source,audit])
        shutil.copyfile(out/'result.json',RAW/f'{name}-result.json')
        shutil.copyfile(out/'plan.json',RAW/f'{name}-plan.json')
        ref=LAB/'target/convergence/eight-native-a/final.gtop'
        run(name+'-local',[local,out/'final.gtop',ref,RAW/f'{name}-local-v3.json'],600,[out/'final.gtop',ref])
