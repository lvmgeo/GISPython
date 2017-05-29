$Now = Get-Date
$Days = $args[2]
$InFolder = $args[0]
$OutFolder = $args[1]
$LastWrite = $Now.AddDays(-$Days)

echo ("")
echo ("--- Arhivejam direktoriju " + $InFolder + " uz " + $OutFolder + " pa pedejam " + $Days + " dienam - " + (Get-Date -format "HH:mm:ss"))
$Files = get-childitem -path $InFolder | 
Where {$_.psIsContainer -eq $false} | 
Where {$_.LastWriteTime -le "$LastWrite"} 

    foreach ($File in $Files)
    {if ($File -ne $NULL)
    {
    echo ("         Arhivejam: " + $InFolder + "\" + $File)
    Move-Item -Path ($InFolder + "\" + $File) -Destination ($OutFolder + "\" + $File) -Force
    }
    ELSE
    {echo ("         Faili nav atrasti")
     exit}
    }
exit