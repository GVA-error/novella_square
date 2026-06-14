$ErrorActionPreference = "Stop"

$appName = "NovellaSquare"
$InstallDir = "$env:LOCALAPPDATA\$appName"


$TempDir = "$env:TEMP\novella_repo"
$ZipPath = "$env:TEMP\repo.zip"
$RepoZipUrl = "https://github.com/GVA-error/novella_square/archive/refs/heads/main.zip"

# =========================
# CLEAN TEMP
# =========================
Remove-Item $TempDir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $TempDir | Out-Null

# =========================
# DOWNLOAD
# =========================
Write-Host "Downloading repository..."

Invoke-WebRequest `
    -Uri $RepoZipUrl `
    -OutFile $ZipPath

# =========================
# EXTRACT
# =========================
Write-Host "Extracting..."

Expand-Archive `
    -Path $ZipPath `
    -DestinationPath $TempDir `
    -Force

# GitHub всегда создаёт папку типа repo-main
$repoRoot = Get-ChildItem $TempDir | Where-Object {
    $_.PSIsContainer
} | Select-Object -First 1

if (-not $repoRoot) {
    throw "Cannot find extracted repository folder"
}

# =========================
# INSTALL DIR PREP
# =========================
Write-Host "Preparing install directory..."

if (Test-Path $InstallDir) {
    Remove-Item $InstallDir -Recurse -Force
}

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

# =========================
# COPY FILES (SAFE MERGE)
# =========================
Write-Host "Copying files..."

Copy-Item `
    -Path "$($repoRoot.FullName)\*" `
    -Destination $InstallDir `
    -Recurse `
    -Force

# =========================
# CLEANUP
# =========================
Write-Host "Cleaning up..."

Remove-Item $ZipPath -Force -ErrorAction SilentlyContinue
Remove-Item $TempDir -Recurse -Force -ErrorAction SilentlyContinue


# =========================
# UV install
# =========================
Write-Host "UV install..."
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "Installing uv..."
    powershell -ExecutionPolicy ByPass -c `
        "irm https://astral.sh/uv/install.ps1 | iex"
    $env:Path += ";$env:USERPROFILE\.local\bin"
}

Set-Location $InstallDir
uv python install 3.11
uv sync

# =========================
# Create run file
# =========================
Write-Host "Create run file..."
$BatFile = "$InstallDir\run.bat"
@"
@echo off
cd /d "$InstallDir"
uv run main.py
"@ | Out-File $BatFile -Encoding ascii

# =========================
# Create shortcuts
# =========================
Write-Host "Create shortcuts..."
$Desktop = [Environment]::GetFolderPath("Desktop")
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut(
    "$Desktop\$appName.lnk"
)
$shortcut.TargetPath = $BatFile
$shortcut.WorkingDirectory = $InstallDir
$shortcut.IconLocation = "$InstallDir\resources\NS_logo_128.ico"
$shortcut.Save()

Set-Location "$env:LOCALAPPDATA"

Write-Host "Done"