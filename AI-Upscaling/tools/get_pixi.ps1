$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

. "$scriptDir\pixi_settings.ps1"

$PIXI_HOME = Join-Path $scriptDir "..\.pixi"
$env:PIXI_HOME = $PIXI_HOME
$env:PIXI_VERSION = $PIXI_VERSION
$env:PIXI_CACHE_DIR = "$PIXI_HOME"

$pixiBinary = Join-Path $PIXI_HOME "bin\pixi.exe"
$tempFile = $null

try {
    if (-not (Test-Path $pixiBinary)) {
        $tempFile = [System.IO.Path]::GetTempFileName() + ".ps1"
        Invoke-WebRequest -Uri 'https://pixi.sh/install.ps1' -OutFile $tempFile
        & $tempFile -PixiVersion $env:PIXI_VERSION -PixiHome $env:PIXI_HOME -NoPathUpdate
    }
} finally {
    if ($tempFile -and (Test-Path $tempFile)) {
        Remove-Item $tempFile -Force
    }
}

$script:pixi = $pixiBinary
