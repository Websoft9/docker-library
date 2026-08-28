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

function Write-HelpHeader {
  param([string]$Text)
  Write-Host ""
  Write-Host "  ▸ $Text" -ForegroundColor Magenta
}

function Write-HelpEntry {
  param([string]$Name, [string]$Desc)
  Write-Host "  " -NoNewline
  Write-Host "make " -NoNewline -ForegroundColor DarkGray
  Write-Host ("{0,-18}" -f $Name) -NoNewline -ForegroundColor Green
  Write-Host $Desc
}

switch ($Target) {
  "help" {
    Write-Host ""
    Write-Host "  docker-library make targets" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Usage: .\make.ps1 <target>"
    Write-Host ""
    Write-HelpHeader "Dev"
    Write-HelpEntry "opencode" "start opencode with proxy disabled"
    Write-HelpEntry "opencode-clear" "list opencode sessions, confirm, then delete them (ARGS: --all/--dry-run)"
    Write-HelpEntry "cli" "open a PowerShell with the libs CLI activated"
    Write-HelpEntry "libs" "run one libs command, e.g. .\make.ps1 libs scan --app wordpress --json"
    Write-HelpHeader "Testing & Quality"
    Write-HelpEntry "test" "run the full repo machine-system test suite"
    Write-HelpEntry "test-cli" "run cli unit and contract tests"
    Write-HelpEntry "test-build" "run build pipeline smoke tests"
    Write-HelpEntry "test-skills" "run skills asset and workflow tests"
    Write-HelpHeader "Config & Setup"
    Write-HelpEntry "help" "show this help"
    Write-HelpEntry "install" "create .venv and install the libs CLI"
    Write-HelpEntry "remote" "interactively write .secrets/remote.env for remote-aware commands"
    Write-HelpEntry "connector" "interactively write .secrets/<provider>.env for external API tokens"
    Write-Host ""
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
  "remote" {
    New-Item -ItemType Directory -Force ".secrets" | Out-Null
    $currentTarget = "remote"
    $currentHost = ""
    $currentUser = "root"
    $currentSecret = ".secrets/ssh/default.pem"
    $currentPath = "/websoft9/library/apps"

    if (Test-Path ".secrets/remote.env") {
      foreach ($line in Get-Content ".secrets/remote.env") {
        if ($line -match '^\s*([^#=]+)=(.*)$') {
          $key = $matches[1].Trim()
          $value = $matches[2].Trim().Trim('"')
          switch ($key) {
            "TARGET" { $currentTarget = $value }
            "SSH_HOST" { $currentHost = $value }
            "SSH_USER" { $currentUser = $value }
            "SSH_SECRET_PATH" { $currentSecret = $value }
            "DEPLOY_ROOT" { $currentPath = $value }
          }
        }
      }
    }

    $inputTarget = Read-Host "TARGET [$currentTarget]"
    if (-not $inputTarget) { $inputTarget = $currentTarget }
    $inputHost = Read-Host "SSH_HOST [$currentHost]"
    if (-not $inputHost) { $inputHost = $currentHost }
    $inputUser = Read-Host "SSH_USER [$currentUser]"
    if (-not $inputUser) { $inputUser = $currentUser }
    $inputSecret = Read-Host "SSH_SECRET_PATH [$currentSecret]"
    if (-not $inputSecret) { $inputSecret = $currentSecret }
    $inputPath = Read-Host "DEPLOY_ROOT [$currentPath]"
    if (-not $inputPath) { $inputPath = $currentPath }

    Set-Content -Encoding UTF8 -Path ".secrets/remote.env" -Value @(
      "TARGET=$inputTarget",
      "SSH_HOST=$inputHost",
      "SSH_USER=$inputUser",
      "SSH_SECRET_PATH=$inputSecret",
      "DEPLOY_ROOT=$inputPath"
    )
    Write-Host "wrote .secrets/remote.env"
  }
  "connector" {
    New-Item -ItemType Directory -Force ".secrets" | Out-Null
    $currentChoice = if ($Args.Count -gt 0 -and ($Args[0] -eq "cloudflare" -or $Args[0] -eq "2")) { "2" } else { "1" }
    Write-Host "Available providers:"
    Write-Host "  1) contentful"
    Write-Host "  2) cloudflare"
    $provider = Read-Host "provider [$currentChoice]"
    if (-not $provider) {
      $provider = $currentChoice
    }

    switch ($provider.ToLowerInvariant()) {
      "1" {
        $file = ".secrets/contentful.env"
        $key = "CONTENTFUL_ACCESS_TOKEN"
      }
      "contentful" {
        $file = ".secrets/contentful.env"
        $key = "CONTENTFUL_ACCESS_TOKEN"
      }
      "2" {
        $file = ".secrets/cloudflare.env"
        $key = "CLOUDFLARE_API_TOKEN"
      }
      "cloudflare" {
        $file = ".secrets/cloudflare.env"
        $key = "CLOUDFLARE_API_TOKEN"
      }
      default {
        throw "Unsupported provider: $provider"
      }
    }

    if (Test-Path $file) {
      Write-Host "updating $file"
    } else {
      Write-Host "creating $file"
    }

    $secure = Read-Host $key -AsSecureString
    $ptr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    try {
      $token = [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    } finally {
      [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    }
    if (-not $token) {
      throw "empty token is not allowed"
    }
    Set-Content -Encoding UTF8 -Path $file -Value "$key=$token"
    Write-Host "wrote $file"
  }
  "test-cli" {
    & .\.venv\Scripts\python.exe -m pytest cli/tests -q
  }
  "test-build" {
    & .\.venv\Scripts\python.exe -m pytest tests/build -q
  }
  "test-skills" {
    & .\.venv\Scripts\python.exe -m pytest tests/skills -q
  }
  "test" {
    & .\.venv\Scripts\python.exe -m pytest cli/tests tests/build tests/skills -q
  }
  default {
    throw "Unknown target: $Target"
  }
}
