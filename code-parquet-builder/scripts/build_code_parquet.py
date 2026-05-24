"""Motor parametrizado para gerar parquet+csv de blocos de codigo Python.

Le um JSON de configuracao com a lista de arquivos fonte, ordem de cada modulo
e filtros de imports a remover. Salva os artefatos em `output_dir`.

Uso:
    python build_code_parquet.py --config caminho.json
    python build_code_parquet.py --config caminho.json --versao v3.1

JSON de configuracao (campos obrigatorios marcados com *):
{
    "versao": "v3.0",                     # *
    "base_python": "C:/...",              # * raiz para resolver paths relativos das fontes
    "output_dir": "C:/.../output",        # *
    "tabela": "tb_semaforo_cabecalho",    # * nome do artefato de saida
    "fontes": [                            # *
        {"arquivo": "lib_x/y.py", "modulo": "y", "ordem_base": 1},
        ...
    ],
    "init_blocos": [                       # opcional
        {"ordem": 1000, "modulo": "init", "tipo": "init",
         "nome": "criar_app", "descricao": "...", "codigo": "..."}
    ],
    "filtros": ["lib_createobj"]          # opcional - pacotes a filtrar
}
"""
from __future__ import annotations
import argparse
import ast
import json
import re
import sys
from pathlib import Path


def _carregar_pandas():
    try:
        import pandas as pd  # noqa
        return pd
    except ImportError:
        print("ERRO: pandas/pyarrow nao instalados. Execute: pip install pandas pyarrow", file=sys.stderr)
        sys.exit(1)


def construir_filtro(filtros: list[str]):
    padroes = [re.compile(r"^\s*from\s+\.+")]
    for pacote in filtros:
        nome = re.escape(pacote)
        padroes.append(re.compile(rf"^\s*from\s+{nome}(\.|$|\s)"))
        padroes.append(re.compile(rf"^\s*import\s+{nome}(\.|$|\s|,)"))

    def filtrar(codigo: str) -> str:
        linhas = codigo.splitlines(keepends=True)
        return "".join(l for l in linhas if not any(p.match(l) for p in padroes))

    return filtrar


def extrair_blocos(caminho: Path, modulo: str, ordem_base: int, filtrar) -> list[dict]:
    source = caminho.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"  AVISO: SyntaxError em {caminho.name}: {e} - pulando", file=sys.stderr)
        return []

    linhas = source.splitlines(keepends=True)
    top_nodes = [
        n for n in ast.iter_child_nodes(tree)
        if isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    ]

    blocos: list[dict] = []
    if top_nodes:
        primeira = min(n.lineno for n in top_nodes)
        topo = filtrar("".join(linhas[: primeira - 1])).strip()
        if topo:
            blocos.append({
                "ordem": ordem_base * 10,
                "modulo": modulo,
                "tipo": "import",
                "nome": f"imports_{modulo}",
                "descricao": f"Imports e inicializacoes globais de {modulo}",
                "codigo": topo,
            })

    for i, node in enumerate(top_nodes):
        tipo = "class" if isinstance(node, ast.ClassDef) else "function"
        start = node.lineno - 1
        end = node.end_lineno
        codigo = filtrar("".join(linhas[start:end])).rstrip()
        blocos.append({
            "ordem": ordem_base * 10 + i + 1,
            "modulo": modulo,
            "tipo": tipo,
            "nome": node.name,
            "descricao": "",
            "codigo": codigo,
        })
    return blocos


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera parquet+csv de blocos de codigo a partir de config JSON.")
    parser.add_argument("--config", required=True, help="Caminho do JSON de configuracao")
    parser.add_argument("--versao", default=None, help="Sobrescreve o campo versao do JSON")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))

    versao = args.versao or config["versao"]
    base_python = Path(config["base_python"])
    output_dir = Path(config["output_dir"])
    tabela = config["tabela"]
    fontes = config["fontes"]
    init_blocos = config.get("init_blocos", [])
    filtros = config.get("filtros", [])

    filtrar = construir_filtro(filtros)

    print(f"\n=== code-parquet-builder - versao {versao} ===\n")
    print(f"config       : {config_path}")
    print(f"base_python  : {base_python}")
    print(f"output_dir   : {output_dir}")
    print(f"tabela       : {tabela}")
    print(f"filtros      : {filtros or '(nenhum)'}")
    print()

    if not base_python.exists():
        print(f"ERRO: base_python nao existe: {base_python}", file=sys.stderr)
        return 1

    todos: list[dict] = []
    for f in fontes:
        caminho = base_python / f["arquivo"]
        if not caminho.exists():
            print(f"  [PULADO] {caminho} nao encontrado")
            continue
        b = extrair_blocos(caminho, f["modulo"], int(f["ordem_base"]), filtrar)
        for x in b:
            x["versao"] = versao
            x["ativo"] = True
        todos.extend(b)
        print(f"  [OK] {f['arquivo']} -> {len(b)} blocos (ordens {f['ordem_base']*10}-{f['ordem_base']*10+len(b)})")

    for b in init_blocos:
        b = dict(b)
        b["versao"] = versao
        b["ativo"] = True
        todos.append(b)
    if init_blocos:
        print(f"  [OK] init -> {len(init_blocos)} blocos")

    todos.sort(key=lambda x: x["ordem"])

    pd = _carregar_pandas()
    colunas = ["versao", "ordem", "modulo", "tipo", "nome", "codigo", "descricao", "ativo"]
    df = pd.DataFrame(todos, columns=colunas)

    output_dir.mkdir(parents=True, exist_ok=True)
    versao_slug = versao.replace(".", "_")
    parquet_path = output_dir / f"{tabela}_{versao_slug}.parquet"
    csv_path = output_dir / f"{tabela}_{versao_slug}.csv"
    df.to_parquet(parquet_path, index=False)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    print(f"\n--- Resultado ---")
    print(f"Blocos totais : {len(df)}")
    print(f"Parquet       : {parquet_path}")
    print(f"CSV           : {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
