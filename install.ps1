# ╔══════════════════════════════════════════════════════════════╗
# ║  skill-blast — Windows PowerShell Installer                 ║
# ║  Run in PowerShell:                                         ║
# ║  irm https://raw.githubusercontent.com/Venkatesh-6921/       ║
# ║    skill-blast/main/install.ps1 | iex                       ║
# ╚══════════════════════════════════════════════════════════════╝

$ErrorActionPreference = "Stop"

function Write-Info    { Write-Host "  ▶  $args" -ForegroundColor Cyan }
function Write-Success { Write-Host "  ✓  $args" -ForegroundColor Green }
function Write-Warn    { Write-Host "  ⚠  $args" -ForegroundColor Yellow }
function Write-Err     { Write-Host "  ✗  $args" -ForegroundColor Red }

Write-Host ""
Write-Host "  skill-blast — 50 AI Agent Skills Installer" -ForegroundColor Cyan -BackgroundColor Black
Write-Host "  ─────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host ""

# ── Python check ───────────────────────────────────────────────────────────────
$PythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
        $major, $minor = $ver.Split(".")
        if ([int]$major -ge 3 -and [int]$minor -ge 9) {
            $PythonCmd = $cmd
            Write-Success "Python $ver found"
            break
        }
    } catch {}
}

if (-not $PythonCmd) {
    Write-Err "Python 3.9+ not found."
    Write-Host ""
    Write-Host "  Install Python from:" -ForegroundColor Yellow
    Write-Host "    https://www.python.org/downloads/windows/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  During install, check 'Add Python to PATH'" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to open the download page, then re-run this script"
    Start-Process "https://www.python.org/downloads/windows/"
    exit 1
}

# ── git check ──────────────────────────────────────────────────────────────────
try {
    $gitVer = git --version 2>$null
    Write-Success "git found: $gitVer"
} catch {
    Write-Err "git not found."
    Write-Host ""
    Write-Host "  Install git from:" -ForegroundColor Yellow
    Write-Host "    https://git-scm.com/download/win" -ForegroundColor Cyan
    Write-Host ""
    $open = Read-Host "Open download page? (y/n)"
    if ($open -eq "y") { Start-Process "https://git-scm.com/download/win" }
    exit 1
}

# ── Install skill-blast ────────────────────────────────────────────────────────
Write-Info "Installing skill-blast…"

# Prefer uv if available
if (Get-Command uv -ErrorAction SilentlyContinue) {
    Write-Info "Found uv, using it for installation…"
    try {
        uv pip install --upgrade skill-blast
        Write-Success "skill-blast installed via uv!"
    } catch {
        Write-Warn "uv install failed, falling back to pip…"
    }
}

if (-not (Get-Command skill-blast -ErrorAction SilentlyContinue)) {
    try {
        & $PythonCmd -m pip install --quiet --upgrade skill-blast
        Write-Success "skill-blast installed!"
    } catch {
        Write-Warn "Standard install failed, trying user install…"
        try {
            & $PythonCmd -m pip install --quiet --upgrade skill-blast --user
            Write-Success "skill-blast installed (user mode)!"
        } catch {
            Write-Err "pip install failed. Please try: pip install skill-blast"
            exit 1
        }
    }
}

# ── Verify and run ─────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  ✓ Ready! Launching skill-blast…" -ForegroundColor Green
Write-Host ""
Start-Sleep 1

# Refresh PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" +
            [System.Environment]::GetEnvironmentVariable("Path","User")

$SbAvailable = $null -ne (Get-Command skill-blast -ErrorAction SilentlyContinue)
if ($SbAvailable) {
    skill-blast $args
} else {
    Write-Warn "skill-blast not found in PATH. Using python -m skill_blast"
    Write-Host "  Tip: Restart your terminal to refresh PATH after pip install." -ForegroundColor Yellow
    & $PythonCmd -m skill_blast $args
}
