$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

. "$scriptDir\check_if_ai_pc.ps1"
. "$scriptDir\get_pixi.ps1"
& $script:pixi $args
