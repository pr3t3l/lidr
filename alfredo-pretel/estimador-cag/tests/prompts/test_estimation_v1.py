"""
Tests del template `estimation/v1`. Verifican el render Jinja2 sin tocar el
LLM: tests del prompt, no del modelo. Deben correr en milisegundos.
"""
from __future__ import annotations

import pytest

from app.prompts.loader import render_estimation_prompt
from app.schemas import (
    DetailLevel,
    EstimationRequest,
    OutputFormat,
    ProjectType,
)


def make_request(**overrides) -> EstimationRequest:
    defaults: dict = dict(
        description=(
            "Necesitamos un buscador semántico sobre 10.000 documentos "
            "legales con filtros por jurisdicción y fecha."
        ),
        project_type=ProjectType.WEB_SAAS,
        detail_level=DetailLevel.MEDIUM,
        output_format=OutputFormat.PHASES_TABLE,
    )
    defaults.update(overrides)
    return EstimationRequest(**defaults)


def test_user_template_includes_description_verbatim():
    description = (
        "El cliente necesita un dashboard interno para visualizar métricas "
        "de adopción de su producto SaaS, con conexión a Snowflake y "
        "permisos por equipo. Plazo: 6 semanas."
    )
    _, user = render_estimation_prompt(make_request(description=description))

    assert "<project_description>" in user
    assert "</project_description>" in user
    # La descripción del usuario debe aparecer literal dentro del bloque.
    pre, _, post = user.partition("<project_description>")
    inside, _, _ = post.partition("</project_description>")
    assert description.strip() in inside


def test_phases_table_keyword_only_when_format_is_phases_table():
    system_table, _ = render_estimation_prompt(
        make_request(output_format=OutputFormat.PHASES_TABLE)
    )
    system_narr, _ = render_estimation_prompt(
        make_request(output_format=OutputFormat.NARRATIVE)
    )
    system_items, _ = render_estimation_prompt(
        make_request(output_format=OutputFormat.LINE_ITEMS)
    )

    # `phases_table` aparece como literal solo en la rama condicional del
    # formato tabla. (`confidence_pct` no sirve como sentinel porque también
    # aparece en los ejemplos few-shot del `examples.j2`.)
    assert "phases_table" in system_table
    assert "phases_table" not in system_narr
    assert "phases_table" not in system_items


def test_detailed_adds_assumptions_per_phase_only_for_detailed_level():
    system_det, _ = render_estimation_prompt(
        make_request(detail_level=DetailLevel.DETAILED)
    )
    system_sum, _ = render_estimation_prompt(
        make_request(detail_level=DetailLevel.SUMMARY)
    )
    system_med, _ = render_estimation_prompt(
        make_request(detail_level=DetailLevel.MEDIUM)
    )

    assert "Asunciones por fase" in system_det
    assert "Asunciones por fase" not in system_sum
    assert "Asunciones por fase" not in system_med


def test_examples_are_included_in_system():
    system, _ = render_estimation_prompt(make_request())
    # El bloque {% include %} debe insertar el contenido de examples.j2
    # — usamos un literal estable del fichero como sonda.
    assert "Ejemplo 1" in system
    assert "Ejemplo 2" in system


def test_render_fails_loudly_on_missing_version():
    with pytest.raises(Exception):
        render_estimation_prompt(make_request(), version="v999")
