$ErrorActionPreference = "Stop"

$appName = "NovellaSquare"
$InstallDir = "$env:LOCALAPPDATA\$appName"

Write-Host "Uninstall..."

Remove-Item $InstallDir -Recurse -Force
Remove-Item "$env:USERPROFILE\Desktop\$appName.lnk" -Force

Write-Host "Done"