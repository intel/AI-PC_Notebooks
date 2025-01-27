#!/bin/bash
set -euo pipefail

if lscpu | grep -q "Core(TM) Ultra"; then
    echo "'Core(TM) Ultra' is present in the CPU information."
else
    echo "'Core(TM) Ultra' is NOT present in the CPU information."
    echo "Full lscpu output:"
    lscpu
    exit 1
fi