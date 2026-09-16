import copy
import unittest
from unittest.mock import patch
import numpy as np
import continuation_shrunk_gpu as gpu


class ShrunkGpuChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=gpu.study.read(gpu.shrunk.OUT/'candidate.json')
        cls.counts,cls.eq=gpu.study.pilot.matrices()

    def contexts(self):
        rng=np.random.default_rng(20260916)
        for alpha,spr in [(.03,1),(1.,8),(10.,20)]:
            w=rng.dirichlet(np.full(169,alpha),size=2)
            case=dict(weights=w.tolist(),pot=20.,stack=20.*spr)
            c=gpu.study.pilot.context(case,self.counts,self.eq)
            c.update(case=case,base_x=c['x'].copy(),base_names=list(c['names']))
            yield c

    def test_folded_standardization_matches_clipped_network_and_centering(self):
        before=copy.deepcopy(self.model);net=gpu.folded_network(self.model)
        for c in self.contexts():
            encoded=gpu.study.fit.features(c,self.model['base']['encoder'])
            clipped=np.clip(encoded['x'],net['low'],net['high'])
            raw=np.maximum(0,clipped@net['weights']+net['bias'])@net['output']
            actual=gpu.study.fit.predict(c,self.model['base'])+raw-(raw*c['mass']).sum()/2
            expected=gpu.shrunk.network.predict(c,self.model)
            np.testing.assert_allclose(actual,expected,atol=2e-12,rtol=0)
            self.assertLess(abs(float((actual*c['mass']).sum()-1)),2e-12)
        self.assertEqual(self.model,before)

    def test_rendered_streaming_network_matches_frozen_cpu_network(self):
        block,expression=gpu.neural_block(self.model)
        lines=[line.replace('double ','').replace('{','').replace('}','').replace(';','').strip()
            for line in block.splitlines()]
        code=compile('\n'.join(lines).replace('((double)s)','float(s)'),'<generated neural block>','exec')
        net=gpu.folded_network(self.model)
        for c in self.contexts():
            encoded=gpu.study.fit.features(c,self.model['base']['encoder']);index={n:i for i,n in enumerate(encoded['names'])}
            d=gpu.study.fit.distribution(c).reshape(-1)
            desc=np.array([[encoded['x'][s,0,index['own_'+n]] for n in ['pairs','suited','ranks','aces','connected']] for s in range(2)]).reshape(-1)
            summary=np.array([[encoded['x'][s,0,index['own_'+n]] for n in ['entropy','effective','maximum','top3','high_pairs','low_pairs','offsuit_broadway','suited_connected']] for s in range(2)]).reshape(-1)
            target=np.maximum(0,np.clip(encoded['x'],net['low'],net['high'])@net['weights']+net['bias'])@net['output']
            for s in range(2):
                for h in [0,12,14,83,168]:
                    a,b=divmod(h,13);hi=max(a,b);lo=min(a,b)
                    scope=dict(fmin=min,fmax=max,float=float,d=d,desc=desc,summary=summary,s=s,h=h,x=s*169+h,
                        equity=float(c['raw'][s,h]),pair=float(a==b),suited=float(a>b),high=hi/12.,low=lo/12.,
                        gap=(hi-lo)/12.,ace=float(hi==12),connected=float(hi>lo and hi-lo<=2),log_spr=float(np.log1p(c['case']['stack']/c['case']['pot'])))
                    exec(code,{'__builtins__':{}},scope)
                    actual=eval(expression,{'__builtins__':{}},scope)
                    self.assertAlmostEqual(actual,float(target[s,h]),delta=2e-12)

    def test_gpu_execution_refuses_a_failed_accuracy_screen(self):
        with patch.object(gpu.evaluation,'registered',return_value=None),patch.object(gpu.study,'read',return_value=dict(accuracy_screen_passed=False)):
            with self.assertRaisesRegex(AssertionError,'pass registered accuracy'):
                gpu.qualified()

    def test_gpu_execution_refuses_the_pending_n15_queue(self):
        import continuation_night_queue as queue
        with patch.object(gpu,'qualified',return_value=None),patch.object(gpu.evaluation,'require_queue_idle',return_value=None),patch.object(queue,'processes',return_value=[
                dict(ProcessId=-1,Name='python.exe',CommandLine='python continuation_shrunk_queue.py 44092')]):
            with self.assertRaisesRegex(AssertionError,'controller is active'):
                gpu.command([],None)


if __name__=='__main__':unittest.main()
