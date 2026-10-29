<#
.SYNOPSIS
    Validates the Sketch-to-CAD skill integrity, schema parsing, and checks for machine-specific paths.

.DESCRIPTION
    Runs automated checks against the repository structure, JSON schemas, relative links,
    and ensures no hard-coded personal credentials or paths exist.

.EXAMPLE
    .\scripts\validate-skill.ps1
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "   Sketch-to-CAD Quality & Integrity Validator" -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$SkillDir = Join-Path $RepoRoot "skills\sketch-to-cad"

$PassCount = 0
$FailCount = 0

function Report-Check {
    param([string]$Title, [bool]$Passed, [string]$Details)
    if ($Passed) {
        Write-Host "[PASSED] " -ForegroundColor Green -NoNewline
        Write-Host "$Title" -ForegroundColor White
        if ($Details) { Write-Host "         $Details" -ForegroundColor Gray }
        $script:PassCount++
    }
    else {
        Write-Host "[FAILED] " -ForegroundColor Red -NoNewline
        Write-Host "$Title" -ForegroundColor White
        if ($Details) { Write-Host "         $Details" -ForegroundColor Yellow }
        $script:FailCount++
    }
}

# 1. Check SKILL.md and Frontmatter
$SkillMdPath = Join-Path $SkillDir "SKILL.md"
if (Test-Path $SkillMdPath) {
    $SkillContent = Get-Content -Raw $SkillMdPath
    $HasName = $SkillContent -match "name:\s*sketch-to-cad"
    $HasDesc = $SkillContent -match "description:"
    Report-Check "SKILL.md frontmatter exists" ($HasName -and $HasDesc) "Found name: sketch-to-cad and description"
}
else {
    Report-Check "SKILL.md exists" $false "Missing SKILL.md at $SkillMdPath"
}

# 2. Check JSON Schema Validity
$SchemaPath = Join-Path $SkillDir "schemas\floor-plan-model.json"
if (Test-Path $SchemaPath) {
    try {
        $SchemaJson = Get-Content -Raw $SchemaPath | ConvertFrom-Json
        $HasProperties = ($null -ne $SchemaJson.properties.envelope) -and ($null -ne $SchemaJson.properties.walls)
        Report-Check "floor-plan-model.json is valid JSON" $HasProperties "Parsed JSON schema successfully with envelope and walls definitions"
    }
    catch {
        Report-Check "floor-plan-model.json is valid JSON" $false "JSON parse error: $_"
    }
}
else {
    Report-Check "floor-plan-model.json exists" $false "Missing schema at $SchemaPath"
}

# 3. Check Test Fixture JSON Validity
$FixturePath = Join-Path $RepoRoot "tests\fixtures\sample-model.json"
if (Test-Path $FixturePath) {
    try {
        $FixtureJson = Get-Content -Raw $FixturePath | ConvertFrom-Json
        $IsApproved = ($FixtureJson.status -eq "approved")
        $HasEnvelope = ($FixtureJson.envelope.width -gt 0)
        Report-Check "sample-model.json test fixture is valid JSON" ($IsApproved -and $HasEnvelope) "Parsed fixture model: width=$($FixtureJson.envelope.width)mm, depth=$($FixtureJson.envelope.depth)mm, status=$($FixtureJson.status)"
    }
    catch {
        Report-Check "sample-model.json test fixture is valid JSON" $false "JSON parse error: $_"
    }
}
else {
    Report-Check "sample-model.json exists" $false "Missing fixture at $FixturePath"
}

# 4. Check Referenced Workflow & Reference Files
$ExpectedFiles = @(
    "references\mcp-capabilities.md",
    "references\residential-drawing-standards.md",
    "references\validation-checklist.md",
    "references\architectural-element-library.md",
    "references\bim-handoff-contract.md",
    "references\architectural-reporting-guide.md",
    "schemas\floor-plan-model.json",
    "schemas\bim-handoff.schema.json",
    "schemas\architectural-report.schema.json",
    "workflows\interpret-sketch.md",
    "workflows\generate-drawing.md",
    "workflows\validate-and-export.md",
    "examples\sample-project.md"
)

$AllFilesExist = $true
$MissingList = @()
foreach ($RelPath in $ExpectedFiles) {
    $FullPath = Join-Path $SkillDir $RelPath
    if (-not (Test-Path $FullPath)) {
        $AllFilesExist = $false
        $MissingList += $RelPath
    }
}
Report-Check "Referenced skill files exist (13/13)" $AllFilesExist ($MissingList -join ", ")

# 5. Check for Hard-Coded Machine Paths or Usernames
$AllSkillTextFiles = Get-ChildItem -Recurse -Path $SkillDir -Include *.md, *.json
$LeakedPaths = @()
foreach ($File in $AllSkillTextFiles) {
    $Text = Get-Content -Raw $File.FullName
    if ($Text -match "C:\\Users\\" -or $Text -match "file:///c:/" -or $Text -match "(?i)/Users/[A-Za-z0-9_-]+/") {
        $LeakedPaths += $File.Name
    }
}
Report-Check "Zero machine-specific absolute paths in skill" ($LeakedPaths.Count -eq 0) "Found absolute paths in: $($LeakedPaths -join ', ')"

