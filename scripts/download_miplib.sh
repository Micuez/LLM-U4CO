#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p data/miplib

cat <<'EOF'
This project currently uses small local benchmark files only.

To stage a tiny MIPLIB-style subset manually, place `.mps` or `.lp` files under:
  data/miplib/

and list them in:
  data/miplib/miplib_small.txt

The loader is intentionally local-first so the framework stays runnable without network access.
EOF
