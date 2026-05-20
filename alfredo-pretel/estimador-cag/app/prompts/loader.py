"""
Loader de templates Jinja2 para los prompts del estimador.

Cada versión vive bajo `estimation/<version>/` y debe contener al menos
`system.j2` y `user.j2`. El loader expone `render_estimation_prompt`, que
devuelve la pareja (system, user) lista para enviar al LLM como dos mensajes
separados con roles distintos.

Razones de los flags:
- `StrictUndefined`: cualquier variable no pasada en el contexto rompe el
  render. Evita prompts mutilados que pasan desapercibidos.
- `trim_blocks` + `lstrip_blocks`: deja el output sin líneas en blanco
  espurias derivadas de los bloques `{% %}`.
"""
from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from app.schemas import EstimationRequest

PROMPTS_ROOT = Path(__file__).parent

_env = Environment(
    loader=FileSystemLoader(PROMPTS_ROOT),
    undefined=StrictUndefined,
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True,
)


def render_estimation_prompt(
    request: EstimationRequest,
    version: str = "v1",
) -> tuple[str, str]:
    """Renderiza los templates de `version` y devuelve (system, user)."""
    context = {
        "description": request.description,
        "project_type": request.project_type.value,
        "detail_level": request.detail_level.value,
        "output_format": request.output_format.value,
    }
    system = _env.get_template(f"estimation/{version}/system.j2").render(**context)
    user = _env.get_template(f"estimation/{version}/user.j2").render(**context)
    return system, user
