param(
    [Parameter(Mandatory = $true)][string]$Skill,
    [Parameter(Mandatory = $true)][string]$Nome,
    [ValidateSet("ps1", "py")][string]$Tipo = "ps1",
    [string]$Descricao = "Automacao parametrizada.",
    [string]$SkillsRoot = "C:\codes\skills"
)

$ErrorActionPreference = "Stop"

if ($Skill -notmatch '^[a-z0-9-]+$') {
    throw "Nome de skill invalido: $Skill"
}

if ($Nome -notmatch '^[a-z0-9-]+$') {
    throw "Nome de script invalido: $Nome"
}

$skillPath = Join-Path $SkillsRoot $Skill
$skillFile = Join-Path $skillPath "SKILL.md"

if (-not (Test-Path -LiteralPath $skillFile)) {
    throw "Skill nao encontrada: $skillPath"
}

$scriptsPath = Join-Path $skillPath "scripts"
New-Item -ItemType Directory -Path $scriptsPath -Force | Out-Null

$scriptFile = Join-Path $scriptsPath "$Nome.$Tipo"
if (Test-Path -LiteralPath $scriptFile) {
    throw "Script ja existe: $scriptFile"
}

if ($Tipo -eq "ps1") {
    $conteudo = @"
param(
    [Parameter(Mandatory = `$true)][string]`$Entrada,
    [string]`$Saida = "."
)

`$ErrorActionPreference = "Stop"

if (-not `$Entrada) {
    throw "Entrada obrigatoria nao informada."
}

[pscustomobject]@{
    Entrada = `$Entrada
    Saida = `$Saida
    Status = "pendente-implementacao"
}
"@
} else {
    $conteudo = @"
import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="$Descricao")
    parser.add_argument("--entrada", required=True)
    parser.add_argument("--saida", default=".")
    args = parser.parse_args()

    print({
        "entrada": args.entrada,
        "saida": args.saida,
        "status": "pendente-implementacao",
    })


if __name__ == "__main__":
    main()
"@
}

Set-Content -LiteralPath $scriptFile -Value $conteudo -Encoding UTF8

[pscustomobject]@{
    Skill = $Skill
    Script = $scriptFile
    Tipo = $Tipo
    Descricao = $Descricao
}
