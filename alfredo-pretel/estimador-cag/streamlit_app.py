"""
Wrapper conversacional con Streamlit para el Estimador CAG.

Reutiliza el mismo system prompt y contexto few-shot que el endpoint FastAPI
(`app/services/llm_service.py`), pero con UI de chat y streaming token a token.

Ejecutar:
    uv run streamlit run streamlit_app.py
"""
from __future__ import annotations

import time
from typing import Iterator

import streamlit as st
from anthropic import Anthropic

from app.config import settings
from app.context.examples import ESTIMATION_EXAMPLES
from app.services.llm_service import build_system_prompt

SYSTEM_PROMPT = build_system_prompt()

st.set_page_config(
    page_title="Estimador CAG — Chat",
    page_icon="💬",
    layout="wide",
)


def get_api_key() -> str:
    """API key desde st.secrets (prioritario) o desde .env vía pydantic-settings."""
    try:
        key = st.secrets.get("ANTHROPIC_API_KEY")  # type: ignore[attr-defined]
        if key:
            return key
    except (FileNotFoundError, st.errors.StreamlitAPIException):
        pass
    return settings.anthropic_api_key


def history_for_api() -> list[dict]:
    """Convierte el historial de session_state en mensajes para la API."""
    return [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state["messages"]
    ]


def stream_estimation(messages: list[dict]) -> Iterator[str]:
    """Llama a Anthropic en streaming y va emitiendo deltas de texto."""
    api_key = get_api_key()
    if not api_key:
        yield (
            "❌ No hay `ANTHROPIC_API_KEY` configurada. "
            "Añádela en `.env` o en `.streamlit/secrets.toml`."
        )
        return

    client = Anthropic(api_key=api_key)
    started = time.perf_counter()

    with client.messages.stream(
        model=settings.anthropic_model,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            yield text
        final = stream.get_final_message()

    st.session_state["last_metrics"] = {
        "model": final.model,
        "input_tokens": final.usage.input_tokens,
        "output_tokens": final.usage.output_tokens,
        "elapsed_s": round(time.perf_counter() - started, 2),
    }


# ----------------------------- Sidebar (Nivel 3) -----------------------------
with st.sidebar:
    st.header("🧠 Contexto CAG")
    st.caption(f"Proveedor: `{settings.llm_provider}` · Modelo: `{settings.anthropic_model}`")

    with st.expander("System prompt activo", expanded=False):
        st.text_area(
            "system_prompt",
            value=SYSTEM_PROMPT,
            height=320,
            disabled=True,
            label_visibility="collapsed",
        )

    with st.expander(
        f"Ejemplos inyectados ({len(ESTIMATION_EXAMPLES)})", expanded=False
    ):
        for i, ex in enumerate(ESTIMATION_EXAMPLES, start=1):
            st.markdown(f"**Ejemplo {i} — resumen de reunión**")
            st.markdown(f"> {ex['meeting_summary']}")
            st.markdown("**Estimación de referencia:**")
            st.markdown(ex["estimation"])
            if i < len(ESTIMATION_EXAMPLES):
                st.divider()

    st.divider()
    st.subheader("📊 Última llamada")
    metrics = st.session_state.get("last_metrics")
    if metrics:
        c1, c2 = st.columns(2)
        c1.metric("Input tokens", metrics["input_tokens"])
        c2.metric("Output tokens", metrics["output_tokens"])
        st.metric("Latencia", f"{metrics['elapsed_s']} s")
        st.caption(f"Modelo devuelto: `{metrics['model']}`")
    else:
        st.caption("Aún no se ha realizado ninguna llamada.")

    st.divider()
    if st.button("🧹 Limpiar conversación", use_container_width=True):
        st.session_state["messages"] = []
        st.session_state.pop("last_metrics", None)
        st.rerun()


# -------------------------------- Chat ---------------------------------------
st.title("💬 Estimador CAG")
st.caption(
    "Pega una transcripción de reunión y obtén una estimación de software. "
    "Arquitectura CAG: los ejemplos históricos se inyectan en el system prompt."
)

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Pega aquí la transcripción de la reunión…")
if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response_text = st.write_stream(stream_estimation(history_for_api()))

    st.session_state["messages"].append(
        {"role": "assistant", "content": response_text}
    )
