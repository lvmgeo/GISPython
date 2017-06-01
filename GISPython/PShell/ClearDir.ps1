$Now = Get-Date
$InFolder = $args[0]
$InWhat = $args[1]

function Remove-Tree($Path,$Include='*') { 
    (Get-ChildItem $Path -Force -Filter $Include) | 
    Foreach { 
        Remove-Item -force -recurse ($Path + "\" + $_)
        echo ("`t`tRemovinge file: [" + $Path + "\" + $_ + "]")
    }
} 

echo ("")
echo ("--- Removing folder: [" + $InFolder + "]" )
Remove-Tree $InFolder $InWhat

exit