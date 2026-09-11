backend_port := "8020"
frontend_port := "5173"

# Install backend (uv) and frontend (npm) dependencies
install:
    #!powershell.exe -NoProfile
    Write-Host "Installing backend dependencies (uv sync)..."
    Push-Location backend
    uv sync
    Pop-Location
    Write-Host "Installing frontend dependencies (npm install)..."
    Push-Location frontend
    npm install
    Pop-Location

# Start backend (FastAPI) and frontend (Vite) in the background
up:
    #!powershell.exe -NoProfile
    New-Item -ItemType Directory -Force -Path .run | Out-Null

    if (Test-Path .run/backend.pid) {
        Write-Host "Backend already running (or stale .run/backend.pid). Run 'just down' first."
    } else {
        $backend = Start-Process -FilePath "uv" -ArgumentList "run","uvicorn","app.main:app","--host","127.0.0.1","--port","{{backend_port}}" -WorkingDirectory "backend" -PassThru -WindowStyle Hidden
        Set-Content -Path .run/backend.pid -Value $backend.Id
        Write-Host "Backend started (PID $($backend.Id)) at http://127.0.0.1:{{backend_port}}"
    }

    if (Test-Path .run/frontend.pid) {
        Write-Host "Frontend already running (or stale .run/frontend.pid). Run 'just down' first."
    } else {
        $frontend = Start-Process -FilePath "cmd.exe" -ArgumentList "/c","npm","run","dev" -WorkingDirectory "frontend" -PassThru -WindowStyle Hidden
        Set-Content -Path .run/frontend.pid -Value $frontend.Id
        Write-Host "Frontend started (PID $($frontend.Id)) at http://127.0.0.1:{{frontend_port}}"
    }

# Stop backend and frontend started by `just up`
down:
    #!powershell.exe -NoProfile
    foreach ($name in "backend","frontend") {
        $pidFile = ".run/$name.pid"
        if (Test-Path $pidFile) {
            $procId = Get-Content $pidFile
            try {
                taskkill /PID $procId /T /F | Out-Null
                Write-Host "Stopped $name (PID $procId)"
            } catch {
                Write-Host "Could not stop $name (PID $procId): $_"
            }
            Remove-Item $pidFile -Force
        } else {
            Write-Host "$name is not running (no $pidFile)"
        }
    }

# Run backend tests
test:
    #!powershell.exe -NoProfile
    Push-Location backend
    uv run pytest
    Pop-Location

# Check whether backend/frontend are reachable
status:
    #!powershell.exe -NoProfile
    try {
        $health = Invoke-RestMethod "http://127.0.0.1:{{backend_port}}/health" -TimeoutSec 3
        Write-Host "Backend: $($health.status) (http://127.0.0.1:{{backend_port}})"
    } catch {
        Write-Host "Backend: not reachable (http://127.0.0.1:{{backend_port}})"
    }
    try {
        Invoke-WebRequest "http://127.0.0.1:{{frontend_port}}" -TimeoutSec 3 -UseBasicParsing | Out-Null
        Write-Host "Frontend: reachable (http://127.0.0.1:{{frontend_port}})"
    } catch {
        Write-Host "Frontend: not reachable (http://127.0.0.1:{{frontend_port}})"
    }
