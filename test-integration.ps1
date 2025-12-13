# NEON Integration Test Script (PowerShell)
# Run this script in PowerShell to verify all components are working

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "NEON Integration Test Suite" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$TestsPassed = 0
$TestsFailed = 0

function Test-Command {
    param(
        [string]$Name,
        [scriptblock]$Command
    )

    Write-Host "Testing: $Name... " -NoNewline

    try {
        $null = & $Command
        Write-Host "✓ PASSED" -ForegroundColor Green
        $script:TestsPassed++
        return $true
    } catch {
        Write-Host "✗ FAILED" -ForegroundColor Red
        $script:TestsFailed++
        return $false
    }
}

function Test-HttpEndpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$ExpectedContent
    )

    Write-Host "Testing: $Name... " -NoNewline

    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing
        if ($response.Content -match $ExpectedContent) {
            Write-Host "✓ PASSED" -ForegroundColor Green
            $script:TestsPassed++
            return $true
        } else {
            Write-Host "✗ FAILED" -ForegroundColor Red
            $script:TestsFailed++
            return $false
        }
    } catch {
        Write-Host "✗ FAILED" -ForegroundColor Red
        Write-Host "  Error: $_" -ForegroundColor Yellow
        $script:TestsFailed++
        return $false
    }
}

Write-Host "1. Checking Prerequisites" -ForegroundColor Yellow
Write-Host "-------------------------"

Test-Command "Docker is running" { docker ps | Out-Null }
Test-Command "Python is installed" { python --version | Out-Null }
Test-Command "Node.js is installed" { node --version | Out-Null }

Write-Host ""
Write-Host "2. Checking Services" -ForegroundColor Yellow
Write-Host "-------------------"

Test-Command "Database container running" { docker ps | Select-String "neon_db" | Out-Null }
Test-Command "Backend container running" { docker ps | Select-String "neon_backend" | Out-Null }

Write-Host ""
Write-Host "3. Testing Backend API" -ForegroundColor Yellow
Write-Host "---------------------"

Test-HttpEndpoint "Health endpoint" "http://localhost:8000/health" "healthy"
Test-HttpEndpoint "Vendors endpoint" "http://localhost:8000/api/v1/images/vendors/" "cisco"
Test-HttpEndpoint "Images endpoint" "http://localhost:8000/api/v1/images/" "ceos"
Test-HttpEndpoint "Chat suggestions" "http://localhost:8000/api/v1/chat/suggestions" "suggestions"

Write-Host ""
Write-Host "4. Testing Lab Operations" -ForegroundColor Yellow
Write-Host "------------------------"

Write-Host "Creating test lab... " -NoNewline
try {
    $labBody = @{
        name = "Integration Test Lab"
        description = "Automated test"
    } | ConvertTo-Json

    $labResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/labs/" `
        -Method Post `
        -ContentType "application/json" `
        -Body $labBody

    if ($labResponse.name -eq "Integration Test Lab") {
        Write-Host "✓ PASSED" -ForegroundColor Green
        $TestsPassed++

        $labId = $labResponse.id
        Write-Host "  Lab ID: $labId" -ForegroundColor Gray

        # Get first image ID
        $images = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/images/"
        $imageId = $images.images[0].id

        # Add a node
        Write-Host "Adding node to lab... " -NoNewline
        $nodeBody = @{
            name = "TestRouter"
            image_id = $imageId
            position_x = 100
            position_y = 100
        } | ConvertTo-Json

        $nodeResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/labs/$labId/nodes" `
            -Method Post `
            -ContentType "application/json" `
            -Body $nodeBody

        if ($nodeResponse.name -eq "TestRouter") {
            Write-Host "✓ PASSED" -ForegroundColor Green
            $TestsPassed++
        } else {
            Write-Host "✗ FAILED" -ForegroundColor Red
            $TestsFailed++
        }

        # Get lab details
        Write-Host "Retrieving lab details... " -NoNewline
        $labDetails = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/labs/$labId"

        if ($labDetails.nodes.Count -gt 0) {
            Write-Host "✓ PASSED" -ForegroundColor Green
            $TestsPassed++
        } else {
            Write-Host "✗ FAILED" -ForegroundColor Red
            $TestsFailed++
        }

        # Clean up - delete lab
        Write-Host "Deleting test lab... " -NoNewline
        $deleteResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/labs/$labId" -Method Delete

        if ($deleteResponse.message -match "deleted") {
            Write-Host "✓ PASSED" -ForegroundColor Green
            $TestsPassed++
        } else {
            Write-Host "✗ FAILED" -ForegroundColor Red
            $TestsFailed++
        }
    } else {
        Write-Host "✗ FAILED" -ForegroundColor Red
        $TestsFailed++
    }
} catch {
    Write-Host "✗ FAILED" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Yellow
    $TestsFailed++
}

Write-Host ""
Write-Host "5. Testing Frontend" -ForegroundColor Yellow
Write-Host "------------------"

if (Test-Path "frontend\dist") {
    Write-Host "Frontend build exists: ✓ PASSED" -ForegroundColor Green
    $TestsPassed++
} else {
    Write-Host "Frontend build missing: ⚠ SKIPPED" -ForegroundColor Yellow
    Write-Host "  Run 'cd frontend; npm run build' to create build" -ForegroundColor Gray
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Test Results" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Tests Passed: " -NoNewline
Write-Host "$TestsPassed" -ForegroundColor Green
Write-Host "Tests Failed: " -NoNewline
Write-Host "$TestsFailed" -ForegroundColor Red
Write-Host ""

if ($TestsFailed -eq 0) {
    Write-Host "✓ All tests passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "  1. Open http://localhost:8000/docs in your browser"
    Write-Host "  2. Start frontend: cd frontend; npm run dev"
    Write-Host "  3. Open http://localhost:5173 to see the UI"
    exit 0
} else {
    Write-Host "✗ Some tests failed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:"
    Write-Host "  1. Check docker-compose logs: docker-compose logs"
    Write-Host "  2. Verify services: docker-compose ps"
    Write-Host "  3. Restart services: docker-compose restart"
    exit 1
}
