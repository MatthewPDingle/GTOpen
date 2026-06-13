#!/usr/bin/env bash
# FREEPIO launcher — sets up the CUDA runtime path so the GPU solver engages
# (without it the server silently falls back to CPU), then starts the server.
set -euo pipefail
cd "$(dirname "$0")"

# nvrtc from the pip-installed nvidia-cuda-nvrtc package (see README), plus
# common system CUDA locations as fallbacks.
for d in \
  "$HOME/.local/cuda-nvrtc/nvidia/cuda_nvrtc/lib" \
  /usr/local/cuda/lib64 \
  /usr/lib/x86_64-linux-gnu; do
  [ -d "$d" ] && export LD_LIBRARY_PATH="$d${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
done

# Always (re)build with the GPU feature — cargo is incremental, so this is a
# fast no-op when nothing changed, and it guarantees the binary actually has
# the GPU engine rather than an older CPU-only build.
cargo build --release -p server --features gpu

exec ./target/release/gto-server "$@"
