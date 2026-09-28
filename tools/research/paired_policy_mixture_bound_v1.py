"""A priori payoff-difference bound for shared complete-policy mixtures.

Caller must verify component identities, a common game, and own-history reach
weighting. This helper does not inspect models, evaluate poker, or change an
existing experiment's registered intervals.
"""
from fractions import Fraction
import math
import re


def mixture(references, weights):
    if not references or len(references) != len(weights):
        raise ValueError('Nonempty complete component list and matching weights required')
    result = {}
    for identity, weight in zip(references, weights):
        if not isinstance(identity, str) or not re.fullmatch('[0-9a-f]{64}', identity):
            raise ValueError('Verified policy content identities required')
        if type(weight) is not int or weight <= 0:
            raise ValueError('Fixed positive integer mixture weights required')
        result[identity] = result.get(identity, 0)+weight
    total = sum(result.values())
    return {key: Fraction(value, total) for key, value in result.items()}


def bound(old_ids, old_weights, new_ids, new_weights, *, payoff_lower, payoff_upper):
    """Bound replacing ONE player's mixture against ANY fixed opponent.

    If common normalized component mass is c, cancel it. Each residual has
    mass 1-c and its expected payoff lies between the fixed terminal bounds.
    The absolute paired gain is at most (1-c)*(upper-lower), pointwise in the
    common physical deal. Opponent mixing and chance integration preserve this.
    """
    if (type(payoff_lower) not in (int, float) or type(payoff_upper) not in (int, float)
            or not math.isfinite(payoff_lower) or not math.isfinite(payoff_upper)
            or payoff_lower >= payoff_upper):
        raise ValueError('Fixed finite terminal payoff bounds required')
    a, b = mixture(old_ids, old_weights), mixture(new_ids, new_weights)
    common = sum((min(a.get(k, 0), b.get(k, 0)) for k in a.keys() | b.keys()), Fraction(0))
    changed = 1-common
    width = Fraction(payoff_upper)-Fraction(payoff_lower)
    exact = changed*width
    # Round the rational bound outward; no policy approximation tolerance is
    # invented here. Any numerical implementation allowance belongs in its plan.
    upper = 0. if exact == 0 else math.nextafter(float(exact), math.inf)
    return dict(common_mass_numerator=common.numerator, common_mass_denominator=common.denominator,
        changed_mass_numerator=changed.numerator, changed_mass_denominator=changed.denominator,
        absolute_gain_numerator=exact.numerator, absolute_gain_denominator=exact.denominator,
        absolute_gain_bound=upper,
        assumptions='Verified complete policies; fixed positive weights; own-history realization-weighted average; same game and bounded terminal payoff; one player replaced against a fixed opponent.',
        bounds_best_response_above=False)
