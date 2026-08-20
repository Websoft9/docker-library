param(
  [string]$Target = "help",
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$Args
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-PythonCommand {
  if (Get-Command py -ErrorAction SilentlyContinue) {
    return "py"
  }
  return "python"
}

function Get-ProxyValue {
  foreach ($name in @("https_proxy", "HTTPS_PROXY", "http_proxy", "HTTP_PROXY")) {
    $value = [Environment]::GetEnvironmentVariable($name)
    if ($value) {
      return $value
    }
  }
  return $null
}

function Save-ProxySnapshot {
  $proxy = Get-ProxyValue
  if ($proxy) {
    Set-Content -NoNewline -Encoding UTF8 -Path "cli/proxy.conf" -Value $proxy
    Write-Host "saved proxy: $proxy"
  }
}

function Set-ProxyEnvironment {
  $proxy = Get-ProxyValue
  if ($proxy) {
    $env:https_proxy = $proxy
    $env:http_proxy = $proxy
    $env:all_proxy = $proxy
    if ($env:NO_PROXY -eq "*" -or $env:no_proxy -eq "*") {
      $env:NO_PROXY = ""
      $env:no_proxy = ""
    }
  }
}

switch ($Target) {
  "help" {
    Write-Host "  install      create .venv and install the libs CLI"
    Write-Host "  libs         run one libs command, e.g. .\\make.ps1 libs scan --app wordpress --json"
    Write-Host "  cli          open a PowerShell with the libs CLI activated"
  }
  "install" {
    $python = Get-PythonCommand
    & $python -m venv .venv
    & .\.venv\Scripts\python.exe -m pip install -e cli/
    Save-ProxySnapshot
  }
  "libs" {
    Set-ProxyEnvironment
    & .\.venv\Scripts\libs.exe @Args
  }
  "cli" {
    $pwsh = if (Get-Command pwsh -ErrorAction SilentlyContinue) { "pwsh" } else { "powershell" }
    $command = "& '.\.venv\Scripts\Activate.ps1'; libs -h"
    & $pwsh -NoExit -Command $command
  }
  default {
    throw "Unknown target: $Target"
  }
}
