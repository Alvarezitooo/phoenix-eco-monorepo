#!/usr/bin/env bash
# tools/run_all.sh
set -euo pipefail

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$ROOT_DIR"

EXIT=0
./tools/check_secrets.sh || EXIT=2
./tools/check_security.sh || EXIT=2
./tools/check_health.sh || EXIT=2

exit $EXIT
