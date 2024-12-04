$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

. "$scriptDir\pixi_settings.ps1"

$PIXI_HOME = Join-Path $scriptDir "..\.pixi"
$env:PIXI_HOME = $PIXI_HOME
$env:PIXI_VERSION = $PIXI_VERSION
$env:PIXI_CACHE_DIR = "$PIXI_HOME"

if (-not $env:PIXI_VERSION) {
    throw "PIXI_VERSION is not set. Please set PIXI_VERSION in pixi_settings.ps1"
}

$pixiBinary = Join-Path $PIXI_HOME "bin\pixi.exe"

if (-not (Test-Path $pixiBinary)) {
    $installPixiScript = Join-Path $scriptDir "install_pixi.ps1"
    & $installPixiScript -PixiVersion $env:PIXI_VERSION -PixiHome $env:PIXI_HOME -NoPathUpdate
}

$script:pixi = $pixiBinary
