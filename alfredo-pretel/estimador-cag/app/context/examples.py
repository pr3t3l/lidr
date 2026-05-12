"""
Few-shot examples inyectados en el system prompt (arquitectura CAG).
Cada ejemplo es una referencia histórica que el modelo usará como ancla
para estimar nuevos proyectos.
"""

ESTIMATION_EXAMPLES = [
    {
        "meeting_summary": (
            "El cliente necesita una plataforma web de gestión de inventario "
            "para una cadena de 5 tiendas. Requiere CRUD de productos, control "
            "de stock por tienda, alertas de bajo stock, autenticación con roles "
            "(admin, gerente, vendedor) y dashboard con métricas de ventas. "
            "Stack abierto. Plazo deseado: 2 meses."
        ),
        "estimation": """## Estimación: Plataforma de Gestión de Inventario Multi-Tienda

### Desglose de tareas
1. **Diseño UI/UX** (wireframes + alta fidelidad): 40h
2. **Backend API** (CRUD productos, stock, tiendas): 60h
3. **Autenticación y RBAC** (3 roles): 20h
4. **Sistema de alertas de stock**: 15h
5. **Dashboard con métricas y gráficas**: 30h
6. **Testing (unit + integration)**: 25h
7. **Deploy y CI/CD básico**: 10h

**Total estimado: 200 horas**
**Equipo recomendado: 2 desarrolladores full-stack + 1 diseñador UX part-time**
**Duración: 7-8 semanas**
**Stack sugerido: FastAPI + PostgreSQL + Next.js + Vercel/Railway**
**Riesgos: integración con sistemas POS existentes (no especificado en reunión, validar)**
""",
    },
    {
        "meeting_summary": (
            "Startup necesita landing page con formulario de captura de leads, "
            "integración con HubSpot CRM, sección de blog gestionable por marketing "
            "(WYSIWYG), y SEO técnico. Diseño ya existe en Figma. Plazo: 4 semanas."
        ),
        "estimation": """## Estimación: Landing + Blog con Integración HubSpot

### Desglose de tareas
1. **Implementación Figma → código** (responsive): 25h
2. **Formulario de contacto + validación**: 8h
3. **Integración HubSpot (API o Forms)**: 12h
4. **CMS para blog (Sanity/Strapi)**: 20h
5. **Editor WYSIWYG configurado**: 6h
6. **SEO técnico (sitemap, schema, OG, performance)**: 15h
7. **Testing cross-browser + QA**: 10h
8. **Deploy + analytics (GA4)**: 6h

**Total estimado: 102 horas**
**Equipo recomendado: 1 desarrollador frontend + 1 backend part-time**
**Duración: 3-4 semanas**
**Stack sugerido: Next.js + Sanity CMS + Vercel**
**Riesgos: latencia de aprobación de diseño si surgen ajustes; permisos OAuth en HubSpot**
""",
    },
]