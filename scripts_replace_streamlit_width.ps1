Get-ChildItem -Recurse -Filter *.py |
ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content `
        -replace 'use_container_width\s*=\s*True', 'width="stretch"' `
        -replace 'use_container_width\s*=\s*False', 'width="content"'
    Set-Content $_.FullName $content
}
