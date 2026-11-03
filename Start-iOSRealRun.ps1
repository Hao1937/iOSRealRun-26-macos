param(
    [switch]$SkipMount
)

$ErrorActionPreference = "Stop"
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = Join-Path $ProjectDir ".pvenv"
$PythonExe = Join-Path $VenvDir "Scripts\python.exe"
$LocalDdiDir = Join-Path $ProjectDir "DeveloperDiskImage\PersonalizedImages\Xcode_iOS_DDI_Personalized"

function Test-IsAdmin {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)
}

if (-not (Test-IsAdmin)) {
    $arguments = @(
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-NoExit",
        "-File", "`"$PSCommandPath`""
    )
    if ($SkipMount) {
        $arguments += "-SkipMount"
    }

    Start-Process `
        -FilePath "powershell.exe" `
        -ArgumentList $arguments `
        -WorkingDirectory $ProjectDir `
        -Verb RunAs
    exit
}

Set-Location $ProjectDir
$env:PYTHONUTF8 = "1"

Write-Host "iOSRealRun launcher"
Write-Host "Project: $ProjectDir"
Write-Host ""

if (-not (Test-Path $PythonExe)) {
    Write-Host "Local virtual environment not found. Creating .pvenv..."
    $PythonLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($PythonLauncher) {
        & py -3 -m venv $VenvDir
    } else {
        $SystemPython = Get-Command python -ErrorAction SilentlyContinue
        if (-not $SystemPython) {
            Write-Host "Python was not found. Please install Python 3.10+ and try again." -ForegroundColor Red
            Read-Host "Press Enter to close"
            exit 1
        }
        & python -m venv $VenvDir
    }
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $PythonExe)) {
        Write-Host "Failed to create .pvenv." -ForegroundColor Red
        Read-Host "Press Enter to close"
        exit 1
    }
}

Write-Host "Python : $PythonExe"
Write-Host ""

& $PythonExe -c "import importlib.metadata as m; raise SystemExit(0 if tuple(map(int, m.version('pymobiledevice3').split('.')[:2])) >= (9, 12) else 1)"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing dependencies..."
    & $PythonExe -m pip install -U pip
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to upgrade pip." -ForegroundColor Red
        Read-Host "Press Enter to close"
        exit $LASTEXITCODE
    }
    & $PythonExe -m pip install -r .\requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install dependencies. You can retry later or install manually with:" -ForegroundColor Red
        Write-Host "$PythonExe -m pip install -r .\requirements.txt"
        Read-Host "Press Enter to close"
        exit $LASTEXITCODE
    }
}

& $PythonExe -c "import importlib.metadata as m; print('pymobiledevice3', m.version('pymobiledevice3'))"

if (-not $SkipMount) {
    Write-Host ""
    Write-Host "[1/2] Checking DeveloperDiskImage..."

    $mountedImages = (& $PythonExe -m pymobiledevice3 mounter list 2>&1 | Out-String)
    $isDeveloperImageMounted = (
        $LASTEXITCODE -eq 0 -and
        $mountedImages -match '"IsMounted"\s*:\s*true' -and
        $mountedImages -match '"MountPath"\s*:\s*"/System/Developer"'
    )

    if ($isDeveloperImageMounted) {
        Write-Host "DeveloperDiskImage is already mounted."
    } else {
        $image = Join-Path $LocalDdiDir "Image.dmg"
        $trustCache = Join-Path $LocalDdiDir "Image.dmg.trustcache"
        $buildManifest = Join-Path $LocalDdiDir "BuildManifest.plist"
        $localDdiReady = (
            (Test-Path -LiteralPath $image) -and
            (Test-Path -LiteralPath $trustCache) -and
            (Test-Path -LiteralPath $buildManifest)
        )

        if ($localDdiReady) {
            Write-Host "Mounting verified local DeveloperDiskImage..."
            & $PythonExe -m pymobiledevice3 mounter mount-personalized $image $trustCache $buildManifest
        } else {
            Write-Host "Local DeveloperDiskImage not found. Trying online auto-mount..."
            & $PythonExe -m pymobiledevice3 mounter auto-mount
        }
    }

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "DeveloperDiskImage mount command failed. Check that the iPhone/iPad is connected, unlocked, trusted, and Developer Mode is enabled." -ForegroundColor Yellow
        Read-Host "Press Enter to close"
        exit $LASTEXITCODE
    }
}

Write-Host ""
Write-Host "[2/2] Starting iOSRealRun. Use Ctrl+C in this window to stop safely."
Write-Host ""

& $PythonExe .\main.py
$exitCode = $LASTEXITCODE

Write-Host ""
Write-Host "iOSRealRun exited with code $exitCode"
Read-Host "Press Enter to close"
exit $exitCode
