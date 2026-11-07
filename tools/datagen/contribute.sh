#!/usr/bin/env bash
# Contribute compute to the GTOpen value-net training data (Linux / WSL).
#   tools/datagen/contribute.sh YOUR_GITHUB_LOGIN [datagen run options, e.g. --hours 8]
# Builds solve-cli (with CUDA when an NVIDIA runtime is present), uploads
# finished jobs every 30 minutes in the background, and generates until
# stopped (Ctrl+C is safe: an unfinished job restarts next time).
# See docs/contribute-compute.md.
set -euo pipefail
cd "$(dirname "$0")/../.."
if [ $# -lt 1 ]; then
  echo "usage: tools/datagen/contribute.sh YOUR_GITHUB_LOGIN [--hours H] [--jobs N]"
  exit 1
fi
LOGIN="$1"; shift

for d in \
  "$HOME/.local/cuda-nvrtc/nvidia/cuda_nvrtc/lib" \
  /usr/local/cuda/lib64 \
  /usr/lib/x86_64-linux-gnu; do
  [ -d "$d" ] && export LD_LIBRARY_PATH="$d${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
done
FEATURES="--features gpu"
if ! command -v nvidia-smi >/dev/null 2>&1 \
   && ! ldconfig -p 2>/dev/null | grep -q libcuda \
   && [ ! -e /usr/lib/wsl/lib/libcuda.so.1 ]; then
  FEATURES=""
  echo "no NVIDIA CUDA runtime found: building CPU-only (much slower)"
fi
cargo build --release -p solver $FEATURES --bin solve-cli

PY=$(command -v python3 || command -v python || true)
UPLOADER=""
if [ -n "$PY" ] && "$PY" -c "import huggingface_hub" 2>/dev/null; then
  "$PY" tools/datagen/upload.py --contributor "$LOGIN" --watch 30 &
  UPLOADER=$!
  trap '[ -n "$UPLOADER" ] && kill "$UPLOADER" 2>/dev/null || true' EXIT
else
  echo "huggingface_hub is not installed: jobs will be saved but not uploaded."
  echo "Install it (pip install huggingface_hub), run hf auth login, then"
  echo "  python3 tools/datagen/upload.py --contributor $LOGIN"
fi

# The generator exits non-zero when it is interrupted or killed; keep going
# so the jobs it finished still get their final upload. A handler (not an
# ignore) for Ctrl+C keeps this script alive while the generator still gets
# the default signal.
trap 'echo' INT
./target/release/solve-cli datagen run --contributor "$LOGIN" "$@" || echo "generator stopped (exit $?)"
if [ -n "$UPLOADER" ]; then
  kill "$UPLOADER" 2>/dev/null || true
  echo "uploading finished jobs..."
  "$PY" tools/datagen/upload.py --contributor "$LOGIN" || true
fi
