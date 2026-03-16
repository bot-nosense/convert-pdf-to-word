param(
    [string]$Host = "0.0.0.0",
    [int]$Port = 8080,
    [string]$ConverterEngine = "pdf2docx"
)

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

$pythonExe = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

& $pythonExe -m pip install -r (Join-Path $PSScriptRoot "requirements.txt")

$env:HOST = $Host
$env:PORT = "$Port"
$env:CONVERTER_ENGINE = $ConverterEngine

Write-Host "Server local: http://$Host:$Port"
Write-Host "Converter engine: $ConverterEngine"

try {
    $addresses = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction Stop |
        Where-Object {
            $_.IPAddress -notlike "127.*" -and
            $_.IPAddress -notlike "169.254.*"
        } |
        Sort-Object -Property IPAddress -Unique |
        Select-Object -ExpandProperty IPAddress

    foreach ($address in $addresses) {
        Write-Host "LAN URL: http://$address:$Port"
    }
}
catch {
    Write-Host "Không thể tự động liệt kê địa chỉ LAN, nhưng server vẫn sẽ chạy."
}

& $pythonExe -m pdf_word_server
