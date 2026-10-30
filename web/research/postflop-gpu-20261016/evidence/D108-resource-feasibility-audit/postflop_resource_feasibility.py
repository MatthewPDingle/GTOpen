"""Prospective feasibility screen; resource differences remain warnings, never adoption."""
from postflop_resource_admission import evaluate_pair

def evaluate_feasibility(baseline: dict, candidate: dict, proof: dict) -> dict:
    """Caller separately verifies ABI, mechanism, every legal input and actual costs."""
    diagnostic = evaluate_pair(baseline, candidate, proof)
    gates = {
        "local_bytes_not_increased": candidate["local_bytes_per_thread"] <= baseline["local_bytes_per_thread"],
        "dynamic_shared_not_increased": candidate["dynamic_shared_bytes"] <= baseline["dynamic_shared_bytes"],
        "max_threads_not_reduced": candidate["max_threads"] >= baseline["max_threads"],
        "supports_all_fixed_thread_controls": min(baseline["max_threads"], candidate["max_threads"]) >= 256,
        "both_fit_default_limits": baseline["fits_default_limits"] and candidate["fits_default_limits"],
        "positive_fixed_driver_occupancy": all(x[1] > 0 for arm in (baseline, candidate) for x in arm["occupancy_by_threads"]),
    }
    return {
        "status": "admit_numerical_controls" if all(gates.values()) else "reject_infeasible_resources",
        "gates": gates,
        "prior_strict_allocation_diagnostic": diagnostic,
        "resource_warnings": [k for k, v in diagnostic["gates"].items() if not v],
        "performance_qualified": False,
        "candidate_accepted": False,
    }
