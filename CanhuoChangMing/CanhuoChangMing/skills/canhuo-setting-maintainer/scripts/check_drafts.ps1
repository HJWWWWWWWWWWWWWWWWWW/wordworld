$ErrorActionPreference = 'Stop'

$root = Resolve-Path (Join-Path $PSScriptRoot '..\..\..')
$draftName = [regex]::Unescape('\u521d\u7a3f')
$chapterPrefix = [regex]::Unescape('\u7b2c')
$chapterSuffix = [regex]::Unescape('\u7ae0\u005f')
$chapterNamePattern = '^' + [regex]::Escape($chapterPrefix) + '(\d{4})' + [regex]::Escape($chapterSuffix)
$draftDir = Join-Path $root $draftName

if (-not (Test-Path -LiteralPath $draftDir)) {
    Write-Output 'DRAFT_DIRECTORY_MISSING=1'
    exit 1
}

$forbiddenPatterns = @(
    '\u7cfb\u7edf',
    '\u6570\u636e',
    '\u6982\u7387',
    '\u6307\u6807',
    '\u9879\u76ee',
    '\u6d41\u7a0b',
    '\u5e73\u53f0',
    '\u7f51\u7edc',
    '\u7535\u8bdd',
    '\u5c0f\u65f6(?!\u5019)',
    '\u516c\u91cc',
    '\u5408\u540c',
    '\u7ee9\u6548',
    '\u6548\u7387',
    '\u8206\u8bba',
    '\u516c\u5173',
    '\u5fc3\u7406\u521b\u4f24',
    '\u540e\u52e4\u4f53\u7cfb',
    '\u57fa\u56e0',
    '\u673a\u5236',
    '\u903b\u8f91',
    '\u98ce\u9669',
    '\u8d44\u6e90'
)

$files = Get-ChildItem -LiteralPath $draftDir -Recurse -File -Filter '*.txt'
$rows = @()
$numbers = @()
$forbiddenHits = @()

foreach ($file in $files) {
    if ($file.Name -notmatch $chapterNamePattern) {
        continue
    }

    $number = [int]$Matches[1]
    $numbers += $number
    $text = Get-Content -LiteralPath $file.FullName -Encoding UTF8 -Raw
    $body = $text -replace '(?m)^#.*$', ''
    $cjkCount = ([regex]::Matches($body, '[\p{IsCJKUnifiedIdeographs}]')).Count
    $fileHits = @()

    foreach ($pattern in $forbiddenPatterns) {
        $matches = [regex]::Matches($body, $pattern)
        foreach ($match in $matches) {
            $fileHits += $match.Value
            $forbiddenHits += "$($file.FullName): $($match.Value)"
        }
    }

    $rows += [pscustomobject]@{
        Chapter = $number
        CJK = $cjkCount
        Forbidden = (($fileHits | Sort-Object -Unique) -join ',')
        File = $file.Name
    }
}

$duplicates = $numbers | Group-Object | Where-Object Count -gt 1
$maxChapter = ($numbers | Measure-Object -Maximum).Maximum
$missing = @()
if ($null -ne $maxChapter) {
    $missing = 1..$maxChapter | Where-Object { $_ -notin $numbers }
}
$short = $rows | Where-Object CJK -lt 1500

$rows | Sort-Object Chapter | Format-Table -AutoSize
Write-Output "DRAFT_TOTAL=$($rows.Count)"
Write-Output "DRAFT_MAX=$maxChapter"
Write-Output "DRAFT_MISSING_TO_MAX=$($missing.Count)"
Write-Output "DRAFT_DUPLICATES=$($duplicates.Count)"
Write-Output "DRAFT_SHORT=$($short.Count)"
Write-Output "DRAFT_FORBIDDEN_HITS=$($forbiddenHits.Count)"
$forbiddenHits | ForEach-Object { Write-Output $_ }

if ($missing.Count -gt 0 -or $duplicates.Count -gt 0 -or $short.Count -gt 0 -or $forbiddenHits.Count -gt 0) {
    exit 1
}
