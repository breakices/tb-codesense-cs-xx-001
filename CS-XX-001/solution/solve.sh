#!/bin/sh
# Applies the reference fix of CS-XX-001 to /workspace/repo.
set -e
cd /workspace/repo
patch -p1 --no-backup-if-mismatch -s < "$(dirname "$0")/golden/golden.patch"
