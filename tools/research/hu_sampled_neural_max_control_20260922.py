"""Isolated highest-regret fallback variant of the frozen neural control.

Architecture, sampling, fitting, averaging, seeds and budgets are unchanged.
The only changed inference rule is used when no legal advantage is positive.
The initial uniform policy is retained to match the registered v1 comparison.
"""
import hu_sampled_neural_control_20260922 as baseline
from hu_sampled_neural_fallback_20260922 import highest_regret_fallback,check


if __name__=='__main__':
    check()
    baseline.regret_policy=highest_regret_fallback
    baseline.main()
