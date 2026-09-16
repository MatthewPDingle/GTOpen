import unittest
import numpy as np
import continuation_exact_game as game
import continuation_exact_game_offsupport as probe
import continuation_exact_game_robust as robust


class CompletionTests(unittest.TestCase):
    def test_zero_hands_are_best_responses_without_changing_support(self):
        old = game.linprog
        game.linprog = robust.robust_linprog
        try:
            for c in [1, 2]:
                for x, y in [(np.array([0., .3, .7]), np.array([.6, .4, 0.])),
                             (np.array([0., 0., 1.]), np.array([1., 0., 0.])),
                             (np.array([.3, .2, .5]), np.array([.7, .1, .2]))]:
                    _, (p, q), _, _ = probe.original_exact(c, x, y)
                    v, (new_p, new_q), _, _ = probe.completed_exact(c, x, y)
                    np.testing.assert_array_equal(p[x>0], new_p[x>0])
                    np.testing.assert_array_equal(q[y>0], new_q[y>0])
                    for h in np.flatnonzero(x == 0):
                        values = []
                        for action in [0., 1.]:
                            b = new_p.copy(); b[h] = action
                            values.append((game.continuation_matrix(c,b,new_q)*game.LEGAL)[h]@y)
                        self.assertAlmostEqual(v[0,h]*(game.LEGAL@y)[h], max(values), places=10)
                    for h in np.flatnonzero(y == 0):
                        values = []
                        for action in [0., 1.]:
                            b = new_q.copy(); b[h] = action
                            values.append(x@(-game.continuation_matrix(c,new_p,b)*game.LEGAL)[:,h])
                        self.assertAlmostEqual(v[1,h]*(game.LEGAL.T@x)[h], max(values), places=10)
        finally:
            game.linprog = old


if __name__ == '__main__':
    unittest.main()
