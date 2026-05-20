"""
Wrapper de proveedor LLM. Mantiene el patrón de la sesión 03: una sola función
de llamada que acepta system + user ya renderizados (no concatenados) y
devuelve el texto plano + metadatos básicos.

El render del prompt vive en `app.prompts.loader`, no aquí.
"""
from __future__ import annotations

from anthropic import AsyncAnthropic

from app.config import settings


async def call_llm(system: str, user: str) -> dict:
    """Llama al LLM con dos mensajes (system + user) y devuelve el texto."""
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
        system=system,
        messages=[{"role": "user", "content": user}],
    )

    text = "".join(block.text for block in response.content if block.type == "text")
    return {
        "text": text,
        "model": response.model,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }
