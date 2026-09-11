# PAGENT Setup Verification Script for Windows
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  PAGENT Setup Verification" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Check Docker
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker installed: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker not found. Please install Docker Desktop." -ForegroundColor Red
    Write-Host "   Download from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Check Docker is running
Write-Host ""
Write-Host "Checking Docker daemon..." -ForegroundColor Yellow
try {
    docker info 2>&1 | Out-Null
    Write-Host "✅ Docker daemon is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker daemon is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check just
Write-Host ""
Write-Host "Checking just (command runner)..." -ForegroundColor Yellow
try {
    $justVersion = just --version
    Write-Host "✅ just installed: $justVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠️  just not found (optional but recommended)" -ForegroundColor Yellow
    Write-Host "   Install: scoop install just" -ForegroundColor Yellow
}

# Check .env files
Write-Host ""
Write-Host "Checking environment files..." -ForegroundColor Yellow
if (Test-Path "backend\.env") {
    Write-Host "✅ backend\.env exists" -ForegroundColor Green

    # Check if credentials are configured
    $envContent = Get-Content "backend\.env" -Raw
    if ($envContent -match "your-username" -or $envContent -match "your-password") {
        Write-Host "⚠️  Backend credentials not configured yet (still using placeholders)" -ForegroundColor Yellow
    } else {
        Write-Host "✅ Backend credentials configured" -ForegroundColor Green
    }
} else {
    Write-Host "❌ backend\.env not found" -ForegroundColor Red
}

if (Test-Path "frontend\.env") {
    Write-Host "✅ frontend\.env exists" -ForegroundColor Green
} else {
    Write-Host "❌ frontend\.env not found" -ForegroundColor Red
}

# Check ports
Write-Host ""
Write-Host "Checking if ports are available..." -ForegroundColor Yellow
$port8020 = Get-NetTCPConnection -LocalPort 8020 -ErrorAction SilentlyContinue
if (-not $port8020) {
    Write-Host "✅ Port 8020 (backend) is available" -ForegroundColor Green
} else {
    Write-Host "⚠️  Port 8020 (backend) is already in use" -ForegroundColor Yellow
    Write-Host "   Process ID: $($port8020.OwningProcess)" -ForegroundColor Gray
}

$port5173 = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue
if (-not $port5173) {
    Write-Host "✅ Port 5173 (frontend) is available" -ForegroundColor Green
} else {
    Write-Host "⚠️  Port 5173 (frontend) is already in use" -ForegroundColor Yellow
    Write-Host "   Process ID: $($port5173.OwningProcess)" -ForegroundColor Gray
}

# Summary
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  Setup Status" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the application:" -ForegroundColor White
Write-Host "  1. Edit backend\.env with your credentials" -ForegroundColor White
Write-Host "  2. Run: docker compose up -d" -ForegroundColor White
Write-Host "  3. Open: http://localhost:5173" -ForegroundColor White
Write-Host ""
Write-Host "For more details, see SETUP_CHECKLIST.md" -ForegroundColor Gray
Write-Host ""
