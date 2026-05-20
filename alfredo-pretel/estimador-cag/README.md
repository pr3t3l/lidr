# Estimador — Alfredo Pretel

Servicio IA en FastAPI que recibe la descripción tipada de un proyecto y
devuelve una estimación generada por un LLM. El prompt vive en **templates
Jinja2 versionados** (`app/prompts/estimation/v1/`) y se renderiza con un
loader, no como `f-string` en el endpoint. El cliente es un **formulario**
Streamlit que produce un `EstimationRequest` y lo manda por HTTP.

**Curso:** LIDR AI Engineering — pre-sesión 04
**Autor:** Alfredo Pretel

---

## Stack

- **Python 3.11** con `uv` como gestor de paquetes
- **FastAPI** + **uvicorn** (servicio IA)
- **Streamlit** (cliente con formulario tipado)
- **Anthropic SDK** — modelo `claude-haiku-4-5`
- **Jinja2** con `StrictUndefined` (templates de prompt)
- **Pydantic v2** (schemas del contrato cliente↔servicio)
- **pytest** (tests de template, sin red)

---

## Quickstart

### 1. Clonar y entrar

\`\`\`bash
git clone https://github.com/pr3t3l/lidr.git
cd lidr/alfredo-pretel/estimador-cag
\`\`\`

### 2. Configurar variables de entorno

\`\`\`bash
cp .env.example .env
# editar .env y pegar tu ANTHROPIC_API_KEY
\`\`\`

### 3. Instalar dependencias

\`\`\`bash
uv sync --all-groups   # incluye dev (pytest)
\`\`\`

### 4. Arrancar el servicio IA (terminal 1)

\`\`\`bash
uv run uvicorn app.main:app --reload
\`\`\`

Queda en \`http://localhost:8000\`. Swagger en \`/docs\`.

### 5. Arrancar el cliente Streamlit (terminal 2)

\`\`\`bash
uv run streamlit run streamlit_app.py
\`\`\`

Abre \`http://localhost:8501\`. Rellena el formulario (descripción +
tipo de proyecto + nivel de detalle + formato de salida) y pulsa
**Estimar**. El cliente hace `POST /api/v1/estimations/estimate` con un
JSON tipado contra el servicio IA y muestra la respuesta.

Si el backend vive en otro host, exporta `ESTIMATOR_API_URL` antes de
lanzar Streamlit:

\`\`\`bash
ESTIMATOR_API_URL=http://backend.local:8000 uv run streamlit run streamlit_app.py
\`\`\`

### 6. Tests

\`\`\`bash
uv run pytest -v
\`\`\`

Los tests verifican el render del template (sin tocar el LLM): que la
descripción aparece dentro de `<project_description>`, que los bloques
condicionales del `output_format` y del `detail_level` se activan solo
cuando corresponde y que los ejemplos few-shot se incluyen.

---

## Endpoints

| Método | URL | Descripción |
|---|---|---|
| GET | \`/health\` | Healthcheck — devuelve estado del servicio |
| GET | \`/healthz\` | Alias de \`/health\` (convención Kubernetes) |
| POST | \`/api/v1/estimations/estimate?prompt_version=v1\` | Genera una estimación tipada |
| GET | \`/docs\` | Documentación Swagger interactiva |

### Ejemplo de request

\`\`\`bash
curl -X POST 'http://localhost:8000/api/v1/estimations/estimate' \\
  -H 'Content-Type: application/json' \\
  -d '{
    "description": "Necesitamos un buscador semántico sobre 10.000 documentos legales con filtros por jurisdicción y fecha.",
    "project_type": "web_saas",
    "detail_level": "medium",
    "output_format": "phases_table"
  }'
\`\`\`

### Respuesta

\`\`\`json
{
  "text": "| phase | tasks | hours | confidence_pct |\n...",
  "prompt_version": "v1"
}
\`\`\`

---

## Arquitectura

\`\`\`
app/
├── main.py                       # FastAPI app + healthcheck
├── config.py                     # Pydantic Settings (.env)
├── schemas.py                    # EstimationRequest/Response + enums
├── routers/
│   └── estimations.py            # POST /estimate (acepta ?prompt_version)
├── services/
│   └── llm_service.py            # call_llm(system, user) → dict
└── prompts/
    ├── loader.py                 # render_estimation_prompt(req, version)
    └── estimation/
        └── v1/
            ├── system.j2         # instrucciones + ramas condicionales + include
            ├── user.j2           # wrapper de la descripción del usuario
            └── examples.j2       # few-shot
tests/
└── prompts/
    └── test_estimation_v1.py     # tests del render (no del modelo)
streamlit_app.py                  # Formulario → POST /estimate
\`\`\`

### Flujo de una petición

1. El usuario rellena el formulario en Streamlit y pulsa **Estimar**.
2. Streamlit serializa un `EstimationRequest` y hace `POST` al servicio IA.
3. FastAPI valida el JSON contra `EstimationRequest`.
4. `render_estimation_prompt(request, version)` produce `(system, user)`.
5. `call_llm(system, user)` envía ambos como mensajes separados (roles distintos).
6. El servicio devuelve `EstimationResponse { text, prompt_version }`.

### Por qué prompts en `.j2` y no en el código

Un `f-string` dentro del endpoint mezcla lógica de orquestación con
contenido editable; no se puede versionar el prompt sin rebuild ni
revisar diffs de prompt como diffs de prompt. Sacarlo a `.j2` permite:

- **Versionar el prompt** en su carpeta (`v1/`, `v2/`…) y cambiar de
  versión sin tocar Python, vía query param o config.
- **Probarlo en aislamiento** (`tests/prompts/`) en milisegundos, sin
  red.
- **Revisarlo en PR** como un documento, no como un string escapado.

`StrictUndefined` evita prompts mutilados silenciosamente cuando falta
una variable en el contexto.

---

## Verificación (ejercicio pre-sesión 04)

- [x] Schemas Pydantic con enums (`ProjectType`, `DetailLevel`, `OutputFormat`).
- [x] Cliente Streamlit con formulario (`st.form` + `st.form_submit_button`)
      que produce un `EstimationRequest` y hace `POST /estimate`.
- [x] Templates Jinja2 en `app/prompts/estimation/v1/` con ramas
      condicionales para `output_format` y `detail_level` e `{% include %}`
      de `examples.j2`.
- [x] Loader con `Environment(StrictUndefined, trim_blocks, lstrip_blocks)`
      y firma `render_estimation_prompt(request, version="v1")`.
- [x] Endpoint refactorizado para enviar `system` y `user` como mensajes
      separados al LLM.
- [x] ≥3 tests del template que corren sin tocar APIs externas
      (`uv run pytest`).

---

## Costo aproximado por llamada

Con \`claude-haiku-4-5\`: ~1500 tokens input + ~800 tokens output ≈
**\$0.005 por estimación**.
