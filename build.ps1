Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$assetsPath = Join-Path $projectRoot "assets"
$iconPath = Join-Path $assetsPath "icon\favicon.ico"
$bundleAssetsArg = "${assetsPath};assets"

if (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} else {
    throw "Python launcher non trovato. Installa Python oppure rendi disponibile 'python' o 'py' nel PATH."
}

Push-Location $projectRoot

try {
    & $pythonCmd -m PyInstaller `
        --noconfirm `
        --clean `
        --onefile `
        --windowed `
        --name "WageWise" `
        --icon $iconPath `
    --specpath "build" `
    --workpath "build/pyinstaller" `
    --distpath "dist" `
        --add-data $bundleAssetsArg `
        main.py
}
finally {
    Pop-Location
}