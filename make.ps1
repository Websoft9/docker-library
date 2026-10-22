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
    Write-HelpHeader "Server Ops"
    Write-HelpEntry "dns-bind" "point the wildcard record (*.<domain>) at the remote host or localhost (ARGS: --domain/--ip/--json)"
    Write-HelpEntry "dns-delete" "delete the single wildcard record (*.<domain>) for the domain (ARGS: --domain/--json)"
    Write-HelpEntry "websoft9-upgrade" "upgrade the Websoft9 platform container: set image tag, pull, recreate (ARGS: --tag/--target)"
    Write-HelpEntry "create-aliyun-ecs" "create a spot Aliyun ECS instance from ci/cloud/aliyun-ecs.json (interactive instance type/disk/release; ARGS: --instance-type/--disk-size/--release-in)"
    Write-HelpHeader "Testing & Quality"
    Write-HelpEntry "test" "run the full repo machine-system test suite"
    Write-HelpEntry "test-cli" "run cli unit and contract tests"
    Write-HelpEntry "test-build" "run build pipeline smoke tests"
    Write-HelpEntry "test-skills" "run skills asset and workflow tests"
    Write-HelpHeader "Config & Setup"
    Write-HelpEntry "help" "show this help"
    Write-HelpEntry "install" "create .venv and install the libs CLI"
    Write-HelpEntry "remote" "interactively write .secrets/remote.env for remote-aware commands"
    Write-HelpEntry "connector" "interactively write .secrets/<provider>.env for API tokens, DNS and cloud credentials"
    Write-HelpEntry "github-token" "configure the GitHub MCP token for opencode"
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
  "opencode-clear" {
    $python = Get-PythonCommand
    & $python ci/scripts/opencode_delete.py @Args
  }
  "dns-bind" {
    Set-ProxyEnvironment
    & .\.venv\Scripts\python.exe -m libs.ops dns-bind @Args
  }
  "dns-delete" {
    Set-ProxyEnvironment
    & .\.venv\Scripts\python.exe -m libs.ops dns-delete @Args
  }
  "websoft9-upgrade" {
    Set-ProxyEnvironment
    & .\.venv\Scripts\python.exe -m libs.ops websoft9-upgrade @Args
  }
  "create-aliyun-ecs" {
    Set-ProxyEnvironment
    & .\.venv\Scripts\python.exe -m libs.ops create-aliyun-ecs @Args
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
  "github-token" {
    $python = Get-PythonCommand
    & $python ci/scripts/configure_github_mcp.py @Args
  }
  "connector" {
    New-Item -ItemType Directory -Force ".secrets" | Out-Null
    $currentChoice = "1"
    if ($Args.Count -gt 0) {
      switch ($Args[0].ToLowerInvariant()) {
        "contentful" { $currentChoice = "1" }
        "cloudflare" { $currentChoice = "2" }
        "dockerhub" { $currentChoice = "3" }
        "dns" { $currentChoice = "4" }
        "alibabacloud" { $currentChoice = "5" }
        "aws" { $currentChoice = "6" }
        "azure" { $currentChoice = "7" }
        "1" { $currentChoice = "1" }
        "2" { $currentChoice = "2" }
        "3" { $currentChoice = "3" }
        "4" { $currentChoice = "4" }
        "5" { $currentChoice = "5" }
        "6" { $currentChoice = "6" }
        "7" { $currentChoice = "7" }
      }
    }
    Write-Host "Available providers:"
    Write-Host "  1) contentful"
    Write-Host "  2) cloudflare"
    Write-Host "  3) dockerhub"
    Write-Host "  4) dns"
    Write-Host "  5) alibabacloud"
    Write-Host "  6) aws"
    Write-Host "  7) azure"
    $provider = Read-Host "provider [$currentChoice]"
    if (-not $provider) {
      $provider = $currentChoice
    }

    switch ($provider.ToLowerInvariant()) {
      "1" { $provider = "contentful" }
      "2" { $provider = "cloudflare" }
      "3" { $provider = "dockerhub" }
      "4" { $provider = "dns" }
      "5" { $provider = "alibabacloud" }
      "6" { $provider = "aws" }
      "7" { $provider = "azure" }
    }

    if ($provider -eq "contentful") {
      $file = ".secrets/contentful.env"
      $key = "CONTENTFUL_ACCESS_TOKEN"
    } elseif ($provider -eq "cloudflare") {
      $file = ".secrets/cloudflare.env"
      $key = "CLOUDFLARE_API_TOKEN"
    } elseif ($provider -eq "dockerhub") {
      $file = ".secrets/dockerhub.env"
      $key = "DOCKERHUB_TOKEN"
    } elseif ($provider -eq "dns") {
      $file = ".secrets/dns.env"
    } elseif ($provider -eq "alibabacloud") {
      $file = ".secrets/aliyun.env"
    } elseif ($provider -eq "aws") {
      $file = ".secrets/aws.env"
    } elseif ($provider -eq "azure") {
      $file = ".secrets/azure.env"
    } else {
      throw "Unsupported provider: $provider"
    }

    if (Test-Path $file) {
      Write-Host "updating $file"
    } else {
      Write-Host "creating $file"
    }

    function Read-SecretValue([string]$Prompt) {
      $secure = Read-Host $Prompt -AsSecureString
      $ptr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
      try {
        return [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
      } finally {
        [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
      }
    }

    $existing = @{}
    if (Test-Path $file) {
      foreach ($line in Get-Content $file) {
        if ($line -match '^\s*([^#=]+)=(.*)$') {
          $existing[$matches[1].Trim()] = $matches[2].Trim()
        }
      }
    }

    if ($provider -eq "dockerhub") {
      $curUser = $existing["DOCKERHUB_USERNAME"]
      $curToken = $existing["DOCKERHUB_TOKEN"]
      $curOrg = $existing["DOCKERHUB_ORG"]
      $inputUser = Read-Host "DOCKERHUB_USERNAME [$curUser]"
      if (-not $inputUser) { $inputUser = $curUser }
      $inputToken = Read-SecretValue "DOCKERHUB_TOKEN [keep existing]"
      if (-not $inputToken) { $inputToken = $curToken }
      $inputOrg = Read-Host "DOCKERHUB_ORG (optional default push namespace) [$curOrg]"
      if (-not $inputOrg) { $inputOrg = $curOrg }
      if (-not $inputUser -or -not $inputToken) { throw "username and token are required" }
      $lines = @("DOCKERHUB_USERNAME=$inputUser", "DOCKERHUB_TOKEN=$inputToken")
      if ($inputOrg) { $lines += "DOCKERHUB_ORG=$inputOrg" }
      Set-Content -Encoding UTF8 -Path $file -Value $lines
    } elseif ($provider -eq "dns") {
      $curDns = $existing["DNS_PROVIDER"]
      if (-not $curDns) { $curDns = "aliyun" }
      $curId = $existing["DNS_KEY_ID"]
      $curSecret = $existing["DNS_KEY_SECRET"]
      $curDomain = $existing["DNS_DOMAIN"]
      $inputDns = Read-Host "DNS_PROVIDER (e.g. aliyun) [$curDns]"
      if (-not $inputDns) { $inputDns = $curDns }
      $inputId = Read-Host "DNS_KEY_ID [$curId]"
      if (-not $inputId) { $inputId = $curId }
      $inputSecret = Read-SecretValue "DNS_KEY_SECRET [keep existing]"
      if (-not $inputSecret) { $inputSecret = $curSecret }
      $inputDomain = Read-Host "DNS_DOMAIN (wildcard base, e.g. libs.websoft9.cn) [$curDomain]"
      if (-not $inputDomain) { $inputDomain = $curDomain }
      if (-not $inputDns -or -not $inputId -or -not $inputSecret) { throw "provider, key id and secret are required" }
      $lines = @("DNS_PROVIDER=$inputDns", "DNS_KEY_ID=$inputId", "DNS_KEY_SECRET=$inputSecret")
      if ($inputDomain) { $lines += "DNS_DOMAIN=$inputDomain" }
      Set-Content -Encoding UTF8 -Path $file -Value $lines
    } elseif ($provider -eq "alibabacloud") {
      $curId = $existing["ALIYUN_ACCESS_KEY_ID"]
      $curSecret = $existing["ALIYUN_ACCESS_KEY_SECRET"]
      $curRegion = $existing["ALIYUN_REGION"]
      $inputId = Read-Host "ALIYUN_ACCESS_KEY_ID [$curId]"
      if (-not $inputId) { $inputId = $curId }
      $inputSecret = Read-SecretValue "ALIYUN_ACCESS_KEY_SECRET [keep existing]"
      if (-not $inputSecret) { $inputSecret = $curSecret }
      $inputRegion = Read-Host "ALIYUN_REGION (optional, e.g. cn-hongkong) [$curRegion]"
      if (-not $inputRegion) { $inputRegion = $curRegion }
      if (-not $inputId -or -not $inputSecret) { throw "access key id and secret are required" }
      $lines = @("ALIYUN_ACCESS_KEY_ID=$inputId", "ALIYUN_ACCESS_KEY_SECRET=$inputSecret")
      if ($inputRegion) { $lines += "ALIYUN_REGION=$inputRegion" }
      Set-Content -Encoding UTF8 -Path $file -Value $lines
    } elseif ($provider -eq "aws") {
      $curId = $existing["AWS_ACCESS_KEY_ID"]
      $curSecret = $existing["AWS_SECRET_ACCESS_KEY"]
      $curRegion = $existing["AWS_REGION"]
      $inputId = Read-Host "AWS_ACCESS_KEY_ID [$curId]"
      if (-not $inputId) { $inputId = $curId }
      $inputSecret = Read-SecretValue "AWS_SECRET_ACCESS_KEY [keep existing]"
      if (-not $inputSecret) { $inputSecret = $curSecret }
      $inputRegion = Read-Host "AWS_REGION (optional, e.g. us-east-1) [$curRegion]"
      if (-not $inputRegion) { $inputRegion = $curRegion }
      if (-not $inputId -or -not $inputSecret) { throw "access key id and secret are required" }
      $lines = @("AWS_ACCESS_KEY_ID=$inputId", "AWS_SECRET_ACCESS_KEY=$inputSecret")
      if ($inputRegion) { $lines += "AWS_REGION=$inputRegion" }
      Set-Content -Encoding UTF8 -Path $file -Value $lines
    } elseif ($provider -eq "azure") {
      $curSub = $existing["AZURE_SUBSCRIPTION_ID"]
      $curTenant = $existing["AZURE_TENANT_ID"]
      $curClient = $existing["AZURE_CLIENT_ID"]
      $curSecret = $existing["AZURE_CLIENT_SECRET"]
      $inputSub = Read-Host "AZURE_SUBSCRIPTION_ID [$curSub]"
      if (-not $inputSub) { $inputSub = $curSub }
      $inputTenant = Read-Host "AZURE_TENANT_ID [$curTenant]"
      if (-not $inputTenant) { $inputTenant = $curTenant }
      $inputClient = Read-Host "AZURE_CLIENT_ID [$curClient]"
      if (-not $inputClient) { $inputClient = $curClient }
      $inputSecret = Read-SecretValue "AZURE_CLIENT_SECRET [keep existing]"
      if (-not $inputSecret) { $inputSecret = $curSecret }
      if (-not $inputSub -or -not $inputTenant -or -not $inputClient -or -not $inputSecret) { throw "subscription id, tenant id, client id and client secret are required" }
      $lines = @("AZURE_SUBSCRIPTION_ID=$inputSub", "AZURE_TENANT_ID=$inputTenant", "AZURE_CLIENT_ID=$inputClient", "AZURE_CLIENT_SECRET=$inputSecret")
      Set-Content -Encoding UTF8 -Path $file -Value $lines
    } else {
      $token = Read-SecretValue $key
      if (-not $token) { throw "empty token is not allowed" }
      Set-Content -Encoding UTF8 -Path $file -Value "$key=$token"
    }
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
