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

# ── FILTRO 2B: Secciones que los profes definen ────────────────────────────
SECCIONES_PROFESOR = [
    {
        "nombre": "Nombre del proyecto",
        "keywords": [
            "nombre del proyecto", "nombre de proyecto", "título del proyecto",
            "titulo del proyecto", "nombre largo", "nombre corto",
            "descripción del proyecto", "descripcion del proyecto",
            "información del equipo", "informacion del equipo",
        ],
        "obligatoria": True,
    },
    {
        "nombre": "Problemática",
        "keywords": [
            "problemática", "problematica", "planteamiento del problema",
            "planteamiento", "contexto de la problemática",
            "contexto de la problematica", "contexto",
        ],
        "obligatoria": True,
    },
    {
        "nombre": "Objetivo General / Objetivos",
        "keywords": [
            "objetivo general", "objetivos general",
            "objetivos de optimización", "objetivos de optimizacion",
            "objetivo",
        ],
        "obligatoria": True,
    },
    {
        "nombre": "Objetivos Específicos / Variables",
        "keywords": [
            "objetivos específicos", "objetivos especificos", "objetivo específico",
            "específicos", "especificos",
            "variables de decisión", "variables de decision",
            "variables a optimizar", "entradas al sistema", "entradas",
            "salidas esperadas", "salidas del sistema",
        ],
        "obligatoria": True,
    },
    {
        "nombre": "Justificación",
        "keywords": [
            "justificación", "justificacion",
            "contexto de la problemática", "contexto de la problematica",
        ],
        "obligatoria": True,
    },
    {
        "nombre": "Tecnologías",
        "keywords": [
            "tecnologías", "tecnologias", "lista de tecnologías",
            "stack tecnológico", "lista de tecnologias",
            "algoritmo", "algoritmos", "herramientas",
        ],
        "obligatoria": True,
    },
    {
        "nombre": "Categoría",
        "keywords": ["categoría", "categoria", "información de la propuesta",
                     "informacion de la propuesta", "área", "area"],
        "obligatoria": False,
    },
    {
        "nombre": "Usuarios Finales / Alcance",
        "keywords": [
            "usuarios finales", "usuario final", "usuarios objetivo",
            "alcance", "público objetivo", "beneficiarios",
            "base de conocimiento", "base de conocimientos",
        ],
        "obligatoria": False,
    },
    {
        "nombre": "Funcionalidades / Módulos",
        "keywords": [
            "funcionalidades", "lista de funcionalidades",
            "requerimientos", "requisitos", "módulos", "modulos",
            "casos de uso", "características", "caracteristicas",
        ],
        "obligatoria": False,
    },
    {
        "nombre": "Bibliografía",
        "keywords": ["bibliografía", "bibliografia", "bibliografía consultada",
                     "referencias", "fuentes"],
        "obligatoria": False,
    },
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
