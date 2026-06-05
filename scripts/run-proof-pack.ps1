param(
    [string]$Python = "python",
    [string]$OutDir = "out",
    [switch]$Full
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$runnerArgs = @(
    "scripts/run-proof-pack.py",
    "--python",
    $Python,
    "--out-dir",
    $OutDir
)

if ($Full) {
    $runnerArgs += "--full"
}

& $Python @runnerArgs
exit $LASTEXITCODE