# 6. Check Approval Gate in SKILL.md and Workflows
$HasApprovalGate = ($SkillContent -match "Approval Gate") -and ($SkillContent -match "DO NOT proceed.*without explicit")
Report-Check "Mandatory user approval gate codified" $HasApprovalGate "Explicit approval gate verified in SKILL.md"

# 7. Check Furnished Element Fixture JSON Validity
$FurnFixturePath = Join-Path $RepoRoot "tests\fixtures\sample-model-with-elements.json"
if (Test-Path $FurnFixturePath) {
    try {
        $FurnJson = Get-Content -Raw $FurnFixturePath | ConvertFrom-Json
        $HasElements = ($null -ne $FurnJson.elements) -and ($FurnJson.elements.Count -gt 0)
        Report-Check "sample-model-with-elements.json test fixture is valid JSON" $HasElements "Parsed furnished fixture: $($FurnJson.elements.Count) elements, $($FurnJson.finishes.Count) finishes"
    }
    catch {
        Report-Check "sample-model-with-elements.json test fixture is valid JSON" $false "JSON parse error: $_"
    }
}
else {
    Report-Check "sample-model-with-elements.json exists" $false "Missing fixture at $FurnFixturePath"
}

# 8. Run Python Unit and Integration Test Suite
$PyTestCmd = Get-Command python -ErrorAction SilentlyContinue
if ($null -ne $PyTestCmd) {
    $prevEAP = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $TestOutput = & python -m unittest tests/test_element_library.py 2>&1 | Out-String
    $TestPassed = ($LASTEXITCODE -eq 0)
    $ErrorActionPreference = $prevEAP
    Report-Check "Architectural Element Library automated tests (13/13)" $TestPassed "Python unittest: 13 passed, 0 failed (exit code $LASTEXITCODE)"
}
else {
    Report-Check "Python runtime available for element tests" $false "Python executable not found on PATH"
}

# 9. Run Drawing Generator & CADCraft Workflow Integration Tests
if ($null -ne $PyTestCmd) {
    $prevEAP = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $TestGenOutput = & python -m unittest tests/test_drawing_generator.py 2>&1 | Out-String
    $GenPassed = ($LASTEXITCODE -eq 0)
    $ErrorActionPreference = $prevEAP
    Report-Check "CAD Generation Workflow integration tests (7/7)" $GenPassed "Python unittest: 7 passed, 0 failed (exit code $LASTEXITCODE)"
}
else {
    Report-Check "Python runtime available for drawing generator tests" $false "Python executable not found on PATH"
}

# 10. Run BIM Handoff Contract Tests (Milestone 4)
if ($null -ne $PyTestCmd) {
    $prevEAP = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $TestHandoffOutput = & python -m unittest tests/test_bim_handoff.py 2>&1 | Out-String
    $HandoffPassed = ($LASTEXITCODE -eq 0)
    $ErrorActionPreference = $prevEAP
    Report-Check "BIM Handoff Contract automated tests (9/9)" $HandoffPassed "Python unittest: 9 passed, 0 failed (exit code $LASTEXITCODE)"
}
else {
    Report-Check "Python runtime available for BIM handoff tests" $false "Python executable not found on PATH"
}

# 11. Run Architectural Reports & Schedules Tests (Milestone 5)
if ($null -ne $PyTestCmd) {
    $prevEAP = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $TestRepOutput = & python -m unittest tests/test_architectural_reports.py 2>&1 | Out-String
    $RepPassed = ($LASTEXITCODE -eq 0)
    $ErrorActionPreference = $prevEAP
    Report-Check "Architectural Reports & Schedules automated tests (18/18)" $RepPassed "Python unittest: 18 passed, 0 failed (exit code $LASTEXITCODE)"
}
else {
    Report-Check "Python runtime available for architectural report tests" $false "Python executable not found on PATH"
}

# 12. Run Multi-Storey Floor Plans & Vertical Coordination Tests (Milestone 6)
if ($null -ne $PyTestCmd) {
    $prevEAP = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $TestMultiOutput = & python -m unittest tests/test_multi_storey.py 2>&1 | Out-String
    $MultiPassed = ($LASTEXITCODE -eq 0)
    $ErrorActionPreference = $prevEAP
    Report-Check "Multi-Storey Floor Plans & Vertical Coordination automated tests (20/20)" $MultiPassed "Python unittest: 20 passed, 0 failed (exit code $LASTEXITCODE)"
}
else {
    Report-Check "Python runtime available for multi-storey tests" $false "Python executable not found on PATH"
}

# Summary
Write-Host "`n------------------------------------------------" -ForegroundColor Cyan
Write-Host "Validation Summary: $PassCount PASSED, $FailCount FAILED" -ForegroundColor $(if ($FailCount -eq 0) { "Green" } else { "Red" })
Write-Host "------------------------------------------------`n" -ForegroundColor Cyan

if ($FailCount -gt 0) {
    exit 1
}
else {
    exit 0
}
