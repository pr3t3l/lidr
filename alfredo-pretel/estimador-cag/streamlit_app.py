"""
Cliente Streamlit del Estimador.

Diferencia respecto a la sesión 03: ya no es un chat. Es un formulario que
produce un EstimationRequest tipado y lo envía por HTTP al servicio IA
(POST /api/v1/estimations/estimate). La respuesta se muestra debajo.

Arrancar (en dos terminales):

    # 1. Servicio IA (FastAPI)
    uv run uvicorn app.main:app --reload

    # 2. Cliente (Streamlit)
    uv run streamlit run streamlit_app.py
"""
from __future__ import annotations

import os
import time

import httpx
import streamlit as st

from app.schemas import (
    DetailLevel,
    EstimationRequest,
    OutputFormat,
    ProjectType,
)

DEFAULT_API_URL = "http://localhost:8000"
API_URL = os.getenv("ESTIMATOR_API_URL", DEFAULT_API_URL).rstrip("/")
ENDPOINT = f"{API_URL}/api/v1/estimations/estimate"

st.set_page_config(
    page_title="Estimador — Formulario",
    page_icon="🧮",
    layout="wide",
)

# --------------------------------- Sidebar -----------------------------------
with st.sidebar:
    st.header("🔌 Servicio IA")
    st.caption(f"Endpoint: `{ENDPOINT}`")
    st.caption(
        "Cambia el host con la variable de entorno `ESTIMATOR_API_URL` "
        "si el backend no corre en localhost:8000."
    )

    st.divider()
    st.subheader("📊 Última llamada")
    metrics = st.session_state.get("last_metrics")
    if metrics:
        st.metric("Latencia", f"{metrics['elapsed_s']} s")
        st.caption(f"Prompt version: `{metrics['prompt_version']}`")
        st.caption(f"HTTP status: `{metrics['status']}`")
    else:
        st.caption("Aún no se ha realizado ninguna llamada.")


# ---------------------------------- Form -------------------------------------
st.title("🧮 Estimador de proyectos")
st.caption(
    "Rellena el formulario y envíalo. El cliente serializa los datos como "
    "`EstimationRequest` y los manda al servicio IA por HTTP."
)

with st.form("estimation_form", clear_on_submit=False):
    description = st.text_area(
        "Descripción del proyecto",
        placeholder=(
            "Describe alcance, integraciones, plazos deseados y cualquier "
            "restricción técnica o de negocio relevante (20–2000 caracteres)."
        ),
        height=220,
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        project_type = st.selectbox(
            "Tipo de proyecto",
            options=[pt.value for pt in ProjectType],
            format_func=lambda v: v.replace("_", " ").title(),
        )
    with c2:
        detail_level = st.selectbox(
            "Nivel de detalle",
            options=[dl.value for dl in DetailLevel],
            index=1,  # medium
            format_func=str.title,
        )
    with c3:
        output_format = st.selectbox(
            "Formato de salida",
            options=[of.value for of in OutputFormat],
            format_func=lambda v: v.replace("_", " ").title(),
        )
    submitted = st.form_submit_button("Estimar", type="primary")

if submitted:
    try:
        request = EstimationRequest(
            description=description,
            project_type=ProjectType(project_type),
            detail_level=DetailLevel(detail_level),
            output_format=OutputFormat(output_format),
        )
    except Exception as exc:  # ValidationError de Pydantic
        st.error(f"❌ Datos del formulario inválidos: {exc}")
        st.stop()

    payload = request.model_dump(mode="json")
    started = time.perf_counter()
    try:
        response = httpx.post(ENDPOINT, json=payload, timeout=120)
    except httpx.RequestError as exc:
        st.error(
            f"❌ No se pudo contactar con el servicio IA en `{ENDPOINT}`.\n\n"
            f"¿Tienes el backend levantado? Arráncalo con "
            "`uv run uvicorn app.main:app --reload`.\n\nDetalle: {exc}"
        )
        st.stop()

    elapsed = round(time.perf_counter() - started, 2)
    if response.status_code != 200:
        st.error(
            f"❌ El servicio IA respondió {response.status_code}: "
            f"`{response.text}`"
        )
        st.stop()

    data = response.json()
    st.session_state["last_metrics"] = {
        "elapsed_s": elapsed,
        "prompt_version": data.get("prompt_version", "?"),
        "status": response.status_code,
    }
    st.session_state["last_response"] = data
    st.session_state["last_request"] = payload


last_response = st.session_state.get("last_response")
if last_response:
    st.divider()
    st.subheader("📝 Estimación")
    st.markdown(last_response["text"])
    with st.expander("Detalles de la petición", expanded=False):
        st.json(st.session_state.get("last_request", {}))
        st.caption(
            f"Respondida con prompt_version=`{last_response.get('prompt_version')}`"
        )
