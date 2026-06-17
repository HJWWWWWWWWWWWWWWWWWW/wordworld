$ErrorActionPreference = 'Stop'
$root = Resolve-Path (Join-Path $PSScriptRoot '..\..\..')
$indexPath = Join-Path $root '分类汇总\00_分类索引.txt'
$lines = Get-Content -LiteralPath $indexPath -Encoding UTF8
$current = $null
$groups = [ordered]@{}

foreach ($line in $lines) {
    if ($line -match '^###\s+(.+\.txt)$') {
        $current = $matches[1]
        $groups[$current] = [System.Collections.Generic.List[string]]::new()
    } elseif ($current -and $line -match '^-\s+(.+\.txt)$') {
        $groups[$current].Add($matches[1])
    }
}

foreach ($entry in $groups.GetEnumerator()) {
    $stem = [System.IO.Path]::GetFileNameWithoutExtension($entry.Key)
    $builder = [System.Text.StringBuilder]::new()
    [void]$builder.AppendLine("# 《残火长明》${stem}汇总")
    [void]$builder.AppendLine()
    foreach ($rel in $entry.Value) {
        $source = Join-Path $root $rel
        [void]$builder.AppendLine("## 来源文档：$rel")
        [void]$builder.AppendLine()
        if (Test-Path -LiteralPath $source) {
            [void]$builder.AppendLine((Get-Content -LiteralPath $source -Encoding UTF8 -Raw).TrimEnd())
        } else {
            [void]$builder.AppendLine("[缺失来源文档：$rel]")
        }
        [void]$builder.AppendLine()
    }
    $dest = Join-Path $root ('分类汇总\' + $entry.Key)
    [System.IO.File]::WriteAllText($dest, $builder.ToString(), [System.Text.UTF8Encoding]::new($false))
}

Write-Output "REBUILT=$($groups.Count)"
