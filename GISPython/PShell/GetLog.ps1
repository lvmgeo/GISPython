$logs = "system","application"
$ComputerName = $args[0]
$OutputDir = $args[1]
$Days = $args[2]
$current = get-date
$oldDate = $current.adddays(-$Days)
$DateStr = Get-Date -format yyyy-MM-dd_HH-mm
$logs | % { echo ("    Beginning export " + $ComputerName + "_" + $_ + "_" + $DateStr + ".xml " + (Get-Date -format "HH:mm:ss"))
            Get-WinEvent -LogName $_ -ComputerName $ComputerName -ErrorAction SilentlyContinue | Where-Object { ( ($_.TimeCreated -ge $oldDate) ) } |  Export-Clixml ($OutputDir + "\" + $ComputerName + "_" + $_ + "_" + $DateStr + ".xml")
            echo ("     ... Finishing export " + (Get-Date -format "HH:mm:ss") + " ...") }