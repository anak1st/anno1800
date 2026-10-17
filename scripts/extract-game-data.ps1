# 解包游戏数据：<game_dir>\maindata\data*.rda -> temp\db
#
# 依赖 RdaConsole（来自 anno-mods/RdaConsole）：把 download\RdaConsole.zip
# 解压到 tools\RdaConsole（默认路径，可用 -RdaConsole 覆盖）。
#
# 用法：
#   pwsh scripts\extract-game-data.ps1
#   pwsh scripts\extract-game-data.ps1 -DryRun              # 只打印命令，不解包
#   pwsh scripts\extract-game-data.ps1 -Out temp\_test -Filter 'config/gui/texts_chinese\.xml$'

param(
    [string]$RdaConsole,
    [string]$Out,
    [string]$Filter = 'config[/\\].*\.(xml|json)$',
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$cfgPath = Join-Path $root 'anno.json'
$cfg = if (Test-Path -LiteralPath $cfgPath) { Get-Content -LiteralPath $cfgPath -Raw | ConvertFrom-Json }
       else { [pscustomobject]@{ temp_dir = 'temp'; game_dir = '' } }

$game = $cfg.game_dir
if (-not $game) { throw 'anno.json 里没有 game_dir：按 README 第〇节新建 anno.json 并填游戏安装目录' }
if (-not $RdaConsole) { $RdaConsole = Join-Path $root 'tools\RdaConsole\build\RdaConsole.exe' }
if (-not (Test-Path -LiteralPath $RdaConsole)) {
    throw "找不到 RdaConsole：$RdaConsole`n把 download\RdaConsole.zip 解压到 tools\RdaConsole，或用 -RdaConsole 指定"
}

$maindata = Join-Path $game 'maindata'
if (-not (Test-Path -LiteralPath $maindata)) { throw "找不到 $maindata（anno.json 的 game_dir 配错了？）" }
$files = @(Get-ChildItem -LiteralPath $maindata -Filter 'data*.rda' -File | ForEach-Object FullName)
if ($files.Count -eq 0) { throw "在 $maindata 里没找到 data*.rda" }

if (-not $Out) { $Out = Join-Path $root (Join-Path $cfg.temp_dir 'db') }
$rdaArgs = @('extract', '-f') + $files + @('-o', $Out, '--filter', $Filter, '-y', '-n')

if ($DryRun) {
    Write-Host "RdaConsole : $RdaConsole"
    Write-Host "输入       : $($files.Count) 个 data*.rda（$maindata）"
    Write-Host "输出       : $Out"
    Write-Host ("命令       : & '{0}' {1}" -f $RdaConsole, ($rdaArgs -join ' '))
    return
}

& $RdaConsole @rdaArgs
if ($LASTEXITCODE -ne 0) { throw "RdaConsole 退出码 $LASTEXITCODE，解包失败" }
$written = @(Get-ChildItem -LiteralPath $Out -Recurse -File -ErrorAction SilentlyContinue)
if ($written.Count -eq 0) { throw "RdaConsole 没有产出文件（参数被拒？看上面的输出）" }

Write-Host "已解包到 $Out（$($written.Count) 个文件）"
Write-Host "下一步：pwsh scripts\build-card-table.ps1"
