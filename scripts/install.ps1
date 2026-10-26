<#
.SYNOPSIS
    Installs the Sketch-to-CAD skill into an Antigravity workspace.

.DESCRIPTION
    Copies the sketch-to-cad skill files into .agents/skills/sketch-to-cad/
    inside the target workspace. Safely detects existing installations and
    protects existing configuration.

.PARAMETER WorkspacePath
    Path to the target workspace directory. If omitted, prompts or defaults to the parent directory.

.PARAMETER Force
    Overwrite an existing installation without prompting for confirmation.

.PARAMETER DryRun
    Simulate the installation without copying any files.

.EXAMPLE
    .\scripts\install.ps1 -WorkspacePath "C:\Projects\MyProject"
    .\scripts\install.ps1 -DryRun
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false, Position = 0)]
    [string]$WorkspacePath,

    [Parameter(Mandatory = $false)]
    [switch]$Force,

    [Parameter(Mandatory = $false)]
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "   Sketch-to-CAD Skill Installer (v0.1.0)" -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

# 1. Locate repository root and source skill directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$SourceSkillDir = Join-Path $RepoRoot "skills\sketch-to-cad"

if (-not (Test-Path $SourceSkillDir)) {
    Write-Error "Source skill directory not found at: '$SourceSkillDir'. Please run this script from inside the repository."
    exit 1
}

$SkillFile = Join-Path $SourceSkillDir "SKILL.md"
if (-not (Test-Path $SkillFile)) {
    Write-Error "Invalid source skill: SKILL.md missing in '$SourceSkillDir'."
    exit 1
}

# 2. Determine target workspace path
if ([string]::IsNullOrWhiteSpace($WorkspacePath)) {
    $DefaultTarget = Split-Path -Parent $RepoRoot
    Write-Host "No -WorkspacePath specified." -ForegroundColor Yellow
    Write-Host "Default workspace: $DefaultTarget"
    $UserInput = Read-Host "Enter target workspace path (press Enter to accept default)"
    if ([string]::IsNullOrWhiteSpace($UserInput)) {
        $WorkspacePath = $DefaultTarget
    } else {
        $WorkspacePath = $UserInput.Trim('"', "'")
    }
}

if (-not (Test-Path $WorkspacePath)) {
    Write-Error "Target workspace path does not exist: '$WorkspacePath'."
    exit 1
}

$TargetAgentsDir = Join-Path $WorkspacePath ".agents"
$TargetSkillsDir = Join-Path $TargetAgentsDir "skills"
$TargetSkillDir = Join-Path $TargetSkillsDir "sketch-to-cad"

Write-Host "Source Skill : $SourceSkillDir" -ForegroundColor Gray
Write-Host "Target Skill : $TargetSkillDir" -ForegroundColor Gray

if ($DryRun) {
    Write-Host "`n[DRY RUN MODE] No files will be modified." -ForegroundColor Magenta
}

# 3. Check for existing installation
if (Test-Path $TargetSkillDir) {
    Write-Host "`nAn existing installation was detected at:" -ForegroundColor Yellow
    Write-Host "  $TargetSkillDir" -ForegroundColor Yellow
    
    if (-not $Force -and -not $DryRun) {
        $Confirm = Read-Host "`nDo you want to overwrite the existing skill? (y/N)"
        if ($Confirm -notmatch "^[Yy]$") {
            Write-Host "`nInstallation aborted by user. Existing files were preserved." -ForegroundColor Green
            exit 0
        }
    }
}

# 4. Perform Installation
try {
    if (-not $DryRun) {
        if (-not (Test-Path $TargetSkillsDir)) {
            New-Item -ItemType Directory -Path $TargetSkillsDir -Force | Out-Null
        }

        Copy-Item -Path $SourceSkillDir -Destination $TargetSkillsDir -Recurse -Force
    }

    Write-Host "`n------------------------------------------------" -ForegroundColor Green
    if ($DryRun) {
        Write-Host "  [DRY RUN] Skill installation preview passed!" -ForegroundColor Green
    } else {
        Write-Host "  [SUCCESS] Skill successfully installed!" -ForegroundColor Green
    }
    Write-Host "------------------------------------------------`n" -ForegroundColor Green

    Write-Host "Installed files location:"
    Write-Host "  $TargetSkillDir" -ForegroundColor White

    Write-Host "`nNext Steps to get started:" -ForegroundColor Cyan
    Write-Host "1. Configure your CADCraft MCP server in '$WorkspacePath\.agents\mcp_config.json'."
    Write-Host "   (See 'docs\cadcraft-mcp-setup.md' in this repository for a sample config)."
    Write-Host "2. Start or restart your Antigravity IDE / session in '$WorkspacePath'."
    Write-Host "3. Provide a floor plan sketch image and ask Antigravity to interpret it with sketch-to-cad."
    Write-Host "4. Review the structured model and approve proposed corrections before CAD generation.`n"

} catch {
    Write-Error "Failed to install skill: $_"
    exit 1
}
