$ErrorActionPreference = 'Stop'
$root = Resolve-Path (Join-Path $PSScriptRoot '..\..\..')
$planDir = Join-Path $root '长篇规划'
$summaryDir = Join-Path $root '分类汇总'

$files = Get-ChildItem -LiteralPath (Join-Path $planDir '02_正式章节卡') -Filter '*正式章节卡.txt'
$all = @()
$rows = @()
foreach ($file in $files) {
    $text = Get-Content -LiteralPath $file.FullName -Encoding UTF8 -Raw
    $nums = [regex]::Matches($text, '(?m)^第(\d+)章') | ForEach-Object { [int]$_.Groups[1].Value }
    $all += $nums
    $rows += [pscustomobject]@{
        File = $file.Name
        Count = $nums.Count
        Start = ($nums | Measure-Object -Minimum).Minimum
        End = ($nums | Measure-Object -Maximum).Maximum
    }
}

$sorted = $all | Sort-Object
$missing = 1..1250 | Where-Object { $_ -notin $sorted }
$duplicates = $sorted | Group-Object | Where-Object Count -gt 1
$missingSources = @()
if (Test-Path -LiteralPath $summaryDir) {
    $missingSources = Get-ChildItem -LiteralPath $summaryDir -Filter '*.txt' |
        Select-String -Pattern '\[缺失来源文档'
}

$forbidden = @(
    @{ Pattern = '阿杳：魂毒'; Label = '阿杳/阿遥同名冲突' },
    @{ Pattern = '林烬(已经|确认|确定).*无复活'; Label = '开放式结局被封死' },
    @{ Pattern = '林烬(已经|确认|确定).*彻底死亡'; Label = '开放式结局被封死' },
    @{ Pattern = '林烬(最后也)?死了|林烬死于|林烬死后'; Label = '开放式结局被直接写死' }
)
$forbiddenHits = @()
foreach ($rule in $forbidden) {
    $hits = Get-ChildItem -LiteralPath $root -Recurse -File -Filter '*.txt' |
    Where-Object { $_.FullName -notlike '*\分类汇总\*' -and $_.FullName -notlike '*\长篇规划\04_旧版核心事件\*' -and $_.Name -ne '残火长明-剧情大纲.txt' } |
        Select-String -Pattern $rule.Pattern
    foreach ($hit in $hits) {
        $forbiddenHits += "$($rule.Label): $($hit.Path):$($hit.LineNumber)"
    }
}

$rows | Sort-Object Start | Format-Table -AutoSize
Write-Output "CHAPTER_TOTAL=$($all.Count)"
Write-Output "CHAPTER_UNIQUE=$(($sorted | Sort-Object -Unique).Count)"
Write-Output "MISSING=$($missing.Count)"
Write-Output "DUPLICATES=$($duplicates.Count)"
Write-Output "MISSING_SOURCES=$($missingSources.Count)"
Write-Output "FORBIDDEN_HITS=$($forbiddenHits.Count)"
$forbiddenHits | ForEach-Object { Write-Output $_ }

if ($files.Count -ne 9 -or $all.Count -ne 1250 -or $missing.Count -gt 0 -or $duplicates.Count -gt 0 -or $missingSources.Count -gt 0 -or $forbiddenHits.Count -gt 0) {
    exit 1
}
