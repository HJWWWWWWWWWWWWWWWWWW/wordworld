$ErrorActionPreference = 'Stop'

$root = Resolve-Path (Join-Path $PSScriptRoot '..\..\..')
$draftName = [regex]::Unescape('\u521d\u7a3f')
$chapterPrefix = [regex]::Unescape('\u7b2c')
$chapterSuffix = [regex]::Unescape('\u7ae0\u005f')
$chapterNamePattern = '^' + [regex]::Escape($chapterPrefix) + '(\d{4})' + [regex]::Escape($chapterSuffix)
$draftDir = Join-Path $root $draftName
$constraintName = [regex]::Unescape('\u0030\u0030\u005f\u6b63\u6587\u521b\u4f5c\u4e0e\u6821\u9a8c\u603b\u7ea6\u675f\u002e\u0074\u0078\u0074')
$minimumCjk = 3000
$partNames = @(
    [regex]::Unescape('\u7b2c\u0030\u0031\u90e8\u005f\u7070\u7089\u4f59\u70ec'),
    [regex]::Unescape('\u7b2c\u0030\u0032\u90e8\u005f\u7384\u9633\u77ed\u68a6'),
    [regex]::Unescape('\u7b2c\u0030\u0033\u90e8\u005f\u9057\u7269\u88c2\u75d5'),
    [regex]::Unescape('\u7b2c\u0030\u0034\u90e8\u005f\u5357\u7586\u767e\u706b'),
    [regex]::Unescape('\u7b2c\u0030\u0035\u90e8\u005f\u5317\u5bd2\u5b64\u5173'),
    [regex]::Unescape('\u7b2c\u0030\u0036\u90e8\u005f\u5341\u4e8c\u5dde\u65e7\u7f6a'),
    [regex]::Unescape('\u7b2c\u0030\u0037\u90e8\u005f\u5929\u4e0b\u5171\u71c3'),
    [regex]::Unescape('\u7b2c\u0030\u0038\u90e8\u005f\u5f52\u589f\u524d\u591c'),
    [regex]::Unescape('\u7b2c\u0030\u0039\u90e8\u005f\u6b8b\u706b\u957f\u660e')
)

if (-not (Test-Path -LiteralPath $draftDir)) {
    Write-Output 'DRAFT_DIRECTORY_MISSING=1'
    exit 1
}

