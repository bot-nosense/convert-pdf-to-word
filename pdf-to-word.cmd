@echo off
setlocal

rem Neu doi thu muc project, sua lai dong duoi day.
set "PROJECT_ROOT=E:\convert-pdf-to-word"
set "PORT=8080"
set "ENGINE=auto"

cd /d "%PROJECT_ROOT%" || (
    echo Khong tim thay thu muc project: %PROJECT_ROOT%
    exit /b 1
)

powershell.exe -NoProfile -NonInteractive -Command ^
  "if (Get-NetTCPConnection -LocalPort %PORT% -State Listen -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }" >nul 2>nul
if "%ERRORLEVEL%"=="0" exit /b 0

powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command ^
  "$root = '%PROJECT_ROOT%'; " ^
  "$script = Join-Path $root 'run_server.ps1'; " ^
  "$stdout = Join-Path $root 'server.out.log'; " ^
  "$stderr = Join-Path $root 'server.err.log'; " ^
  "Start-Process -FilePath 'powershell.exe' -WorkingDirectory $root -WindowStyle Hidden -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File',$script,'-Port','%PORT%','-ConverterEngine','%ENGINE%') -RedirectStandardOutput $stdout -RedirectStandardError $stderr"
exit /b %ERRORLEVEL%
