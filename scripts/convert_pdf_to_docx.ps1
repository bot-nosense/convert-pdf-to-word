param(
    [Parameter(Mandatory = $true)]
    [string]$InputPath,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath
)

$ErrorActionPreference = "Stop"
$wdAlertsNone = 0
$wdFormatDocumentDefault = 16
$wordOptionsRegistryPath = "HKCU:\SOFTWARE\Microsoft\Office\16.0\Word\Options"

$word = $null
$document = $null

try {
    if (-not (Test-Path -LiteralPath $InputPath)) {
        throw "Input PDF not found: $InputPath"
    }

    $resolvedInputPath = (Resolve-Path -LiteralPath $InputPath).Path
    $outputFolder = Split-Path -Parent $OutputPath
    if ($outputFolder -and -not (Test-Path -LiteralPath $outputFolder)) {
        New-Item -Path $outputFolder -ItemType Directory | Out-Null
    }

    $resolvedOutputPath = [System.IO.Path]::GetFullPath($OutputPath)

    if (-not (Test-Path -LiteralPath $wordOptionsRegistryPath)) {
        New-Item -Path $wordOptionsRegistryPath -Force | Out-Null
    }

    New-ItemProperty `
        -Path $wordOptionsRegistryPath `
        -Name "DisableConvertPDFWarning" `
        -PropertyType DWord `
        -Value 1 `
        -Force | Out-Null

    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = $wdAlertsNone
    $word.Options.ConfirmConversions = $false
    $word.Options.DoNotPromptForConvert = $true

    $document = $word.Documents.Open($resolvedInputPath, $false, $true)
    $document.SaveAs([ref]$resolvedOutputPath, [ref]$wdFormatDocumentDefault)
    $document.Close([ref]$false)
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($document)
    $document = $null
}
catch {
    Write-Error $_.Exception.Message
    exit 1
}
finally {
    if ($document -ne $null) {
        try {
            $document.Close([ref]$false)
        }
        catch {
        }

        try {
            [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($document)
        }
        catch {
        }
    }

    if ($word -ne $null) {
        try {
            $word.Quit()
        }
        catch {
        }

        try {
            [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($word)
        }
        catch {
        }
    }

    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
