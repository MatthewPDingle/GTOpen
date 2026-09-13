"""D05 read-only wider-cohort inventory, serial and live-app guarded."""
import json,re,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'07-large-refinement-20260912'))
import run07
run07.RAW=HERE/'raw'
def main():
    run07.run('d05-cohort-tests-v2',['cargo','test','--release','-p','solver','--features','gpu,preflop-research',
        '--lib','cross_player_inventory','--','--nocapture','--test-threads=1'],240,[HERE/'D05_PROTOCOL.md'])
    log=(run07.RAW/'d05-cohort-tests-v2.log').read_text()
    assert '2 passed; 0 failed; 1 ignored' in log
    exe=run07.LAB/re.search(r'Running unittests .*?\(([^)]+\.exe)\)',log).group(1)
    for fixture,save in [('small','behavioral-fixed-e0-v1'),('large','eight-native-a')]:
        source=run07.LAB/'target/convergence'/save/'final.gtop'
        eq=run07.LAB/'cache/preflop_eq169.bin';fit=run07.LAB/'cache/realization_fit.json'
        name=f'd05-{fixture}-v1';out=run07.RAW/(name+'.json')
        run07.run(name,[exe,'preflop::gpu::cross_player_inventory::cross_player_inventory_from_saved_state',
            '--exact','--ignored','--nocapture','--test-threads=1'],180,[source,eq,fit,HERE/'D05_PROTOCOL.md',exe],
            {'PREFLOP_GPU_REUSE_INPUT':str(source),'PREFLOP_GPU_REUSE_OUTPUT':str(out),'PREFLOP_GPU_REUSE_EQUITY':str(eq),
            'PREFLOP_GPU_LAYOUT_STATS':'1','PREFLOP_GPU_COHORT_INVENTORY':'1','REALIZATION_FIT':str(fit)})
        x=json.loads(out.read_text())
        old=json.loads((run07.RAW/f'd04-{fixture}-v1.json').read_text())
        for k in ['input','players','nodes','iteration','batch','rows','baseline_cdf_rows','all_player_union','pairs',
            'same_source_rechecks','source_identities','all_static_union','buffer_bytes','base_bytes','retained_c01_bytes',
            'best_pairing','natural_pairing','all_pairings']:
            assert x[k]==old[k],(fixture,k)
        print(json.dumps({'fixture':fixture,'cohorts':x['cohorts']['selected_static_plan'],'admitted':x['cohorts']['admitted']}),flush=True)
if __name__=='__main__':main()
