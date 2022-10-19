# escape=`

FROM mcr.microsoft.com/windows/servercore:ltsc2019

LABEL Description="CI for PLCNext" Vendor="Websoft9" Version="0.9"

# Packages for build
ARG VS_INSTALLATION_DIR=C:\minVS
ARG BASIC_DIR=C:\myproject
ARG VS_URL="https://aka.ms/vs/16/release/vs_community.exe" 

ARG PLCNCLI_PATH=$BASIC_DIR\plcncli\PLCnCLI

ENV MSBUILD_ENV_SET $VS_INSTALLATION_DIR\Common7\Tools\Launch-VsDevShell.ps1

SHELL ["powershell", "-Command"]

WORKDIR ${BASIC_DIR}
COPY packages\* ${BASIC_DIR}\

# Download Visual Studio
RUN Invoke-WebRequest -URI $env:VS_URL -OutFile vs.exe

# Install VS
RUN `
    Start-Process vs.exe -ArgumentList "--installPath", "$env:VS_INSTALLATION_DIR", `
    "--add", "Microsoft.Net.Component.4.TargetingPack", `
    "--add", "Microsoft.VisualStudio.Component.Roslyn.Compiler", `
    "--add", "Microsoft.VisualStudio.Component.VC.14.20.x86.x64", `
    "--quiet", "--norestart" -wait -NoNewWindow -RedirectStandardOutput installvs.log

# Get the file of msi, and install it
RUN `
    $plugin = Get-ChildItem -Name -Filter *.msi;`
    Start-Process $plugin -ArgumentList "/quiet" -wait

# Delete install files, image size optimization
RUN Remove-Item *.zip,*.msi,*.xz,*.exe

VOLUME ${BASIC_DIR}

# Define the entry point for the docker container
ENTRYPOINT ["powershell.exe", "Invoke-Expression", "$env:MSBUILD_ENV_SET", ";", "powershell.exe", "-NoExit", "-ExecutionPolicy", "ByPass"]
