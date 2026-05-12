"""
Servicio LLM con arquitectura CAG: inyecta ejemplos estáticos en el system prompt.
"""
from anthropic import AsyncAnthropic

from app.config import settings
from app.context.examples import ESTIMATION_EXAMPLES


def _build_system_prompt() -> str:
    """Construye el system prompt con los ejemplos few-shot inyectados."""
    examples_block = "\n\n---\n\n".join(
        f"### Ejemplo {i + 1}\n"
        f"**Resumen de reunión:**\n{ex['meeting_summary']}\n\n"
        f"**Estimación generada:**\n{ex['estimation']}"
        for i, ex in enumerate(ESTIMATION_EXAMPLES)
    )

    return f"""Eres un estimador senior de proyectos de software. Tu trabajo es analizar \
transcripciones de reuniones con clientes y generar estimaciones detalladas en horas, \
con desglose de tareas, equipo recomendado, duración, stack tecnológico sugerido y riesgos.

Sigue el formato y nivel de detalle de los siguientes ejemplos históricos. Sé conservador \
en las estimaciones (incluye buffer para imprevistos), explicita supuestos cuando la \
transcripción sea ambigua, y señala riesgos que el cliente debería conocer.

# Ejemplos de estimaciones previas

{examples_block}

# Instrucciones finales
- Devuelve la estimación en Markdown siguiendo la estructura de los ejemplos.
- Si falta información crítica en la transcripción, lístala al final como "Supuestos" o "Preguntas para el cliente".
- No inventes requisitos que no estén en la transcripción.
"""


async def generate_estimation(transcription: str) -> dict:
    """
    Genera una estimación a partir de una transcripción de reunión.

    Returns:
        dict con campos: estimation, model, provider, input_tokens, output_tokens
    """
    if settings.llm_provider != "anthropic":
        raise NotImplementedError(
            f"Provider '{settings.llm_provider}' no implementado. "
            "Solo 'anthropic' está soportado en esta versión."
        )

    if not settings.anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY no configurada en .env")

    client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    response = await client.messages.create(
        model=settings.anthropic_model,
        max_tokens=2048,
        system=_build_system_prompt(),
        messages=[
            {
                "role": "user",
                "content": (
                    f"Genera una estimación para el siguiente proyecto basándote en "
                    f"esta transcripción de reunión:\n\n{transcription}"
                ),
            }
        ],
    )

    estimation_text = "".join(
        block.text for block in response.content if block.type == "text"
    )

    return {
        "estimation": estimation_text,
        "model": response.model,
        "provider": "anthropic",
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }