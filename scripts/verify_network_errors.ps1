param([string]$Project = 'lr30')
$ErrorActionPreference = 'Stop'
function Compose { & docker compose -p $Project @args; if($LASTEXITCODE -ne 0){throw "Compose failed: $args"} }
$results = [Collections.Generic.List[object]]::new()
function Request([string]$Name,[int]$Expected) {
    $watch=[Diagnostics.Stopwatch]::StartNew()
    $r=Invoke-WebRequest -Uri http://127.0.0.1:8080/integration/notifications -Method Post -Headers @{Authorization="Bearer $script:token"} -ContentType 'application/json' -Body '{"recipient":"stable@cloud.local","message":"Network error handling enabled"}' -SkipHttpErrorCheck
    $watch.Stop()
    $item=[ordered]@{scenario=$Name;code=[int]$r.StatusCode;seconds=[Math]::Round($watch.Elapsed.TotalSeconds,3);body=($r.Content|ConvertFrom-Json)}
    $results.Add($item); $item | ConvertTo-Json -Compress | Write-Output
    if($r.StatusCode -ne $Expected){throw "Unexpected status for $Name"}
}
function Ready {
    for($i=0;$i -lt 30;$i++) {try {$r=Invoke-WebRequest http://127.0.0.1:8080/status; if($r.StatusCode -eq 200){return}} catch {}; Start-Sleep -Seconds 1}; throw 'API not ready'
}
Compose up -d
Ready
$password=[guid]::NewGuid().ToString('N')
$credentials=@{username=('lr30_'+[guid]::NewGuid().ToString('N').Substring(0,12));password=$password}|ConvertTo-Json
$r=Invoke-RestMethod http://127.0.0.1:8080/auth/register -Method Post -ContentType application/json -Body $credentials
Compose exec -T app python -c "from app.data.database import SessionLocal; from app.services.access import assign_role; db=SessionLocal(); assign_role(db,$($r.id),'operator'); db.close()"
$script:token=(Invoke-RestMethod http://127.0.0.1:8080/auth/login -Method Post -ContentType application/json -Body $credentials).access_token
try {
    Request A_running 201
    Compose stop notification
    Request B_stopped 503
    Compose start notification
    Start-Sleep -Seconds 2
    Request D_after_start 201
    Compose pause notification
    Request C_paused 504
    Compose unpause notification
    Request D_after_unpause 201
    $env:NOTIFICATION_TIMEOUT_SECONDS='1.0'
    Compose up -d --no-deps --force-recreate app
    Ready
    Compose pause notification
    Request timeout_1_second 504
    Compose unpause notification
    $env:NOTIFICATION_TIMEOUT_SECONDS='2.0'
    $env:NOTIFICATION_MAX_ATTEMPTS='2'
    $env:NOTIFICATION_RETRY_DELAY_SECONDS='0.25'
    Compose up -d --no-deps --force-recreate app
    Ready
    Compose stop notification
    Request attempts_2_delay_025 503
} finally {
    Compose unpause notification
    Compose start notification
    Remove-Item Env:NOTIFICATION_TIMEOUT_SECONDS,Env:NOTIFICATION_MAX_ATTEMPTS,Env:NOTIFICATION_RETRY_DELAY_SECONDS -ErrorAction SilentlyContinue
    Compose up -d --no-deps --force-recreate app
    Ready
    $results | ConvertTo-Json -Depth 6 | Set-Content evidence/lr30_results.json
}
Request final_restored 201
$results | ConvertTo-Json -Depth 6 | Set-Content evidence/lr30_results.json
Compose ps -a
