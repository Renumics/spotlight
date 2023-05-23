try {
    $Process = Start-Process spotlight-notebook -PassThru -NoNewWindow `
        -RedirectStandardError Output.log -ArgumentList "-y --no-browser"
    foreach ($i in 0..20) {
        $Match = Select-String -Path Output.log -Pattern "http://127.0.0.1:\S*" -List
        if ($Match -ne $Null) {
            break
        }
        Start-Sleep 0.5
    }
    if ($Match -eq $Null) {
        throw "No connection to Spotlight Notebook"
    }
    Invoke-WebRequest $Match.Matches.Value
}
finally {
    if ($Process -ne $Null) {
        Stop-Process -InputObject $Process
    }
}
