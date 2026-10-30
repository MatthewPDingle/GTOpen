"""D061 getter-only child process. Run only through the authorized root wrapper."""
import argparse
import ctypes as C
import json
import os
import sys
from datetime import datetime, timezone

DLL_PATH = r"C:\Windows\System32\nvcuda.dll"
ATTRIBUTES = {
    "compute_capability_major": 75,
    "compute_capability_minor": 76,
    "l2_cache_bytes": 38,
    "max_persisting_l2_cache_bytes": 108,
    "max_access_policy_window_bytes": 109,
}
PERSISTING_L2_LIMIT = 6


class CUuuid(C.Structure):
    _fields_ = [("bytes", C.c_ubyte * 16)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--getters-only", action="store_true", required=True)
    parser.parse_args()
    report = {
        "id": "D061", "device_ordinal": 0,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "dll_path": DLL_PATH,
        "values": {}, "calls": [], "errors": [],
        "context_limit_scope": "This isolated query process's retained primary context; not the live server's context.",
        "kernel_launches": 0, "solver_launches": 0,
        "streams_created": 0, "modules_loaded": 0,
        "application_device_allocations": 0,
        "cache_policy_mutations": 0, "performance_measurement": False,
    }
    funcs = {}

    def invoke(name, *args, purpose=None):
        row = {"api": name, "return_code": None}
        if purpose is not None:
            row["purpose"] = purpose
        if name not in funcs:
            row["error"] = "symbol unavailable; call not made"
        else:
            try:
                row["return_code"] = int(funcs[name](*args))
            except Exception as exc:
                row["error"] = repr(exc)
        report["calls"].append(row)
        return row["return_code"]

    def integer(name, key, *tail):
        value = C.c_int()
        rc = invoke(name, C.byref(value), *tail, purpose=key)
        report["values"][key] = value.value if rc == 0 else None
        return report["values"][key]

    try:
        if os.name != "nt" or C.sizeof(C.c_void_p) != 8:
            raise RuntimeError("Requires 64-bit Windows Python")
        dll = C.WinDLL(DLL_PATH)
        pi, pp = C.POINTER(C.c_int), C.POINTER(C.c_void_p)
        signatures = {
            "cuInit": [C.c_uint],
            "cuDriverGetVersion": [pi],
            "cuDeviceGetCount": [pi],
            "cuDeviceGet": [pi, C.c_int],
            "cuDeviceGetName": [C.POINTER(C.c_char), C.c_int, C.c_int],
            "cuDeviceGetUuid_v2": [C.POINTER(CUuuid), C.c_int],
            "cuDeviceGetAttribute": [pi, C.c_int, C.c_int],
            "cuCtxGetCurrent": [pp],
            "cuDevicePrimaryCtxRetain": [pp, C.c_int],
            "cuCtxSetCurrent": [C.c_void_p],
            "cuCtxGetLimit": [C.POINTER(C.c_size_t), C.c_int],
            "cuDevicePrimaryCtxRelease_v2": [C.c_int],
        }
        for name, argtypes in signatures.items():
            try:
                fn = getattr(dll, name)
                fn.argtypes, fn.restype = argtypes, C.c_int
                funcs[name] = fn
            except AttributeError as exc:
                report["errors"].append({"symbol": name, "error": repr(exc)})
        if invoke("cuInit", 0) != 0:
            raise RuntimeError("cuInit unavailable or failed; no dependent calls")
        integer("cuDriverGetVersion", "driver_version")
        count = integer("cuDeviceGetCount", "device_count")
        if count is None or count < 1:
            raise RuntimeError("Device ordinal 0 unavailable")
        device = integer("cuDeviceGet", "device_handle", 0)
        if device is None:
            raise RuntimeError("cuDeviceGet failed")
        name = C.create_string_buffer(256)
        rc = invoke("cuDeviceGetName", name, len(name), device)
        report["values"]["name"] = name.value.decode("utf-8", errors="replace") if rc == 0 else None
        report["values"]["name_buffer_hex"] = bytes(name).hex() if rc == 0 else None
        uuid = CUuuid()
        rc = invoke("cuDeviceGetUuid_v2", C.byref(uuid), device)
        report["values"]["uuid_hex"] = bytes(uuid.bytes).hex() if rc == 0 else None
        for key, attribute in ATTRIBUTES.items():
            integer("cuDeviceGetAttribute", key, attribute, device)

        report["values"]["current_context_persisting_l2_limit_bytes"] = None
        context_apis = ("cuCtxGetCurrent", "cuDevicePrimaryCtxRetain", "cuCtxSetCurrent",
                        "cuCtxGetLimit", "cuDevicePrimaryCtxRelease_v2")
        if all(name in funcs for name in context_apis):
            previous, retained = C.c_void_p(), C.c_void_p()
            if invoke("cuCtxGetCurrent", C.byref(previous)) == 0:
                report["original_thread_context_was_null"] = previous.value is None
                if invoke("cuDevicePrimaryCtxRetain", C.byref(retained), device) == 0:
                    try:
                        if invoke("cuCtxSetCurrent", retained, purpose="bind owned query context") == 0:
                            limit = C.c_size_t()
                            rc = invoke("cuCtxGetLimit", C.byref(limit), PERSISTING_L2_LIMIT)
                            if rc == 0:
                                report["values"]["current_context_persisting_l2_limit_bytes"] = limit.value
                    finally:
                        # Attempt BOTH cleanup calls even if bind/get/restore fails.
                        invoke("cuCtxSetCurrent", previous, purpose="restore original thread binding")
                        invoke("cuDevicePrimaryCtxRelease_v2", device, purpose="release owned retained reference")
        else:
            report["errors"].append({"context_limit": "unavailable; no context retained because getter/cleanup symbols are incomplete"})
    except Exception as exc:
        report["errors"].append({"exception": repr(exc)})
    failed = bool(report["errors"]) or any(row["return_code"] != 0 for row in report["calls"])
    report["status"] = "partial_or_error" if failed else "complete"
    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    # CUDA return codes (including unsupported) remain in calls; no error becomes zero.
    print("D061_CAPABILITY " + json.dumps(report, sort_keys=True, allow_nan=False), flush=True)
    return 2 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
