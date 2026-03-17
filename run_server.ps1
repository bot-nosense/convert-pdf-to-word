param(
    [string]$BindHost = "0.0.0.0",
    [int]$Port = 8080,
    [string]$ConverterEngine = "auto"
)

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

$pythonExe = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

& $pythonExe -m pip install -r (Join-Path $PSScriptRoot "requirements.txt")

$env:HOST = $BindHost
$env:PORT = "$Port"
$env:CONVERTER_ENGINE = $ConverterEngine

& $pythonExe -m pdf_word_server
