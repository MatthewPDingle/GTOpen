"""Prospective GPU resource prefilter; never a performance/adoption decision.

Reported registers may rise inside an unchanged allocation quantum. The
compute-12.0 model must be sealed to the D094 SDK/driver calibration evidence.
Other hardware requires its own verified model. Historical protocols are frozen.
"""

from __future__ import annotations


def evaluate_pair(baseline: dict, candidate: dict, allocation_proof: dict) -> dict:
    """Compare one compiled kernel at the same fixed dynamic-shared geometry.

    Callers must pin the complete input/proof hashes, verify the actual device,
    ABI, intended changed entries and all other entry bodies, and complete all
    numerical, performance and material-cost gates separately.
    """
    dev = allocation_proof.get("device", {})
    if not (
        allocation_proof.get("status")
        == "pass_same_allocation_quantum_and_driver_occupancy"
        and allocation_proof.get("retained_driver_matches") == 60
        and allocation_proof.get("all1024thread_counts_all10shapes_pairwise_equal")
        is True
        and allocation_proof.get("kernel_launches") == 0
        and (dev.get("major"), dev.get("minor"), dev.get("warp_size"),
             dev.get("register_quantum_per_warp")) == (12, 0, 32, 256)
    ):
        raise ValueError("No calibrated allocation model for this device")

    integer_fields = ("registers", "local_bytes_per_thread", "static_shared_bytes",
                      "dynamic_shared_bytes", "max_threads")
    occupancy = []
    for arm in (baseline, candidate):
        if any(type(arm.get(k)) is not int or arm[k] < 0 for k in integer_fields):
            raise ValueError("Incomplete or invalid compiled-resource attributes")
        if arm["registers"] > 255:
            raise ValueError("Reported registers outside the calibrated device range")
        observed = arm.get("occupancy_by_threads", [])
        if not (
            isinstance(observed, list)
            and len(observed) == 3
            and all(isinstance(v, list) and len(v) == 2
                    and all(type(x) is int and x >= 0 for x in v) for v in observed)
            and [v[0] for v in observed] == [64, 128, 256]
            and type(arm.get("fits_default_limits")) is bool
        ):
            raise ValueError("Missing fixed64/128/256 driver occupancy observations")
        occupancy.append(observed)

    warp = dev["warp_size"]
    quantum = dev["register_quantum_per_warp"]

    def allocated_per_warp(row: dict) -> int:
        nominal = row["registers"] * warp
        return ((nominal + quantum - 1) // quantum) * quantum

    before = allocated_per_warp(baseline)
    after = allocated_per_warp(candidate)
    gates = {
        "allocated_registers_not_increased": after <= before,
        "local_bytes_not_increased": candidate["local_bytes_per_thread"]
        <= baseline["local_bytes_per_thread"],
        "static_shared_not_increased": candidate["static_shared_bytes"]
        <= baseline["static_shared_bytes"],
        "dynamic_shared_not_increased": candidate["dynamic_shared_bytes"]
        <= baseline["dynamic_shared_bytes"],
        "max_threads_not_reduced": candidate["max_threads"] >= baseline["max_threads"],
        "both_fit_default_limits": baseline["fits_default_limits"]
        and candidate["fits_default_limits"],
        "driver_occupancy_not_reduced": all(
            c[1] >= b[1] for b, c in zip(*occupancy)
        ),
    }
    return {
        "status": "admit_numerical_controls" if all(gates.values())
        else "reject_resource_prefilter",
        "gates": gates,
        "nominal_registers": [baseline["registers"], candidate["registers"]],
        "allocated_registers_per_warp": [before, after],
        "allocated_registers_per_block": [
            {"threads": t,
             "baseline": before * ((t + warp - 1) // warp),
             "candidate": after * ((t + warp - 1) // warp)}
            for t in (64, 128, 256)
        ],
        "performance_qualified": False,
        "candidate_accepted": False,
    }
