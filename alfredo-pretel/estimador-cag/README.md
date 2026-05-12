# Estimador CAG — Alfredo Pretel

API FastAPI que recibe transcripciones de reuniones y devuelve estimaciones de software generadas por un LLM, usando arquitectura **CAG** (Context-Augmented Generation): el contexto estático (ejemplos de estimaciones previas) se inyecta directamente en el prompt.

**Curso:** LIDR AI Engineering — Sesión Proyecto 1
**Autor:** Alfredo Pretel

---

## Stack

- **Python 3.11** con `uv` como gestor de paquetes
- **FastAPI** + **uvicorn** (servidor ASGI)
- **Anthropic SDK** — modelo `claude-haiku-4-5`
- **Pydantic Settings** para configuración

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
uv sync
\`\`\`

### 4. Arrancar el servidor

\`\`\`bash
uv run uvicorn app.main:app --reload
\`\`\`

El servidor queda en \`http://localhost:8000\`.

---

## Endpoints

| Método | URL | Descripción |
|---|---|---|
| GET | \`/health\` | Healthcheck — devuelve estado del servicio |
| GET | \`/healthz\` | Alias de \`/health\` (convención Kubernetes) |
| POST | \`/api/v1/estimations/estimate\` | Genera una estimación a partir de una transcripción |
| GET | \`/docs\` | Documentación Swagger interactiva |

### Ejemplo de uso

\`\`\`bash
curl -X POST http://localhost:8000/api/v1/estimations/estimate \\
  -H "Content-Type: application/json" \\
  -d '{
    "transcription": "El cliente necesita una landing page con formulario de captura de leads, integración con HubSpot CRM, y blog con WYSIWYG. Plazo: 4 semanas. Diseño en Figma."
  }'
\`\`\`

Respuesta:

\`\`\`json
{
  "estimation": "## Estimación: Landing + Blog...",
  "model": "claude-haiku-4-5-...",
  "provider": "anthropic",
  "input_tokens": 1234,
  "output_tokens": 567
}
\`\`\`

---

## Arquitectura

\`\`\`
app/
├── main.py                  # App FastAPI + healthcheck + montaje de routers
├── config.py                # Pydantic Settings (lee .env)
├── routers/
│   └── estimations.py       # Endpoint /estimate + schemas Pydantic
├── services/
│   └── llm_service.py       # Llamada a Anthropic + construcción del prompt
└── context/
    └── examples.py          # Few-shot examples (datos estáticos inyectados)
\`\`\`

### Flujo de una petición

1. \`POST /api/v1/estimations/estimate\` llega a \`main.py\`
2. Se enruta al \`APIRouter\` de \`estimations.py\`
3. Pydantic valida el JSON contra \`EstimationRequest\`
4. \`llm_service.generate_estimation()\` construye el system prompt inyectando los \`ESTIMATION_EXAMPLES\` (esto es **CAG**)
5. Se llama a Anthropic con el modelo configurado en \`.env\`
6. La respuesta se valida contra \`EstimationResponse\` y se devuelve como JSON

### Por qué CAG y no RAG

Con solo 2 ejemplos en \`context/examples.py\`, todo cabe en el system prompt. No se necesita base de datos vectorial ni retrieval. Cuando el corpus de ejemplos crezca a decenas/cientos, evolucionará a RAG en módulos posteriores del curso.

---

## Verificación

Checklist del ejercicio:

- [x] Arranca con \`uv run uvicorn app.main:app --reload\` sin errores
- [x] API keys cargadas desde \`.env\` (nunca en código)
- [x] \`GET /health\` responde 200
- [x] \`POST /api/v1/estimations/estimate\` recibe transcripción y devuelve estimación
- [x] La estimación se inspira en los ejemplos del contexto inyectado
- [x] Swagger accesible en \`/docs\`
- [x] \`.env\` está en \`.gitignore\`

---

## Costo aproximado por llamada

Con \`claude-haiku-4-5\`: ~1500 tokens input + ~800 tokens output ≈ **\$0.005 por estimación**.
