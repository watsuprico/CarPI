$path = (Get-Location).ToString()
Get-ChildItem $path -recurse -include *.*| ForEach-Object { $_.Fullname.Replace($path + "\","").Replace("\","/") } | Where {$_ -ne "List.ps1"} > downloadList.txt
$file = [IO.File]::ReadAllText($path + "\downloadList.txt") -replace "`r`n", "`n"
[IO.File]::WriteAllText($path + "\downloadList.txt",$file)

Get-ChildItem $path -recurse -include *.*| ForEach-Object { $_.DirectoryName.Replace($path.ToString() + "\","").Replace("\","/") } | Where {$_ -ne $path} | Get-Unique > directoryList.txt
$file = [IO.File]::ReadAllText($path + "\directoryList.txt") -replace "`r`n", "`n"
[IO.File]::WriteAllText($path + "\directoryList.txt",$file)