param(
    [Parameter(Mandatory = $false)]
    [string]$Ip = "192.168.10.2",

    [Parameter(Mandatory = $false)]
    [int]$Port = 5000
)

function Send-TcpCmd {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Cmd
    )

    $tcp = New-Object System.Net.Sockets.TcpClient($Ip, $Port)
    $stream = $tcp.GetStream()
    $writer = New-Object System.IO.StreamWriter($stream)
    $reader = New-Object System.IO.StreamReader($stream)
    $writer.AutoFlush = $true

    $banner = $reader.ReadLine()
    $writer.WriteLine($Cmd)
    $response = $reader.ReadLine()

    $tcp.Close()

    [PSCustomObject]@{
        Command = $Cmd
        Banner  = $banner
        Reply   = $response
    }
}

$commands = @(
    "PING",
    "SET 1 1",
    "GET 1",
    "SET 1 0",
    "GET ALL"
)

foreach ($cmd in $commands) {
    Send-TcpCmd -Cmd $cmd
}

