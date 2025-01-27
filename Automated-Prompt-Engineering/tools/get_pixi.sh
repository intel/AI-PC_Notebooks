#!/bin/bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/pixi_settings.env"

PIXI_HOME="$script_dir/../.pixi"
export PIXI_HOME PIXI_NO_PATH_UPDATE PIXI_VERSION

if [[ -z "$PIXI_VERSION" ]]; then
    echo "Please set PIXI_VERSION in pixi_settings.env"
    exit 1
fi

pixi_binary="${PIXI_HOME}/bin/pixi"

if [[ ! -x "$pixi_binary" ]]; then
    echo "Installing Pixi..."
    $script_dir/install_pixi.sh
fi

export pixi="$pixi_binary"
