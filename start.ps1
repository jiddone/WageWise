$ErrorActionPreference = 'Stop'

$python = Join-Path $PSScriptRoot 'venv\Scripts\python.exe'
$main = Join-Path $PSScriptRoot 'main.py'

if (-not (Test-Path -LiteralPath $python)) {
    throw "Python del virtual environment non trovato: $python"
}

& $python $main