$constraintErrors = @()
$canonicalConstraint = Join-Path $draftDir $constraintName
if (-not (Test-Path -LiteralPath $canonicalConstraint)) {
    $constraintErrors += "missing canonical constraint: $canonicalConstraint"
}
else {
    $canonicalHash = (Get-FileHash -LiteralPath $canonicalConstraint -Algorithm SHA256).Hash
    foreach ($partName in $partNames) {
        $partDir = Join-Path $draftDir $partName
        $partConstraint = Join-Path $partDir $constraintName
        if (-not (Test-Path -LiteralPath $partDir)) {
            $constraintErrors += "missing part draft directory: $partDir"
            continue
        }
        if (-not (Test-Path -LiteralPath $partConstraint)) {
            $constraintErrors += "missing part constraint copy: $partConstraint"
            continue
        }
        $partHash = (Get-FileHash -LiteralPath $partConstraint -Algorithm SHA256).Hash
        if ($partHash -ne $canonicalHash) {
            $constraintErrors += "constraint copy mismatch: $partConstraint"
        }
    }
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

# These are deliberately narrow regressions for prose that turns an embodied
# scene into a load-bearing or task-allocation note. Broader words such as
# "负责" and "必须" remain valid in dialogue, decrees, and account books.
$styleRiskPatterns = @(
    '\u5c40\u90e8\u606f\u7eb9.{0,20}(\u627f\u91cd|\u6491\u4f4f\u6570\u606f)',
    '\u6bcf\u4e00\u6bb5.{0,16}\u627f\u91cd',
    '\u53d1\u529b\u65b9\u5f0f\u50cf',
    '\u5fc5\u987b\u8ba9.{0,24}(\u4fdd\u6301\u5e73\u7a33|\u59cb\u7ec8\u4fdd\u6301)',
    '\u7075\u606f\u53ea\u7559\u5728.{0,28}(\u810a\u80cc|\u5de6\u80a9)',
    '\u8d1f\u8d23\u6570\u547c\u5438',
    '\u8d1f\u8d23\u770b\u836f\u7089',
    '\u4e24\u4eba\u5206\u522b\u8d1f\u8d23',
    '\u5c40\u90e8\u606f\u7eb9',
    '\u5c06.{0,16}\u7075\u606f.{0,20}(\u53ea\u7559\u5728|\u5206\u914d\u5230|\u538b\u8fdb|\u5f15\u5165)',
    '\u5c06.{0,16}\u706b\u606f.{0,20}(\u5206\u914d\u5230|\u538b\u8fdb|\u5f15\u5165|\u9001\u5165)',
    '\u4f53\u5916\u606f\u8def',
    '\u606f\u7eb9.{0,20}(\u627f\u62c5|\u627f\u91cd|\u6491\u4f4f)',
    '\u7b2c\u4e00\u7f15.{0,100}\u7b2c\u4e8c\u7f15',
    '\u6b8b\u706b.{0,20}(\u538b\u7a33|\u7a33\u5b9a\u8f93\u51fa|\u7cbe\u786e\u5206\u914d)',
    '\u6697\u7ea2\u4eae\u5230\u54ea\u4e00\u5757',
    '\u5b8c\u6574\u606f\u8f6e.{0,20}\u4e3a\u951a',
    '\u4ed6(\u7ec8\u4e8e|\u7b2c\u4e00\u6b21|\u8fd9\u624d)?\u660e\u767d',
    '\u5979(\u7ec8\u4e8e|\u7b2c\u4e00\u6b21|\u8fd9\u624d)?\u660e\u767d',
    '\u8fd9\u4e0d\u662f.{0,50}\u800c\u662f',
    '\u771f\u6b63\u7684.{0,24}(\u662f|\u4e0d\u662f)',
    '\u8fd9\u8bf4\u660e',
    '\u8fd9\u610f\u5473\u7740',
    '\u613f\u610f\u627f\u62c5',
    '\u62d2\u7edd\u627f\u62c5',
    '\u8c01\u540c\u610f.{0,12}\u8c01\u4e0d\u540c\u610f',
    '\u64a4\u56de\u680f',
    '\u64a4\u56de\u7a97\u53e3',
    '\u4f5c\u51fa\u9009\u62e9',
    '\u4f9d\u6b21\u8868\u6001',
    '\u660e\u786e\u540c\u610f\u70b9\u706b',
    '\u5c1a\u672a\u540c\u610f\u70b9\u706b'
)

$magicTermPatterns = @(
    '\u7075\u606f',
    '\u606f\u7eb9',
    '\u606f\u8f6e',
    '\u6c14\u6d77',
    '\u672f\u75d5',
    '\u547d\u706b',
    '\u9b42\u5f71',
    '\u6b8b\u706b'
)

# Chapters 1-230 precede the actual acquisition in the third volume. These
# terms indicate that the retired early-awakening version has leaked back in.
# "引灰" is also forbidden in prose because no character, including Lin Jin,
# can identify or name it during the first two volumes.
$earlyPowerPatterns = @(
    '\u6b8b\u706b',
    '\u706b\u7ed3',
    '\u9aa8\u7eb9',
    '\u707c\u7eb9',
    '\u5f15\u7070',
    '\u6b8b\u706b\u5bbf\u4e3b',
    '\u8bb0\u5fc6.{0,12}(\u71c3\u6599|\u70e7\u8680|\u4ee3\u4ef7)',
    '\u5473\u89c9.{0,8}(\u4e27\u5931|\u6d88\u5931|\u5931\u53bb)',
    '\u836f\u5e03\u4e0b.{0,16}(\u6697\u7ea2|\u53d1\u4eae|\u4eae\u8d77|\u7741\u773c)',
    '\u53f3(\u638c|\u8155|\u81c2).{0,16}(\u6697\u7ea2.{0,8}(\u4eae|\u9192)|\u53d1\u4eae|\u4eae\u8d77|\u65e0\u706b\u81ea\u70ed)',
    '(\u672a\u77e5\u706b|\u5f02\u706b).{0,20}(\u6cbf\u76ae\u80a4|\u6551\u4eba|\u5931\u63a7)',
    '(\u5c1d\u4e0d\u51fa|\u5403\u4e0d\u51fa).{0,8}(\u7ca5|\u5c18\u571f|\u76d0|\u82e6)',
    '\u90a3\u56e2\u706b\u5148\u5403',
    '\u80f8\u53e3\u7684\u4e1c\u897f',
    '\u706b\u7ebf.{0,12}(\u5f80\u8098|\u722c)'
)

$files = Get-ChildItem -LiteralPath $draftDir -Recurse -File -Filter '*.txt'
$rows = @()
$numbers = @()
$forbiddenHits = @()
$styleRiskHits = @()

foreach ($file in $files) {
    if ($file.Name -notmatch $chapterNamePattern) {
        continue
    }

    $number = [int]$Matches[1]
    $numbers += $number
    $text = Get-Content -LiteralPath $file.FullName -Encoding UTF8 -Raw
    $body = $text -replace '\A(?:\uFEFF)?\u7b2c\d+\u7ae0[^\r\n]*(?:\r?\n)+', ''
    $body = $body -replace '(?m)^#.*$', ''
    $cjkCount = ([regex]::Matches($body, '[\p{IsCJKUnifiedIdeographs}]')).Count
    $fileHits = @()

    foreach ($pattern in $forbiddenPatterns) {
        $matches = [regex]::Matches($body, $pattern)
        foreach ($match in $matches) {
            $fileHits += $match.Value
            $forbiddenHits += "$($file.FullName): $($match.Value)"
        }
    }

    foreach ($pattern in $styleRiskPatterns) {
        $matches = [regex]::Matches($body, $pattern)
        foreach ($match in $matches) {
            $styleRiskHits += "$($file.FullName): $($match.Value)"
        }
    }

    if ($number -le 230) {
        foreach ($pattern in $earlyPowerPatterns) {
            $matches = [regex]::Matches($body, $pattern)
            foreach ($match in $matches) {
                $styleRiskHits += "$($file.FullName): early-residual-fire=$($match.Value)"
            }
        }
    }

    $paragraphs = [regex]::Split($body.Trim(), '\r?\n\s*\r?\n')
    foreach ($paragraph in $paragraphs) {
        $matchedMagicTerms = @($magicTermPatterns | Where-Object { [regex]::IsMatch($paragraph, $_) })
        if ($matchedMagicTerms.Count -ge 3) {
            $preview = ($paragraph -replace '\r?\n', ' ')
            if ($preview.Length -gt 80) {
                $preview = $preview.Substring(0, 80) + '...'
            }
            $styleRiskHits += "$($file.FullName): magic-term-density=$($matchedMagicTerms.Count): $preview"
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
$short = $rows | Where-Object CJK -lt $minimumCjk

$rows | Sort-Object Chapter | Format-Table -AutoSize
Write-Output "DRAFT_TOTAL=$($rows.Count)"
Write-Output "DRAFT_MAX=$maxChapter"
Write-Output "DRAFT_MISSING_TO_MAX=$($missing.Count)"
Write-Output "DRAFT_DUPLICATES=$($duplicates.Count)"
Write-Output "DRAFT_MINIMUM_CJK=$minimumCjk"
Write-Output "DRAFT_SHORT=$($short.Count)"
$short | Sort-Object Chapter | ForEach-Object {
    Write-Output "DRAFT_SHORT_CHAPTER=$($_.Chapter):$($_.CJK):$($_.File)"
}
Write-Output "DRAFT_CONSTRAINT_COPY_ERRORS=$($constraintErrors.Count)"
$constraintErrors | ForEach-Object { Write-Output $_ }
Write-Output "DRAFT_FORBIDDEN_HITS=$($forbiddenHits.Count)"
$forbiddenHits | ForEach-Object { Write-Output $_ }
Write-Output "DRAFT_STYLE_RISK_HITS=$($styleRiskHits.Count)"
$styleRiskHits | ForEach-Object { Write-Output $_ }

if ($missing.Count -gt 0 -or $duplicates.Count -gt 0 -or $short.Count -gt 0 -or $constraintErrors.Count -gt 0 -or $forbiddenHits.Count -gt 0 -or $styleRiskHits.Count -gt 0) {
    exit 1
}
