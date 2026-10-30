"""D064 capture/instantiate metadata inspection; root-authorized execution only."""
import argparse
import ctypes as C
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
from datetime import datetime, timezone

DLL_PATH = r"C:\Windows\System32\nvcuda.dll"
EXPECTED_UUID = "a5459b5a632b3e73d7f1a06e167102ee"
PTX_SHA256 = "5bcf5832f6e52ab195efbfafea6013273f64066c9620cdeaa02e0be081ec7dc4"
ATTRIBUTES = {"compute_capability_major": 75, "compute_capability_minor": 76,
              "l2_cache_bytes": 38, "max_persisting_l2_cache_bytes": 108,
              "max_access_policy_window_bytes": 109}


class CUuuid(C.Structure):
    _fields_ = [("bytes", C.c_ubyte * 16)]


class AccessPolicyWindow(C.Structure):
    _fields_ = [("base_ptr", C.c_void_p), ("num_bytes", C.c_size_t),
                ("hitRatio", C.c_float), ("hitProp", C.c_uint),
                ("missProp", C.c_uint)]


class AttributeValue(C.Union):
    _fields_ = [("pad", C.c_char * 64), ("accessPolicyWindow", AccessPolicyWindow)]


def window_fields(value):
    w = value.accessPolicyWindow
    return {"base_ptr": w.base_ptr or 0, "num_bytes": w.num_bytes,
            "hit_ratio_bits": struct.unpack("<I", struct.pack("<f", w.hitRatio))[0],
            "hit_property": w.hitProp, "miss_property": w.missProp}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture-only", action="store_true", required=True)
    parser.parse_args()
    report = {"id": "D064", "pid": os.getpid(), "device_ordinal": 0,
              "started_at": datetime.now(timezone.utc).isoformat(),
              "calls": [], "errors": [], "values": {}, "cleanup": {},
              "captured_kernel_launch_calls": 0, "graph_replays": 0,
              "eager_kernel_launches": 0, "performance_measurement": False,
              "solver_graph_tested": False, "candidate_accepted": False,
              "context_scope": "This isolated process's retained primary context only.",
              "interpretation": "Retained graph-node policy metadata after capture and instantiation only; no executable replay, physical cache, numerical or speed proof."}
    funcs = {}
    device = None
    previous, context = C.c_void_p(), C.c_void_p()
    allocation = C.c_uint64()
    module, function, stream = C.c_void_p(), C.c_void_p(), C.c_void_p()
    graph, executable = C.c_void_p(), C.c_void_p()
    retained = bound = capturing = False
    owns_allocation = owns_module = owns_stream = False
    inspected = False

    def check(condition, message):
        if not condition:
            raise RuntimeError(message)

    def invoke(name, *args, purpose=None):
        row = {"api": name, "return_code": None}
        if purpose is not None:
            row["purpose"] = purpose
        try:
            row["return_code"] = int(funcs[name](*args))
        except Exception as exc:
            row["error"] = repr(exc)
        report["calls"].append(row)
        return row["return_code"]

    def need(name, *args, purpose=None):
        check(invoke(name, *args, purpose=purpose) == 0, name + " failed; no fallback")

    def integer(name, key, *tail):
        value = C.c_int()
        rc = invoke(name, C.byref(value), *tail, purpose=key)
        report["values"][key] = value.value if rc == 0 else None
        check(rc == 0, name + " failed for " + key)
        return value.value

    try:
        check(os.name == "nt" and C.sizeof(C.c_void_p) == 8, "Requires 64-bit Windows")
        layout = {name: getattr(AccessPolicyWindow, name).offset
                  for name, _ in AccessPolicyWindow._fields_}
        check(layout == {"base_ptr": 0, "num_bytes": 8, "hitRatio": 16,
                         "hitProp": 20, "missProp": 24}, "Unexpected APW field ABI")
        check(C.sizeof(AccessPolicyWindow) == 32 and C.alignment(AccessPolicyWindow) == 8
              and C.sizeof(AttributeValue) == 64 and C.alignment(AttributeValue) == 8,
              "Unexpected attribute union ABI")
        report["abi"] = {"window_size": 32, "union_size": 64, "alignment": 8,
                         "window_offsets": layout}
        ptx = Path(__file__).with_name("copy.ptx").read_bytes()
        report["ptx_sha256"] = hashlib.sha256(ptx).hexdigest()
        check(report["ptx_sha256"] == PTX_SHA256, "PTX input pin mismatch")
        image = C.create_string_buffer(ptx)
        pi, pp, ps = C.POINTER(C.c_int), C.POINTER(C.c_void_p), C.POINTER(C.c_size_t)
        pa = C.POINTER(AttributeValue)
        signatures = {
            "cuInit": [C.c_uint], "cuDriverGetVersion": [pi], "cuDeviceGetCount": [pi],
            "cuDeviceGet": [pi, C.c_int],
            "cuDeviceGetName": [C.POINTER(C.c_char), C.c_int, C.c_int],
            "cuDeviceGetUuid_v2": [C.POINTER(CUuuid), C.c_int],
            "cuDeviceGetAttribute": [pi, C.c_int, C.c_int],
            "cuCtxGetCurrent": [pp], "cuDevicePrimaryCtxRetain": [pp, C.c_int],
            "cuCtxSetCurrent": [C.c_void_p], "cuCtxGetLimit": [ps, C.c_int],
            "cuDevicePrimaryCtxRelease_v2": [C.c_int],
            "cuMemAlloc_v2": [C.POINTER(C.c_uint64), C.c_size_t],
            "cuMemFree_v2": [C.c_uint64],
            "cuModuleLoadData": [pp, C.c_void_p],
            "cuModuleGetFunction": [pp, C.c_void_p, C.c_char_p],
            "cuModuleUnload": [C.c_void_p],
            "cuStreamCreate": [pp, C.c_uint], "cuStreamDestroy_v2": [C.c_void_p],
            "cuStreamGetAttribute": [C.c_void_p, C.c_int, pa],
            "cuStreamSetAttribute": [C.c_void_p, C.c_int, pa],
            "cuStreamBeginCapture_v2": [C.c_void_p, C.c_int],
            "cuStreamIsCapturing": [C.c_void_p, pi],
            "cuStreamEndCapture": [C.c_void_p, pp],
            "cuLaunchKernel": [C.c_void_p, C.c_uint, C.c_uint, C.c_uint,
                               C.c_uint, C.c_uint, C.c_uint, C.c_uint,
                               C.c_void_p, pp, pp],
            "cuGraphInstantiateWithFlags": [pp, C.c_void_p, C.c_ulonglong],
            "cuGraphGetNodes": [C.c_void_p, pp, ps],
            "cuGraphNodeGetType": [C.c_void_p, pi],
            "cuGraphKernelNodeGetAttribute": [C.c_void_p, C.c_int, pa],
            "cuGraphExecDestroy": [C.c_void_p], "cuGraphDestroy": [C.c_void_p],
        }
        dll = C.WinDLL(DLL_PATH)
        # Resolve every cleanup symbol before creating any owned driver resource.
        for name, argtypes in signatures.items():
            fn = getattr(dll, name)
            fn.argtypes, fn.restype = argtypes, C.c_int
            funcs[name] = fn
        need("cuInit", 0)
        integer("cuDriverGetVersion", "driver_version")
        check(integer("cuDeviceGetCount", "device_count") == 1, "Expected one fixed device")
        device = integer("cuDeviceGet", "device_handle", 0)
        name = C.create_string_buffer(256)
        need("cuDeviceGetName", name, len(name), device)
        report["values"]["name"] = name.value.decode("utf-8", errors="replace")
        uuid = CUuuid()
        need("cuDeviceGetUuid_v2", C.byref(uuid), device)
        report["values"]["uuid_hex"] = bytes(uuid.bytes).hex()
        check(report["values"]["uuid_hex"] == EXPECTED_UUID, "Unexpected device UUID")
        for key, attr in ATTRIBUTES.items():
            integer("cuDeviceGetAttribute", key, attr, device)
        v = report["values"]
        check(v["compute_capability_major"] >= 8 and v["l2_cache_bytes"] >= 128
              and v["max_persisting_l2_cache_bytes"] >= 128
              and v["max_access_policy_window_bytes"] >= 128, "Insufficient capabilities")
        need("cuCtxGetCurrent", C.byref(previous))
        need("cuDevicePrimaryCtxRetain", C.byref(context), device)
        retained = True
        check(bool(context.value), "Null retained context")
        need("cuCtxSetCurrent", context, purpose="bind owned process context")
        bound = True
        limit = C.c_size_t()
        need("cuCtxGetLimit", C.byref(limit), 6)
        v["current_context_persisting_l2_limit_bytes"] = limit.value
        check(128 <= limit.value <= v["max_persisting_l2_cache_bytes"], "Current limit outside required bounds")

        need("cuMemAlloc_v2", C.byref(allocation), 256)
        owns_allocation = True
        report["allocation"] = {"base_ptr": allocation.value, "bytes": 256}
        check(allocation.value != 0 and allocation.value % 256 == 0, "Unexpected allocation alignment")
        need("cuModuleLoadData", C.byref(module), image)
        owns_module = True
        check(bool(module.value), "Null module")
        need("cuModuleGetFunction", C.byref(function), module, b"d064_copy")
        check(bool(function.value), "Null function")
        need("cuStreamCreate", C.byref(stream), 1)
        owns_stream = True
        check(bool(stream.value), "Null stream")
        initial = AttributeValue()
        need("cuStreamGetAttribute", stream, 1, C.byref(initial), purpose="new stream policy")
        report["initial_stream_window"] = window_fields(initial)
        check(initial.accessPolicyWindow.num_bytes == 0, "New stream already has a window")
        requested = AttributeValue()
        requested.accessPolicyWindow = AccessPolicyWindow(allocation.value, 128, 1.0, 2, 0)
        report["requested_window"] = window_fields(requested)
        need("cuStreamSetAttribute", stream, 1, C.byref(requested), purpose="single fixed window")
        observed = AttributeValue()
        need("cuStreamGetAttribute", stream, 1, C.byref(observed), purpose="exact stream readback")
        report["stream_window"] = window_fields(observed)
        check(report["stream_window"] == report["requested_window"], "Stream window mismatch/alignment change")

        source, destination = C.c_uint64(allocation.value), C.c_uint64(allocation.value + 128)
        params = (C.c_void_p * 2)(C.cast(C.byref(source), C.c_void_p),
                                C.cast(C.byref(destination), C.c_void_p))
        need("cuStreamBeginCapture_v2", stream, 1)
        capturing = True
        status = C.c_int()
        need("cuStreamIsCapturing", stream, C.byref(status))
        report["capture_status_immediately_before_launch"] = status.value
        check(capturing and status.value == 1, "Capture is not ACTIVE; launch forbidden")
        # No CUDA call intervenes between this ACTIVE query and the only launch.
        report["captured_kernel_launch_calls"] += 1
        need("cuLaunchKernel", function, 1, 1, 1, 1, 1, 1, 0, stream, params, None)
        end_rc = invoke("cuStreamEndCapture", stream, C.byref(graph))
        capturing = False
        check(end_rc == 0 and bool(graph.value), "End capture failed or null graph")
        # Match cudarc end_capture: instantiate immediately, with AUTO_FREE_ON_LAUNCH.
        need("cuGraphInstantiateWithFlags", C.byref(executable), graph, 1)
        check(bool(executable.value), "Null executable graph")
        count = C.c_size_t()
        need("cuGraphGetNodes", graph, None, C.byref(count))
        report["graph_node_count"] = count.value
        check(count.value == 1, "Expected exactly one captured node")
        nodes = (C.c_void_p * 1)()
        need("cuGraphGetNodes", graph, nodes, C.byref(count))
        check(count.value == 1 and bool(nodes[0]), "Captured node fetch mismatch")
        kind = C.c_int()
        need("cuGraphNodeGetType", nodes[0], C.byref(kind))
        report["graph_node_type"] = kind.value
        check(kind.value == 0, "Captured node is not a kernel")
        node_policy = AttributeValue()
        need("cuGraphKernelNodeGetAttribute", nodes[0], 1, C.byref(node_policy))
        report["retained_node_window_after_instantiation"] = window_fields(node_policy)
        check(window_fields(node_policy) == report["requested_window"], "Retained node window mismatch")
        inspected = True
    except Exception as exc:
        report["errors"].append({"exception": repr(exc)})
    finally:
        # No replay or synchronization is needed: the only launch was captured.
        # Every applicable cleanup is attempted once, even after another failure.
        if bound:
            if capturing:
                invoke("cuStreamEndCapture", stream, C.byref(graph), purpose="end failed capture during cleanup")
            if executable.value:
                report["cleanup"]["exec_destroy"] = invoke("cuGraphExecDestroy", executable)
            if graph.value:
                report["cleanup"]["graph_destroy"] = invoke("cuGraphDestroy", graph)
            if owns_stream:
                disabled = AttributeValue()
                report["cleanup"]["policy_disable"] = invoke("cuStreamSetAttribute", stream, 1, C.byref(disabled), purpose="disable owned stream window")
                final = AttributeValue()
                rc = invoke("cuStreamGetAttribute", stream, 1, C.byref(final), purpose="disabled window readback")
                report["cleanup"]["disabled_window"] = window_fields(final) if rc == 0 else None
                if rc == 0 and final.accessPolicyWindow.num_bytes != 0:
                    report["errors"].append({"cleanup": "Stream window remained enabled"})
            if owns_allocation:
                report["cleanup"]["mem_free"] = invoke("cuMemFree_v2", allocation)
            if owns_stream:
                report["cleanup"]["stream_destroy"] = invoke("cuStreamDestroy_v2", stream)
            if owns_module:
                report["cleanup"]["module_unload"] = invoke("cuModuleUnload", module)
        if retained:
            report["cleanup"]["context_restore"] = invoke("cuCtxSetCurrent", previous, purpose="restore original thread binding")
            report["cleanup"]["primary_release"] = invoke("cuDevicePrimaryCtxRelease_v2", device, purpose="release owned retained reference")
    failed = (not inspected or bool(report["errors"])
              or any(row["return_code"] != 0 for row in report["calls"]))
    report["status"] = "FAIL_OR_UNSUPPORTED" if failed else "PASS_CAPTURED_NODE_ATTRIBUTE"
    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    print("D064_CAPTURE_POLICY " + json.dumps(report, sort_keys=True, allow_nan=False), flush=True)
    return 2 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
