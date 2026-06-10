"""Custom charts bootstrap for ATM-EQ using the project chart framework."""

import importlib.util
import sys
from pathlib import Path


def _load_local_module(module_name: str, relative_path: str):
    """Load local modules by path (report folder contains hyphen, so regular import fails)."""
    module_path = Path(__file__).parent / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Nao foi possivel carregar modulo: {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_helpers = _load_local_module("atm_eq_chart_helpers", "charts/chart_helpers.py")
_load_local_module("atm_eq_image_dimensions", "charts/image_dimensions.py")

# Carrega os modulos especificos de cada grafico para que os decoradores @chart
# sejam registrados no momento da importacao.
_grafico_mapa_municipio_info = _load_local_module(
    "atm_eq_grafico_mapa_municipio_info",
    "charts/grafico_mapa_municipio_info.py",
)
_grafico_atendimento_creche_pre_escola = _load_local_module(
    "atm_eq_grafico_atendimento_creche_pre_escola",
    "charts/grafico_atendimento_creche_pre_escola.py",
)
_grafico_condicionalidades = _load_local_module(
    "atm_eq_grafico_condicionalidades",
    "charts/grafico_condicionalidades.py",
)
_grafico_distribuicao_matriculas = _load_local_module(
    "atm_eq_grafico_distribuicao_matriculas",
    "charts/grafico_distribuicao_matriculas.py",
)
_grafico_declaracao_racial = _load_local_module(
    "atm_eq_grafico_declaracao_racial",
    "charts/grafico_declaracao_racial.py",
)
_grafico_nivel_formacao_professores = _load_local_module(
    "atm_eq_grafico_nivel_formacao_professores",
    "charts/grafico_nivel_formacao_professores.py",
)
_grafico_infraestrutura_basica_empty_state = _load_local_module(
    "atm_eq_grafico_infraestrutura_basica_empty_state",
    "charts/grafico_infraestrutura_basica_empty_state.py",
)
_grafico_taxa_rendimento = _load_local_module(
    "atm_eq_grafico_taxa_rendimento",
    "charts/grafico_taxa_rendimento.py",
)
_grafico_vaar_municipio_2023_2025 = _load_local_module(
    "atm_eq_grafico_vaar_municipio_2023_2025",
    "charts/grafico_vaar_municipio_2023_2025.py",
)
_grafico_crescimento_vaar_fundeb_2023_2026 = _load_local_module(
    "atm_eq_grafico_crescimento_vaar_fundeb_2023_2026",
    "charts/grafico_crescimento_vaar_fundeb_2023_2026.py",
)
_grafico_condicionalidade_iii_desigualdade_racial = _load_local_module(
    "atm_eq_grafico_condicionalidade_iii_desigualdade_racial",
    "charts/grafico_condicionalidade_iii_desigualdade_racial.py",
)
_grafico_condicionalidade_iii_desigualdade_socioeconomica = _load_local_module(
    "atm_eq_grafico_condicionalidade_iii_desigualdade_socioeconomica",
    "charts/grafico_condicionalidade_iii_desigualdade_socioeconomica.py",
)

ensure_rawline_font_available = _helpers.ensure_rawline_font_available

# Initialize chart font once at module load (register Rawline if available).
ensure_rawline_font_available(strict=False)
