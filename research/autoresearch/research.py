"""Zero-configuration entry point; no venv activation or path edits needed."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import venv

from workspace import HERE, ROOT, ensure_workspace


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["setup", "verify", "lab"], nargs="?", default="setup")
    parser.add_argument("extra", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    extra = args.extra
    if extra and args.action != "lab":
        parser.error("extra arguments are only supported after 'lab'")
    ensure_workspace()
    if args.action == "verify":
        # Audit historical evidence, not a claim that later edits passed those tests.
        return subprocess.call([sys.executable, str(HERE / "verify_gpu_pass.py"), "--recorded"], cwd=ROOT)
    env_dir = ROOT / "target/autoresearch/venv"
    python = env_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.exists():
        print("Creating local research Python environment...", flush=True)
        venv.EnvBuilder(with_pip=True).create(env_dir)
    requirements = HERE / "requirements.txt"
    marker = env_dir / "gtopen-requirements.txt"
    content = requirements.read_bytes()
    if not marker.exists() or marker.read_bytes() != content:
        subprocess.run([str(python), "-m", "pip", "install", "-r", str(requirements)], check=True)
        marker.write_bytes(content)
    print(f"Research ready at {ROOT}; no shell activation needed.", flush=True)
    if args.action == "lab":
        return subprocess.call([str(python), str(HERE / "lab.py"), *extra], cwd=ROOT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
