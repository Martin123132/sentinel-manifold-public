param(
    [string]$Python = "python",
    [string]$OutDir = "out",
    [switch]$Full
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

if (!(Test-Path $OutDir)) {
    New-Item -ItemType Directory -Path $OutDir | Out-Null
}

$suites = @(
    @{ Name = "Regression"; Input = "samples/regression-suite.json"; Output = "$OutDir/suite-report.json" },
    @{ Name = "Customer-shaped"; Input = "samples/customer-shaped-regression-suite.json"; Output = "$OutDir/customer-shaped-regression-suite-report.json" },
    @{ Name = "Policy calibration"; Input = "samples/policy-calibration-suite.json"; Output = "$OutDir/policy-calibration-suite-report.json" },
    @{ Name = "Integration starter"; Input = "samples/integration-starter-suite.json"; Output = "$OutDir/integration-starter-suite-report.json" },
    @{ Name = "Mixed proof"; Input = "samples/mixed-proof-suite.json"; Output = "$OutDir/mixed-proof-suite-report.json" }
)

if ($Full) {
    $suites += @(
        @{ Name = "Agent policy"; Input = "samples/agent-policy-suite.json"; Output = "$OutDir/agent-policy-suite-report.json" },
        @{ Name = "Buyer policy depth"; Input = "samples/buyer-policy-depth-suite.json"; Output = "$OutDir/buyer-policy-depth-suite-report.json" },
        @{ Name = "Policy tuning"; Input = "samples/policy-tuning-suite.json"; Output = "$OutDir/policy-tuning-suite-report.json" },
        @{ Name = "External adoption"; Input = "examples/external-adoption/support-assistant/sentinel-suite.json"; Output = "$OutDir/external-adoption-suite-report.json" }
    )
}

$results = @()

foreach ($suite in $suites) {
    Write-Host "Running $($suite.Name)..."
    & $Python app/cli.py suite --input $suite.Input --out $suite.Output --fail-on-fail
    $exitCode = $LASTEXITCODE

    if ($exitCode -ne 0) {
        throw "Suite failed: $($suite.Name) ($($suite.Input))"
    }

    $report = Get-Content -Raw -Path $suite.Output | ConvertFrom-Json
    $summary = $report.summary
    $results += [pscustomobject]@{
        Suite = $suite.Name
        Status = $report.status
        Cases = $summary.case_count
        Passed = $summary.passed
        Failed = $summary.failed
        Report = $suite.Output
    }
}

Write-Host ""
$results | Format-Table -AutoSize
Write-Host "All Sentinel proof suites passed."
Write-Host "Reports are in $OutDir."
