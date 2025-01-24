#!/bin/bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$script_dir/check_if_ai_pc.sh"
source "$script_dir/get_pixi.sh"

"$pixi" "$@"