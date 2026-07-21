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
    @{ Pattern = '林烬(最后也)?死了|林烬死于|林烬死后|林烬至死|林烬最终.{0,8}(死亡|死去)'; Label = '开放式结局被直接写死' },
    @{ Pattern = '林烬.{0,16}(肉身|魂魄|存在痕迹).{0,16}(燃尽|消散|消解)'; Label = '开放式结局被机制写死' },
    @{ Pattern = '云州'; Label = '旧行政州名未统一' },
    @{ Pattern = '九州灯火|九州皆焚'; Label = '九灯被误写为九州' },
    @{ Pattern = '通用六境|燃命境'; Label = '燃命被误列为正常境界' },
    @{ Pattern = '玩家|Boss|剧情杀'; Label = '小说设定混入游戏开发术语' },
    @{ Pattern = '第(一|二|三|四|五|六|七|八|九|十|十一)次残火'; Label = '残火旧次数标题回流' },
    @{ Pattern = '灰炉.{0,32}(残火苏醒|唤醒残火)'; Label = '灰炉被误写为残火获得地' },
    @{ Pattern = '第20章《[^》]{0,12}残火|第43章《[^》]{0,12}残火|第68章《[^》]{0,12}残火'; Label = '第一部旧残火节点回流' },
    @{ Pattern = '无人看见的熔钉|以残火(熔断|切断)|残火.{0,16}(精准|精确|稳定输出)'; Label = '残火被写成听令工具' },
    @{ Pattern = '引灰(替林烬|为林烬|帮助林烬).{0,16}(指出|破阵|预警)|引灰(发光|发热)预警'; Label = '引灰越权成为早期工具' },
    @{ Pattern = '共同守誓(意志)?.{0,12}(残火|火种)|残火.{0,12}共同守誓'; Label = '残火旧起源回流' },
    @{ Pattern = '任何境界(都)?可能燃命|高阶修士命火强行点亮'; Label = '命火被误写为高阶通用能力' },
    @{ Pattern = '迫使各方说明自己愿意承担什么、拒绝什么'; Label = '章卡回流汇报式表态模板' },
    @{ Pattern = '作出选择'; Label = '说明式选择措辞回流' }
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

$baselinePath = Join-Path $root '全局设定定稿基准.txt'
$requiredCanon = @(
    '世界名：玄尘大陆。',
    '燧京州、青州、北寒州、南疆州、渡厄州、云麓州、楚南州、东海州、西陵州、赤炎州、沧澜州、黑沙州。',
    '命火是性命本源，不是修为升高后自然掌握的力量；普通高阶修炼者也无法自行燃动。',
    '真正残火尚未进入故事。',
    '真正残火封入玄阳学院第七区地下的无灯窟',
    '九盏灯第一次同时回应的，是他们封住归墟的强烈意愿。',
    '第三部：林烬取得残火后对所有同伴隐瞒。除林烬本人外，没有任何人确认真相；叶无舟只从无灯窟焦痕、林烬伤势与几次异常中生疑',
    '第四部中段：沈青萝在替林烬治疗时，首先看见普通灵息反噬不可能留下的命源灼伤。',
    '第七部皇城线：天灯失控时，残火在公开灯讯与众目之下显现，存在由此无法再否认。',
    '林烬的境界时间线固定：第一部启息初入，第二部启息圆满，第三部前段以正常修行进入通脉；第六部化渊池一役进入照魂；第九部封印归墟前进入立域，封印归墟时借自身域相承接九灯与界线、进入承天。',
    '外物不是普通修行与立域的必需条件。修士凭自身灵根、内景与息律即可施术、起域',
    '灵器能够保存术痕与息律，既可放大主人术法，也可依靠器中积存、器灵或预炼术式独立发挥有限作用',
    '它并非只有代价：每次真正显现都能带来足以改变现场的力量',
    '林烬在封印时进入承天，界线重现后失踪。火幕散去前只允许出现一粒离开阵心、随即不知所终的微小火花',
    '最后一句固定为：“火还没有灭。”'
)
$missingCanon = @()
if (-not (Test-Path -LiteralPath $baselinePath)) {
    $missingCanon += '缺失《全局设定定稿基准》'
}
else {
    $baselineText = Get-Content -LiteralPath $baselinePath -Encoding UTF8 -Raw
    foreach ($required in $requiredCanon) {
        if (-not $baselineText.Contains($required)) {
            $missingCanon += $required
        }
    }
}

$rows | Sort-Object Start | Format-Table -AutoSize
Write-Output "CHAPTER_TOTAL=$($all.Count)"
Write-Output "CHAPTER_UNIQUE=$(($sorted | Sort-Object -Unique).Count)"
Write-Output "MISSING=$($missing.Count)"
Write-Output "DUPLICATES=$($duplicates.Count)"
Write-Output "MISSING_SOURCES=$($missingSources.Count)"
Write-Output "FORBIDDEN_HITS=$($forbiddenHits.Count)"
Write-Output "MISSING_CANON=$($missingCanon.Count)"
$forbiddenHits | ForEach-Object { Write-Output $_ }
$missingCanon | ForEach-Object { Write-Output "缺失定稿基准：$_" }

if ($files.Count -ne 9 -or $all.Count -ne 1250 -or $missing.Count -gt 0 -or $duplicates.Count -gt 0 -or $missingSources.Count -gt 0 -or $forbiddenHits.Count -gt 0 -or $missingCanon.Count -gt 0) {
    exit 1
}
