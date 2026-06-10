#!/usr/bin/env python3
"""
Script de teste local para geração do relatório ATS-02.

Uso:
    python test_generate.py [--data FILE] [--output FILE]

Exemplos:
    # Usar dados de teste padrão
    python test_generate.py

    # Usar arquivo de dados customizado
    python test_generate.py --data data/test_data_complete.json

    # Especificar arquivo de saída
    python test_generate.py --output relatorio_ufal_2024.pdf
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path


def load_test_data(data_file: Path) -> dict:
    """Carrega dados de teste do arquivo JSON."""
    print(f"📄 Carregando dados de teste: {data_file}")

    if not data_file.exists():
        print(f"❌ Erro: Arquivo não encontrado: {data_file}")
        sys.exit(1)

    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"✓ Dados carregados com sucesso")
    print(f"  - Instituição: {data['metadata']['universidade']}")
    print(f"  - Ano base: {data['params']['ano_base']}")

    return data


async def generate_report(data: dict, output_file: Path):
    """Gera o relatório PDF."""
    print("\n🔧 Inicializando executor ATS-02...")

    # Importar executor (do diretório local)
    try:
        # Adicionar diretório atual ao path para import local
        current_dir = Path(__file__).parent
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))

        # Importar executor do arquivo local
        from executor import ATS02Executor

        print("✓ Executor importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar executor: {e}")
        print(f"\nErro detalhado: {e}")
        print(f"Diretório atual: {Path.cwd()}")
        print(f"Arquivo executor: {Path(__file__).parent / 'executor.py'}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Inicializar executor
    reports_dir = Path(__file__).parent.parent
    executor = ATS02Executor(reports_dir)

    # Gerar relatório
    print("\n📊 Gerando gráficos...")
    print("⚙️  Compilando template Typst...")
    print("📄 Gerando PDF...\n")

    try:
        pdf_bytes = await executor.execute(data)
        print(f"✓ PDF gerado com sucesso ({len(pdf_bytes):,} bytes)")
    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Salvar PDF
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'wb') as f:
        f.write(pdf_bytes)

    print(f"\n✅ Relatório salvo em: {output_file.absolute()}")
    print(f"📊 Tamanho: {len(pdf_bytes) / 1024:.1f} KB")


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Gera relatório ATS-02 usando dados de teste locais (sem BigQuery)"
    )
    parser.add_argument(
        '--data',
        type=Path,
        default=Path(__file__).parent / 'data' / 'test_data_fake_charts.json',
        help='Arquivo JSON com dados de teste (padrão: data/test_data_fake_charts.json)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path(__file__).parent / 'output' / 'relatorio_ats02_teste.pdf',
        help='Arquivo PDF de saída (padrão: output/relatorio_ats02_teste.pdf)'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("  GERADOR DE RELATÓRIO ATS-02 - MODO TESTE LOCAL")
    print("=" * 70)
    print()

    # Carregar dados
    data = load_test_data(args.data)

    # Gerar relatório
    asyncio.run(generate_report(data, args.output))

    print()
    print("=" * 70)
    print("  ✅ PROCESSO CONCLUÍDO COM SUCESSO!")
    print("=" * 70)
    print()
    print(f"Para visualizar o relatório:")
    print(f"  open {args.output}  # macOS")
    print(f"  xdg-open {args.output}  # Linux")
    print(f"  start {args.output}  # Windows")
    print()


if __name__ == "__main__":
    main()
