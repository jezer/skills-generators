param(
    [Parameter(Mandatory=$true)] [string]$Config,
    [string]$Versao
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$python    = Join-Path $scriptDir "build_code_parquet.py"
$env:PYTHONIOENCODING = "utf-8"

$argList = @("--config", $Config)
if ($Versao) { $argList += @("--versao", $Versao) }

Write-Host "code-parquet-builder: Config=$Config Versao=$Versao"
python $python @argList
