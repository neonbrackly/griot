# =============================================================================
# Start Griot Registry Development Environment (PowerShell)
# =============================================================================
# This script starts MongoDB and the Registry API with hot-reload enabled
#
# Usage:
#   .\scripts\start-dev.ps1              # Start in foreground
#   .\scripts\start-dev.ps1 -Detached    # Start in background
#   .\scripts\start-dev.ps1 -Command down    # Stop all services
#   .\scripts\start-dev.ps1 -Command logs    # View logs
# =============================================================================

param(
    [Parameter(Position=0)]
    [ValidateSet("up", "down", "logs", "restart", "clean", "status")]
    [string]$Command = "up",

    [switch]$Detached,

    [string]$Service = "registry"
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
$ComposeFile = Join-Path $ProjectDir "docker-compose.dev.yml"

# Change to monorepo root
$MonorepoRoot = Split-Path -Parent $ProjectDir
Push-Location $MonorepoRoot

try {
    switch ($Command) {
        "up" {
            Write-Host "[INFO] Starting Griot Registry development environment..." -ForegroundColor Green
            Write-Host "[INFO] MongoDB will be available at: mongodb://localhost:27017" -ForegroundColor Green
            Write-Host "[INFO] Registry API will be available at: http://localhost:8000" -ForegroundColor Green
            Write-Host "[INFO] Mongo Express (admin) will be available at: http://localhost:8081" -ForegroundColor Green
            Write-Host ""

            if ($Detached) {
                docker-compose -f $ComposeFile up -d --build
                Write-Host "[INFO] Services started in background" -ForegroundColor Green
                Write-Host "[INFO] View logs with: .\scripts\start-dev.ps1 -Command logs" -ForegroundColor Green
            } else {
                docker-compose -f $ComposeFile up --build
            }
        }

        "down" {
            Write-Host "[INFO] Stopping Griot Registry development environment..." -ForegroundColor Green
            docker-compose -f $ComposeFile down
        }

        "logs" {
            docker-compose -f $ComposeFile logs -f $Service
        }

        "restart" {
            Write-Host "[INFO] Restarting services..." -ForegroundColor Green
            docker-compose -f $ComposeFile restart $Service
        }

        "clean" {
            Write-Host "[WARN] This will remove all containers and volumes (data will be lost)!" -ForegroundColor Yellow
            $confirm = Read-Host "Are you sure? (y/N)"
            if ($confirm -eq "y" -or $confirm -eq "Y") {
                docker-compose -f $ComposeFile down -v
                Write-Host "[INFO] Cleaned up all containers and volumes" -ForegroundColor Green
            }
        }

        "status" {
            docker-compose -f $ComposeFile ps
        }
    }
} finally {
    Pop-Location
}
