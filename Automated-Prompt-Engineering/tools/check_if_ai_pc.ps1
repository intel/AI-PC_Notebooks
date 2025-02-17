$ErrorActionPreference = 'Stop'

$cpuName = (Get-CimInstance -ClassName Win32_Processor).Name

# Write the CPU name to the console
Write-Output "CPU Name: $cpuName"

# Check if "Core(TM) Ultra" is present in the CPU name
if ($cpuName -like "*Core(TM) Ultra*") {
    Write-Output "The CPU is Core(TM) Ultra."
} else {
    throw "CPU does not match the required specification: Core(TM) Ultra."
}
