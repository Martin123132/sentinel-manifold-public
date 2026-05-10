param(
  [string]$ImageName = "sentinel-manifold:ci",
  [string]$ContainerName = "sentinel-manifold-smoke",
  [int]$HostPort = 8788,
  [string]$ApiKey = "docker-smoke-secret",
  [switch]$RunSuite,
  [switch]$PublicDemo
)

$ErrorActionPreference = "Stop"

function Find-Docker {
  $command = Get-Command docker -ErrorAction SilentlyContinue
  if ($command) {
    return $command.Source
  }

  $dockerDesktopCli = "C:\Program Files\Docker\Docker\resources\bin\docker.exe"
  if (Test-Path $dockerDesktopCli) {
    return $dockerDesktopCli
  }

  throw "Docker CLI was not found. Install Docker Desktop or add docker.exe to PATH."
}

function Wait-For-Health {
  param([string]$Url)

  for ($i = 1; $i -le 30; $i++) {
    try {
      return Invoke-RestMethod $Url
    } catch {
      Start-Sleep -Seconds 1
    }
  }

  throw "Container did not become healthy at $Url."
}

function Invoke-Docker {
  param(
    [string]$DockerExe,
    [string[]]$Arguments
  )

  & $DockerExe @Arguments
  if ($LASTEXITCODE -ne 0) {
    throw "Docker command failed: docker $($Arguments -join ' ')"
  }
}

function Assert-Docker-Ready {
  param([string]$DockerExe)

  $desktopStatus = ""
  try {
    $desktopStatus = (& $DockerExe desktop status 2>$null | Out-String).Trim()
  } catch {
    $desktopStatus = ""
  }

  if ($desktopStatus -match "Status\s+(\S+)") {
    $status = $Matches[1]
    if ($status -ne "running") {
      throw "Docker Desktop status is '$status'. Open Docker Desktop and confirm the Linux engine is running. If it reports WSL needs an update, run 'wsl --update' or 'wsl --install --no-distribution --web-download' from an elevated PowerShell, then restart Docker Desktop."
    }
  }

  try {
    Invoke-Docker $DockerExe @("--context", "desktop-linux", "version", "--format", "{{.Server.Version}}") | Out-Null
  } catch {
    throw "Docker Desktop is not ready. Open Docker Desktop and confirm the Linux engine is running. If it reports WSL needs an update, run 'wsl --update' or 'wsl --install --no-distribution --web-download' from an elevated PowerShell, then restart Docker Desktop."
  }
}

try {
  $docker = Find-Docker
  Assert-Docker-Ready $docker

  Invoke-Docker $docker @("--context", "desktop-linux", "build", "-t", $ImageName, ".")

  $existing = Invoke-Docker $docker @("--context", "desktop-linux", "ps", "-aq", "--filter", "name=^/$ContainerName$")
  if ($existing) {
    Invoke-Docker $docker @("--context", "desktop-linux", "rm", "-f", $ContainerName) | Out-Null
  }

  try {
    $runArgs = @("--context", "desktop-linux", "run", "-d", "--name", $ContainerName, "-p", "${HostPort}:8787", "-e", "SENTINEL_API_KEY=$ApiKey")
    if ($PublicDemo) {
      $runArgs += @("-e", "SENTINEL_PUBLIC_DEMO=true")
    }
    $runArgs += $ImageName
    Invoke-Docker $docker $runArgs | Out-Null
    $baseUrl = "http://127.0.0.1:$HostPort"
    $health = Wait-For-Health "$baseUrl/api/health"
    if (-not $health.ok -or -not $health.auth_required) {
      throw "Unexpected health payload: $($health | ConvertTo-Json -Compress)"
    }
    if ($PublicDemo -and -not $health.public_demo) {
      throw "Expected public_demo=true in health payload: $($health | ConvertTo-Json -Compress)"
    }

    if ($PublicDemo) {
      $publicProviders = Invoke-RestMethod "$baseUrl/api/providers"
      if (($publicProviders.providers | Measure-Object).Count -ne 1 -or $publicProviders.providers[0].id -ne "local_demo") {
        throw "Expected public demo provider discovery to expose only local_demo, got $($publicProviders | ConvertTo-Json -Compress -Depth 10)."
      }
      $auditStatus = $null
      try {
        Invoke-RestMethod "$baseUrl/api/audits" | Out-Null
      } catch {
        $auditStatus = [int]$_.Exception.Response.StatusCode
      }
      if ($auditStatus -ne 401) {
        throw "Expected unauthenticated audit request to return 401 in public demo mode, got $auditStatus."
      }
    } else {
      $unauthorizedStatus = $null
      try {
        Invoke-RestMethod "$baseUrl/api/providers" | Out-Null
      } catch {
        $unauthorizedStatus = [int]$_.Exception.Response.StatusCode
      }
      if ($unauthorizedStatus -ne 401) {
        throw "Expected unauthenticated provider request to return 401, got $unauthorizedStatus."
      }
    }

    $providers = Invoke-RestMethod "$baseUrl/api/providers" -Headers @{ Authorization = "Bearer $ApiKey" }
    if (($providers.providers | Measure-Object).Count -lt 5) {
      throw "Expected at least five providers, got $($providers.providers.Count)."
    }

    $result = [ordered]@{
      image = $ImageName
      container = $ContainerName
      health = "ok"
      auth_required = $health.auth_required
      public_demo = [bool]$health.public_demo
      provider_count = $providers.providers.Count
    }

    if ($RunSuite) {
      $headers = @{}
      if (-not $PublicDemo) {
        $headers = @{ Authorization = "Bearer $ApiKey" }
      }
      $suite = Invoke-RestMethod "$baseUrl/api/demo-suite" -Headers $headers
      $suiteReport = Invoke-RestMethod "$baseUrl/api/suite" -Headers $headers -Method Post -ContentType "application/json" -Body ($suite | ConvertTo-Json -Depth 40)
      if ($suiteReport.status -ne "PASS") {
        throw "Expected demo suite to PASS, got $($suiteReport.status): $($suiteReport | ConvertTo-Json -Compress -Depth 20)"
      }
      if ($suiteReport.summary.case_count -lt 1 -or $suiteReport.summary.failed -ne 0) {
        throw "Unexpected suite summary: $($suiteReport.summary | ConvertTo-Json -Compress)"
      }
      if ($PublicDemo -and (($suiteReport.cases | Where-Object { $_.evidence }).Count -ne 0)) {
        throw "Expected public demo suite to skip evidence persistence."
      }
      $result.suite_status = $suiteReport.status
      $result.suite_cases = $suiteReport.summary.case_count
      $result.suite_passed = $suiteReport.summary.passed
      $result.suite_failed = $suiteReport.summary.failed
    }

    [pscustomobject]$result | ConvertTo-Json
  } finally {
    & $docker --context desktop-linux rm -f $ContainerName 2>$null | Out-Null
  }
} catch {
  [Console]::Error.WriteLine("ERROR: $($_.Exception.Message)")
  exit 1
}
