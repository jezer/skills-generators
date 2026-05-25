BeforeAll {
    $script:SkillDir = Split-Path -Parent $PSScriptRoot
    $script:Script   = Join-Path $script:SkillDir "scripts\build_code_parquet.py"
    $script:Wrapper  = Join-Path $script:SkillDir "scripts\build-code-parquet.ps1"
    $script:Example  = Join-Path $script:SkillDir "templates\config.example.json"
}

Describe "code-parquet-builder structure" {
    It "tem build_code_parquet.py" { Test-Path $script:Script | Should -BeTrue }
    It "tem wrapper build-code-parquet.ps1 com param Config" {
        (Get-Content -LiteralPath $script:Wrapper -Raw) | Should -Match "\[Parameter\(Mandatory=\`$true\)\]\s*\[string\]\`$Config"
    }
    It "tem config.example.json valido com campos obrigatorios" {
        Test-Path $script:Example | Should -BeTrue
        $j = Get-Content -LiteralPath $script:Example -Raw | ConvertFrom-Json
        $j.versao | Should -Not -BeNullOrEmpty
        $j.base_python | Should -Not -BeNullOrEmpty
        $j.output_dir | Should -Not -BeNullOrEmpty
        $j.tabela | Should -Not -BeNullOrEmpty
        $j.fontes | Should -Not -BeNullOrEmpty
    }
    It "py --help nao falha" {
        $out = (& python $script:Script --help 2>&1) -join "`n"
        $out | Should -Match "usage:"
        $out | Should -Match "--config"
    }
}
