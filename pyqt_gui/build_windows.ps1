$ErrorActionPreference = "Stop"

$AppName = "bosonicflow-gkp"
$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RootDir

$PythonBin = $env:PYTHON_BIN
if (-not $PythonBin) {
  $PythonBin = (Get-Command python).Source
}

& $PythonBin -m PyInstaller --version *> $null
if ($LASTEXITCODE -ne 0) {
  & $PythonBin -m pip install pyinstaller
}

& $PythonBin -m PyInstaller `
  --noconfirm `
  --windowed `
  --name $AppName `
  --collect-submodules pennylane `
  main.py

New-Item -ItemType Directory -Force -Path downloads | Out-Null
$zipPath = Join-Path downloads "$AppName-windows.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath }
Compress-Archive -Path (Join-Path dist $AppName) -DestinationPath $zipPath
