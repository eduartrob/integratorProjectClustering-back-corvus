# ── FILTRO 1: Etiquetas del clasificador ML ────────────────────────────────
ETIQUETA_VALIDAS = {"Excelente", "Regular"}   # Ruido → rechazado

# ── FILTRO 2A: Blacklist de documentos que nunca son propuestas ────────────
BLACKLIST_DOCS = [
    "currículum", "curriculum vitae", "experiencia laboral",
    "autoevaluación", "manual de usuario", "manual de mantenimiento",
    "portafolio profesional", "carta de presentación", "hoja de vida",
    "referencias personales", "referencias profesionales",
    "linkedin.com", "desarrollador fullstack",
]

# ── FILTRO 2B: Secciones por defecto cuando no hay configuración de materia ────
SECCIONES_PROFESOR = [
    {"nombre": "Nombre del proyecto", "obligatoria": True},
    {"nombre": "Problemática", "obligatoria": True},
    {"nombre": "Objetivo General", "obligatoria": True},
    {"nombre": "Objetivos Específicos", "obligatoria": True},
    {"nombre": "Justificación", "obligatoria": True},
    {"nombre": "Tecnologías / Metodología", "obligatoria": True},
    {"nombre": "Categoría", "obligatoria": False},
    {"nombre": "Usuarios Finales / Alcance", "obligatoria": False},
    {"nombre": "Funcionalidades / Módulos", "obligatoria": False},
    {"nombre": "Bibliografía", "obligatoria": False},
]

# ── FILTRO 3: Anchors para extraer contenido por sección ──────────────────
ANCHORS_COHERENCIA = {
    "Problema": [
        "problemática", "contexto de la problemática",
        "planteamiento del problema", "contexto de la problematica",
    ],
    "Objetivo": [
        "objetivo general", "objetivos de optimización",
        "objetivos de optimizacion",
    ],
    "Justificación": ["justificación", "justificacion"],
}

TODOS_LOS_ANCHORS = [
    kw for kws in ANCHORS_COHERENCIA.values() for kw in kws
] + [
    "objetivo general", "objetivos específicos", "objetivos especificos",
    "nombre del proyecto", "nombre largo", "categoría", "usuarios finales",
    "tecnologías", "tecnologias", "bibliografía", "bibliografia",
    "funcionalidades", "metodología", "metodologia",
]

COHERENCIA_UMBRAL = 0.20
MIN_CHARS_SECCION = 40
