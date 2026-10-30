"""Registered-look intervals for IID, bounded, paired policy evaluations.

One observation is a complete paired deal evaluation, never an action record.
Policies and the deal distribution must be frozen independently of these draws.
An interval for a tested deviation is NOT an upper bound on best-response gain.
"""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Plan:
    lower: float
    upper: float
    series: tuple[str, ...]
    looks: tuple[int, ...]
    alpha: float = .05

    def __post_init__(self):
        if not (math.isfinite(self.lower) and math.isfinite(self.upper)
                and self.lower < self.upper and 0 < self.alpha < 1):
            raise ValueError('Invalid fixed bounds or family error probability')
        if not (isinstance(self.series, tuple) and self.series
                and all(isinstance(s, str) and s for s in self.series)
                and len(set(self.series)) == len(self.series)):
            raise ValueError('Declare distinct series before evaluation')
        if not (isinstance(self.looks, tuple) and self.looks
                and all(type(n) is int and n >= 2 for n in self.looks)
                and tuple(sorted(set(self.looks))) == self.looks):
            raise ValueError('Declare increasing sample counts before evaluation')


class PairedEvaluation:
    def __init__(self, plan: Plan, series: str):
        if series not in plan.series:
            raise ValueError('Unregistered series')
        self.plan, self.series = plan, series
        self.count, self.mean, self.m2 = 0, 0., 0.

    def add_difference(self, value: float):
        if not math.isfinite(value) or not self.plan.lower <= value <= self.plan.upper:
            raise ValueError('Nonfinite or out-of-bounds paired deal value')
        if self.count >= self.plan.looks[-1]:
            raise ValueError('Registered sample budget exhausted')
        self.count += 1
        delta = value - self.mean
        self.mean += delta / self.count
        self.m2 += delta * (value - self.mean)

    def merge(self, other):
        """Combine disjoint independent deal batches under the same plan."""
        if other is self or self.plan != other.plan or self.series != other.series:
            raise ValueError('Incompatible evaluation batches')
        total = self.count + other.count
        if total > self.plan.looks[-1]:
            raise ValueError('Registered sample budget exhausted')
        if not other.count:
            return
        delta = other.mean - self.mean
        self.m2 += other.m2 + delta * delta * self.count * other.count / total
        self.mean += delta * other.count / total
        self.count = total

    def interval(self):
        if self.count not in self.plan.looks:
            raise ValueError('Unregistered evaluation look')
        # Maurer & Pontil (2009), Theorem 4, scaled to [lower, upper].
        # Allocate alpha/(2 * series * looks) to each one-sided statement.
        log = math.log(4 * len(self.plan.series) * len(self.plan.looks) / self.plan.alpha)
        variance = max(0., self.m2 / (self.count - 1))
        radius = (math.sqrt(2 * variance * log / self.count)
                  + 7 * (self.plan.upper - self.plan.lower) * log / (3 * (self.count - 1)))
        return dict(count=self.count, mean=self.mean, sample_variance=variance,
                    radius=radius, lower=max(self.plan.lower, self.mean-radius),
                    upper=min(self.plan.upper, self.mean+radius),
                    family_error_probability=self.plan.alpha,
                    bounds_best_response_above=False)
