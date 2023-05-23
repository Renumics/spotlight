$Port = "5000"
$URL = "http://127.0.0.1:${Port}"

try {
    $Process = Start-Process spotlight -PassThru -NoNewWindow `
        -ArgumentList "--host 127.0.0.1 --port ${Port} --no-browser data/tables/tallymarks-small.h5"

    foreach ($i in 0..20) {
        try {
            $Response = Invoke-WebRequest "${URL}/api/table/"
            $GenerationID = ($Response.Content | ConvertFrom-Json).generation_id
        }
        catch {}
        if ($GenerationID -ne $Null) {
            break
        }
        Start-Sleep 0.5
    }
    if ($GenerationID -eq $Null) {
        throw "No connection to Spotlight"
    }
    Invoke-WebRequest "${URL}/api/table/number/42?generation_id=${GenerationID}"
}
finally {
    if ($Process -ne $Null) {
        Stop-Process -InputObject $Process
    }
}
