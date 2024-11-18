#!/bin/bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/pixi_settings.env"

PIXI_HOME="$script_dir/../.pixi"
export PIXI_HOME PIXI_NO_PATH_UPDATE PIXI_VERSION

pixi_binary="${PIXI_HOME}/bin/pixi"

if [[ ! -x "$pixi_binary" ]]; then
    echo "Installing Pixi..."
    ./install_pixi.sh
fi

export pixi="$pixi_binary"
