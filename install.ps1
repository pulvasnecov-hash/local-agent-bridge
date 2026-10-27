[CmdletBinding()]
param(
    [string]$OpenCodeExecutable = '',
    [string]$Model = ''
)
$ErrorActionPreference = 'Stop'
$configPath = Join-Path $PSScriptRoot 'bridge.local.json'
if (-not (Test-Path -LiteralPath $configPath)) {
    $config = Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot 'bridge.example.json') | ConvertFrom-Json
    if ($OpenCodeExecutable) {
        $config.opencode_command = @((Resolve-Path -LiteralPath $OpenCodeExecutable).Path)
    }
    $config.model = $Model
    $config | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $configPath -Encoding UTF8
    Write-Host 'Created bridge.local.json. Existing OpenCode settings were not changed.'
} else {
    Write-Host 'Keeping existing bridge.local.json. Edit it to change local settings.'
}
$pythonCommand = Get-Command py -ErrorAction SilentlyContinue
if ($pythonCommand) {
    & $pythonCommand.Source -3 (Join-Path $PSScriptRoot 'bridge.py') doctor
} else {
    $pythonCommand = Get-Command python -ErrorAction Stop
    & $pythonCommand.Source (Join-Path $PSScriptRoot 'bridge.py') doctor
}
exit $LASTEXITCODE
