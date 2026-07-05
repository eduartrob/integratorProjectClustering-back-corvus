"""
pipeline_corvus.py
==================
Pipeline monolítico de Corvus: PDF real → Clasificación → K-Means → Mapa t-SNE

Uso:
    python pipeline_corvus.py --pdf PropuestasPI.docx.pdf

Requiere que el ecosistema ya esté entrenado:
    - modelo_clasificacion_embeddings.pkl
    - proyectos_aprobados_filtrados.csv
"""

import argparse
import sys
import re
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import pdfplumber

from fastembed import TextEmbedding
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.manifold import TSNE

warnings.filterwarnings("ignore")

MODELO_PKL      = "modelo_clasificacion_embeddings.pkl"
ECOSISTEMA_CSV  = "proyectos_aprobados_filtrados.csv"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
PCA_DIM         = 10   # Para K-Means (preserva geometría)
K_MAX           = 9


# ── PASO 1: Extraer texto del PDF ────────────────────────────────────────────
def extraer_texto_pdf(ruta_pdf):
    print(f"\n[PASO 1] Extrayendo texto de: {ruta_pdf}")
    partes = []
    with pdfplumber.open(ruta_pdf) as pdf:
        print(f"         Páginas: {len(pdf.pages)}")
        for i, pag in enumerate(pdf.pages):
            t = pag.extract_text()
            if t:
                partes.append(t)
                print(f"         → Pág {i+1}: {len(t)} chars")
    texto = " ".join(partes)
    print(f"         Total: {len(texto)} chars")
    return texto


# ── PASO 2: Limpiar (reutiliza test_limpieza.py) ─────────────────────────────
def limpiar(texto):
    texto = str(texto).lower()
    texto = re.sub(r'\s+', ' ', texto)
    texto = re.sub(r'[^\w\s\.,áéíóúüñ]', '', texto)
    return texto.strip()


# ── FILTRO 2A: Blacklist (documentos que NUNCA son propuestas) ──────────
_BLACKLIST = [
    "currículum", "curriculum vitae", "experiencia laboral",
    "autoevaluación", "manual de usuario", "manual de mantenimiento",
    "portafolio profesional", "carta de presentación", "hoja de vida",
    "referencias personales", "referencias profesionales",
    "linkedin.com", "desarrollador fullstack",
]

def validar_blacklist(texto_crudo: str) -> str | None:
    """
    Revisa el texto crudo (sin limpiar, primeros 3000 chars) contra la blacklist.
    Retorna la palabra bloqueada si encuentra una, None si pasa limpio.
    """
    t = texto_crudo.lower()[:3000]
    for palabra in _BLACKLIST:
        if palabra in t:
            return palabra
    return None


# ── FILTRO 2B: Secciones que el profesor pide en la propuesta ───────────
# Adaptadas del formato de propuesta que los profes definieron.
# Usa el texto CRUDO (con mayusculas/acentos reales) para mayor precision.
_SECCIONES_PROFESOR = [
    {
        "nombre": "Nombre del proyecto",
        # PropuestasPI: tiene la portada con el nombre; PROPUESTA: usa "NOMBRE LARGO" / "NOMBRE CORTO" / "DESCRIPCIÓN DEL PROYECTO"
        "keywords": [
            "nombre del proyecto", "nombre de proyecto", "título del proyecto", "titulo del proyecto",
            "nombre largo", "nombre corto", "descripción del proyecto", "descripcion del proyecto",
            "información del equipo", "informacion del equipo",  # PropuestasPI tiene esta tabla
        ],
        "obligatoria": True,
    },

    {
        "nombre": "Problemática",
        # PROPUESTA: "CONTEXTO DE LA PROBLEMÁTICA" / "PROBLEMÁTICA"
        # PropuestasPI: "problemática" / "contexto"
        "keywords": [
            "problemática", "problematica", "planteamiento del problema", "planteamiento",
            "contexto de la problemática", "contexto de la problematica", "contexto",
        ],
        "obligatoria": True,
    },
    {
        "nombre": "Objetivo General / Objetivos",
        # PROPUESTA: usa "OBJETIVOS DE OPTIMIZACIÓN" (no dice "general")
        # PropuestasPI: usa "objetivo general"
        "keywords": [
            "objetivo general", "objetivos general",
            "objetivos de optimización", "objetivos de optimizacion",
            "objetivo",   # captura cualquier variante con "objetivo"
        ],
        "obligatoria": True,
    },
    {
        "nombre": "Objetivos Específicos / Variables",
        # PropuestasPI: "OBJETIVOS\nESPECÍFICOS" — partido en 2 líneas en el PDF
        # PROPUESTA: usa "VARIABLES DE DECISIÓN" / "VARIABLES A OPTIMIZAR" / "ENTRADAS AL SISTEMA"
        "keywords": [
            "objetivos específicos", "objetivos especificos", "objetivo específico",
            "específicos",   # captura la palabra suelta cuando el PDF parte la línea
            "especificos",
            "variables de decisión", "variables de decision",
            "variables a optimizar",
            "entradas al sistema", "entradas",
            "salidas esperadas", "salidas del sistema",
        ],
        "obligatoria": True,
    },
    {
        "nombre": "Justificación",
        # PROPUESTA.pdf usa "CONTEXTO DE LA PROBLEMÁTICA" como su justificación implícita
        "keywords": [
            "justificación", "justificacion",
            "contexto de la problemática", "contexto de la problematica",
        ],
        "obligatoria": True,
    },
    {
        "nombre": "Categoría",
        # Opcional: proyectos técnico-científicos no siempre tienen categoría explícita
        "keywords": ["categoría", "categoria", "información de la propuesta", "informacion de la propuesta", "área", "area"],
        "obligatoria": False,
    },
    {
        "nombre": "Usuarios Finales / Alcance",
        # PROPUESTA: no tiene "usuarios finales" pero tiene "base de conocimiento" / "salidas esperadas"
        # → opcional: no todos los proyectos son apps con usuarios
        "keywords": [
            "usuarios finales", "usuario final", "usuarios objetivo",
            "alcance", "público objetivo", "beneficiarios",
            "base de conocimiento", "base de conocimientos",
        ],
        "obligatoria": False,
    },
    {
        "nombre": "Funcionalidades / Módulos",
        # PROPUESTA: describe módulos y funciones implícitamente
        # PropuestasPI: tiene "LISTA DE FUNCIONALIDADES"
        "keywords": [
            "funcionalidades", "lista de funcionalidades", "funcionalidades por tipo",
            "requerimientos", "requisitos", "módulos", "modulos",
            "casos de uso", "características", "caracteristicas",
        ],
        "obligatoria": False,   # opcional: no todas las propuestas son apps
    },
    {
        "nombre": "Tecnologías",
        # PropuestasPI: "LISTA DE TECNOLOGÍAS A APLICAR" (aparece partido en varias líneas)
        # PROPUESTA: no menciona stack explícito
        "keywords": [
            "tecnologías", "tecnologias", "lista de tecnologías",
            "stack tecnológico", "lista de tecnologias",
            "algoritmo", "algoritmos",   # proyectos científicos usan "algoritmo" en vez de "stack"
            "herramientas",
        ],
        "obligatoria": True,
    },
    {
        "nombre": "Bibliografía",
        "keywords": [
            "bibliografía", "bibliografia", "bibliografía consultada",
            "referencias", "fuentes",
        ],
        "obligatoria": False,   # algunos proyectos iniciales aún no tienen bibliografía
    },
]

def validar_secciones(texto_crudo: str) -> dict:
    """
    Filtro 2B: Verifica que el documento tenga las secciones que los profes piden.
    Usa el texto crudo (antes de limpiar) para detectar mejor encabezados y títulos.
    Retorna: {ok, faltantes, encontradas}
    """
    t = texto_crudo.lower()
    faltantes = []
    encontradas = []

    for seccion in _SECCIONES_PROFESOR:
        if any(kw in t for kw in seccion["keywords"]):
            encontradas.append(seccion["nombre"])
        elif seccion["obligatoria"]:
            faltantes.append(seccion["nombre"])

    return {
        "ok": len(faltantes) == 0,
        "faltantes": faltantes,
        "encontradas": encontradas,
    }


# ── FILTRO 3: Coherencia semántica entre secciones ──────────────────────
# Pares clave que deben hablar del mismo tema:
#   Problemática ↔ Objetivo  (el objetivo debe resolver el problema)
#   Problema ↔ Justificación  (la justificación debe explicar por qué importa el problema)
#   Objetivo ↔ Justificación  (la justificación debe sustentar el objetivo)

_COHERENCIA_PARES = [
    ("Problema", "Objetivo"),
    ("Problema", "Justificación"),
    ("Objetivo", "Justificación"),
]

# Keywords que marcan el INICIO de cada sección de interés (para extraer su contenido)
_ANCHORS_COHERENCIA = {
    "Problema": [
        "problemática", "contexto de la problemática", "planteamiento del problema",
        "contexto de la problematica",
    ],
    "Objetivo": [
        "objetivo general", "objetivos de optimización", "objetivos de optimizacion",
    ],
    "Justificación": [
        "justificación", "justificacion",
    ],
}

# Todos los anchors de todas las secciones (para detectar el fin de una sección)
_TODOS_LOS_ANCHORS = [
    kw for kws in _ANCHORS_COHERENCIA.values() for kw in kws
] + [
    # Keywords de las demás secciones para saber cuándo termina una
    "objetivo general", "objetivos específicos", "objetivos especificos",
    "nombre del proyecto", "nombre largo", "categoría", "usuarios finales",
    "tecnologías", "tecnologias", "bibliografía", "bibliografia",
    "funcionalidades", "metodología", "metodologia",
]

COHERENCIA_UMBRAL = 0.20   # similitud coseno mínima para considerar que son coherentes
COHERENCIA_AVISO  = 0.30   # por debajo de este valor se genera una advertencia (pero no rechaza)
MIN_CHARS_SECCION = 40     # mínimo de caracteres para que valga la pena vectorizar la sección


def _coseno(v1, v2):
    """Similitud coseno entre dos vectores numpy."""
    den = np.linalg.norm(v1) * np.linalg.norm(v2)
    return float(np.dot(v1, v2) / den) if den > 0 else 0.0


def extraer_contenido_secciones(texto_crudo: str) -> dict:
    """
    Extrae el contenido de cada sección de interés buscando los anchors
    y tomando el texto hasta que aparezca el siguiente anchor conocido.
    Retorna: {"Problema": "texto...", "Objetivo": "texto...", "Justificación": "texto..."}
    """
    t = texto_crudo.lower()
    contenidos = {}

    for nombre_sec, anchors in _ANCHORS_COHERENCIA.items():
        # Encontrar la posición del primer anchor que exista en el texto
        inicio = None
        for kw in anchors:
            pos = t.find(kw)
            if pos != -1:
                inicio = pos + len(kw)
                break

        if inicio is None:
            continue   # esta sección no fue encontrada

        # Buscar el próximo anchor (de cualquier sección) para saber dónde termina
        fin = len(t)
        for otro_kw in _TODOS_LOS_ANCHORS:
            pos = t.find(otro_kw, inicio + 1)
            if pos != -1 and pos < fin:
                fin = pos

        # Extraer y limpiar el contenido entre inicio y fin
        contenido = texto_crudo[inicio:fin].strip()
        contenido = re.sub(r'\s+', ' ', contenido)

        if len(contenido) >= MIN_CHARS_SECCION:
            contenidos[nombre_sec] = contenido[:800]  # max 800 chars por sección

    return contenidos


def validar_coherencia(texto_crudo: str, emb_model) -> dict:
    """
    Filtro 3: Verifica que las secciones clave hablen del mismo tema.
    Calcula similitud coseno entre pares de secciones.
    Retorna: {ok, pares_invalidos, advertencias, detalles}
    """
    contenidos = extraer_contenido_secciones(texto_crudo)

    # Vectorizar solo las secciones que se pudieron extraer
    vectores = {}
    for nombre, texto in contenidos.items():
        vec = np.array(list(emb_model.embed([texto])))[0]
        vectores[nombre] = vec

    pares_invalidos = []
    advertencias    = []
    detalles        = []

    for (sec_a, sec_b) in _COHERENCIA_PARES:
        if sec_a not in vectores or sec_b not in vectores:
            detalles.append(f"  ⚠️  {sec_a} ↔ {sec_b}: no se pudo extraer contenido suficiente (se omite)")
            continue

        sim = _coseno(vectores[sec_a], vectores[sec_b])
        barra = int(sim * 20) * "█" + int((1 - sim) * 20) * "░"

        if sim < COHERENCIA_UMBRAL:
            detalles.append(f"  ❌ {sec_a} ↔ {sec_b}: {sim:.2f}  [{barra}]  (incoherentes)")
            pares_invalidos.append((sec_a, sec_b, sim))
        elif sim < COHERENCIA_AVISO:
            detalles.append(f"  ⚠️  {sec_a} ↔ {sec_b}: {sim:.2f}  [{barra}]  (coherencia baja)")
            advertencias.append((sec_a, sec_b, sim))
        else:
            detalles.append(f"  ✅ {sec_a} ↔ {sec_b}: {sim:.2f}  [{barra}]")

    return {
        "ok": len(pares_invalidos) == 0,
        "pares_invalidos": pares_invalidos,
        "advertencias": advertencias,
        "detalles": detalles,
        "secciones_extraidas": list(contenidos.keys()),
    }


# ── PASO 3: Clasificar con el modelo ya entrenado ────────────────────────────
def clasificar(texto_limpio, emb_model):
    print("\n[PASO 3] Clasificando con el modelo entrenado...")
    clf = joblib.load(MODELO_PKL)
    vector = np.array(list(emb_model.embed([texto_limpio])))[0]
    etiqueta = clf.predict([vector])[0]
    try:
        probas = clf.predict_proba([vector])[0]
        for clase, p in zip(clf.classes_, probas):
            print(f"         {clase:10s}: {p*100:.1f}%")
    except:
        pass
    print(f"         ✅ RESULTADO: {etiqueta.upper()}")
    return etiqueta, vector


# ── PASOS 4+5: Ecosistema + PCA + K-Means ────────────────────────────────────
def _k_optimo(vectores_pca):
    siluetas = []
    rango = range(2, min(K_MAX + 1, len(vectores_pca)))
    for k in rango:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(vectores_pca)
        siluetas.append(silhouette_score(vectores_pca, km.labels_))
    k = list(rango)[np.argmax(siluetas)]
    print(f"         K óptimo: {k}  (Silueta: {max(siluetas):.4f})")
    return k


def kmeans_pipeline(vector_nuevo, emb_model):
    print("\n[PASO 4] Cargando ecosistema...")
    df = pd.read_csv(ECOSISTEMA_CSV)
    print(f"         {len(df)} proyectos en el ecosistema")

    print("[PASO 4] Vectorizando ecosistema...")
    vecs_eco = np.array(list(emb_model.embed(df['texto_extraido'].tolist())))

    # Combinar: ecosistema + PDF nuevo al final
    todos = np.vstack([vecs_eco, vector_nuevo.reshape(1, -1)])
    idx_nuevo = len(todos) - 1

    # ── PCA 384D → 10D (para K-Means, no para visualizar) ───────────────────
    print("[PASO 5] PCA: 384D → 10D para K-Means...")
    n_comp = min(PCA_DIM, len(todos) - 1)
    pca = PCA(n_components=n_comp, random_state=42)
    pca_todos = pca.fit_transform(todos)
    var = pca.explained_variance_ratio_.sum() * 100
    print(f"         Varianza explicada: {var:.1f}% con {n_comp} componentes")

    # ── K-Means (solo entrenado sobre ecosistema) ────────────────────────────
    print("[PASO 5] Buscando K óptimo...")
    k = _k_optimo(pca_todos[:-1])

    print(f"[PASO 5] Ejecutando K-Means con {k} clústeres...")
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(pca_todos[:-1])
    labels_todos = km.predict(pca_todos)

    cluster_nuevo = labels_todos[idx_nuevo]
    centroide = km.cluster_centers_[cluster_nuevo]
    dist = np.linalg.norm(pca_todos[idx_nuevo] - centroide)
    dist_max = max(np.linalg.norm(pca_todos[i] - km.cluster_centers_[labels_todos[i]])
                   for i in range(len(pca_todos) - 1))
    pos = (dist / dist_max) * 100 if dist_max > 0 else 0

    print(f"\n         📍 Clúster asignado: {cluster_nuevo}")
    print(f"         📏 Distancia al centroide: {dist:.4f}")
    print(f"         🎯 Posición relativa: {pos:.1f}%")
    if pos < 30:
        print("         → CONVENCIONAL (cerca del núcleo)")
    elif pos < 70:
        print("         → INTERMEDIO")
    else:
        print("         → INNOVADOR (en la frontera del clúster)")

    df['cluster'] = labels_todos[:-1]
    return df, pca_todos, labels_todos, idx_nuevo, cluster_nuevo, k, dist, pos


# ── PASO 6: Visualización t-SNE 10D → 2D ─────────────────────────────────────
def visualizar(df, pca_todos, labels_todos, idx_nuevo,
               cluster_nuevo, k, etiqueta, dist, pos, nombre_pdf):
    print("\n[PASO 6] t-SNE: 10D → 2D para visualización...")
    perp = min(30, len(pca_todos) - 1)
    tsne = TSNE(n_components=2, perplexity=perp, random_state=42)
    coords = tsne.fit_transform(pca_todos)

    # Separar ecosistema del PDF nuevo
    df['x'] = coords[:-1, 0]
    df['y'] = coords[:-1, 1]
    coord_nuevo = coords[idx_nuevo]

    print("[PASO 6] Dibujando mapa...")
    fig, ax = plt.subplots(figsize=(14, 9))
    sns.set_theme(style="white")

    # Mapa de calor de densidad
    sns.kdeplot(data=df, x='x', y='y',
                fill=True, thresh=0.01, levels=10,
                cmap="Blues_r", alpha=0.45, ax=ax)

    # Puntos del ecosistema por clúster
    paleta = plt.colormaps['tab10']
    for c in range(k):
        df_c = df[df['cluster'] == c]
        ax.scatter(df_c['x'], df_c['y'],
                   color=paleta(c), s=55, alpha=0.75,
                   edgecolors='white', linewidths=0.4,
                   label=f'Clúster {c}  ({len(df_c)} proyectos)')
        # Centroide
        cx, cy = df_c['x'].mean(), df_c['y'].mean()
        ax.scatter(cx, cy, color='black', marker='X', s=260, zorder=8)
        ax.annotate(f'C{c}', (cx, cy), xytext=(6, 6),
                    textcoords='offset points',
                    fontsize=9, fontweight='bold', color='black')

    # ── Estrella roja: el PDF del alumno ─────────────────────────────────────
    ax.scatter(coord_nuevo[0], coord_nuevo[1],
               color='red', marker='*', s=1400,
               edgecolors='darkred', linewidths=1.5, zorder=15,
               label=f'Tu propuesta → Clúster {cluster_nuevo}')

    ax.annotate(
        f"  ← {nombre_pdf}\n  {etiqueta} | Clúster {cluster_nuevo}\n  Distancia: {pos:.0f}%",
        (coord_nuevo[0], coord_nuevo[1]),
        xytext=(14, 0), textcoords='offset points',
        fontsize=10, fontweight='bold', color='darkred',
        bbox=dict(boxstyle='round,pad=0.4', fc='white', ec='darkred', alpha=0.88)
    )

    ax.set_title(
        f'Mapa Semántico Corvus — "{nombre_pdf}"\n'
        f'Clasificación: {etiqueta} | Clúster {cluster_nuevo}/{k} | '
        f'Posición en clúster: {pos:.0f}%',
        fontsize=13, fontweight='bold', pad=14
    )
    ax.set_xlabel('Dimensión Semántica 1  (t-SNE, solo visual)', fontsize=10)
    ax.set_ylabel('Dimensión Semántica 2  (t-SNE, solo visual)', fontsize=10)
    ax.legend(title='Leyenda', bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=9)

    plt.tight_layout()
    salida = "mapa_pipeline_resultado.png"
    plt.savefig(salida, dpi=200, bbox_inches='tight')
    print(f"[ÉXITO] Mapa global guardado como '{salida}'")
    plt.show()

    # ── GRÁFICA 2: Zoom al clúster asignado (como mapas_individuales.png) ────
    # Filtra solo los proyectos del clúster donde cayó el PDF nuevo,
    # y agrega la estrella roja dentro de ese grupo.
    print(f"[PASO 6] Generando zoom del Clúster {cluster_nuevo}...")

    df_cluster = df[df['cluster'] == cluster_nuevo].copy()

    # Coordenadas 2D solo de ese clúster (+ el punto nuevo)
    xs_cluster = list(df_cluster['x']) + [coord_nuevo[0]]
    ys_cluster = list(df_cluster['y']) + [coord_nuevo[1]]

    fig2, ax2 = plt.subplots(figsize=(10, 8))
    sns.set_theme(style="white")

    # Mapa de calor solo del clúster
    if len(df_cluster) > 3:
        sns.kdeplot(data=df_cluster, x='x', y='y',
                    fill=True, thresh=0.01, levels=8,
                    cmap="Blues_r", alpha=0.55, ax=ax2)

    # Puntos del clúster (proyectos del ecosistema)
    ax2.scatter(df_cluster['x'], df_cluster['y'],
                color=paleta(cluster_nuevo), s=120, alpha=0.85,
                edgecolors='white', linewidths=0.6,
                label=f'{len(df_cluster)} proyectos similares')

    # Centroide del clúster
    cx, cy = df_cluster['x'].mean(), df_cluster['y'].mean()
    ax2.scatter(cx, cy, color='black', marker='X', s=400, zorder=9,
                label='Centroide del clúster')
    ax2.annotate('Centro', (cx, cy), xytext=(6, 6),
                 textcoords='offset points',
                 fontsize=10, fontweight='bold', color='black')

    # Línea del centroide al PDF nuevo (distancia visual)
    ax2.plot([cx, coord_nuevo[0]], [cy, coord_nuevo[1]],
             color='darkred', linestyle='--', linewidth=1.5, alpha=0.6, zorder=7)

    # ── Estrella roja: el PDF del alumno dentro del clúster ──────────────────
    ax2.scatter(coord_nuevo[0], coord_nuevo[1],
                color='red', marker='*', s=1800,
                edgecolors='darkred', linewidths=2, zorder=15,
                label=f'Tu propuesta ({etiqueta})')

    ax2.annotate(
        f"  ← {nombre_pdf}\n  {etiqueta}\n  Posición: {pos:.0f}% del radio",
        (coord_nuevo[0], coord_nuevo[1]),
        xytext=(14, 0), textcoords='offset points',
        fontsize=11, fontweight='bold', color='darkred',
        bbox=dict(boxstyle='round,pad=0.4', fc='white', ec='darkred', alpha=0.9)
    )

    ax2.set_title(
        f'Zoom — Clúster {cluster_nuevo}  ({len(df_cluster)} proyectos similares)\n'
        f'Tu propuesta: "{nombre_pdf}" | Posición: {pos:.0f}%',
        fontsize=13, fontweight='bold', pad=14
    )
    ax2.set_xlabel('Dimensión Semántica 1 (t-SNE, solo visual)', fontsize=10)
    ax2.set_ylabel('Dimensión Semántica 2 (t-SNE, solo visual)', fontsize=10)
    ax2.legend(fontsize=10, loc='upper left')

    plt.tight_layout()
    salida2 = f"mapa_zoom_cluster_{cluster_nuevo}.png"
    plt.savefig(salida2, dpi=200, bbox_inches='tight')
    print(f"[ÉXITO] Zoom del clúster guardado como '{salida2}'")
    plt.show()


# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", default="PropuestasPI.docx.pdf")
    args = parser.parse_args()

    print("=" * 65)
    print("  🦅  CORVUS — PIPELINE COMPLETO DE ANÁLISIS DE PROPUESTA")
    print("=" * 65)

    # 1 — Extracción
    texto_crudo = extraer_texto_pdf(args.pdf)
    if not texto_crudo.strip():
        print("[ERROR] PDF sin texto extraíble (¿PDF escaneado?)")
        sys.exit(1)

    # 2 — Limpieza
    print("\n[PASO 2] Limpiando texto...")
    texto_limpio = limpiar(texto_crudo)
    print(f"         Preview: {texto_limpio[:180]}...")

    # Cargar embeddings una sola vez (se reutiliza en pasos 3 y 4)
    print("\n[INFO] Cargando modelo de embeddings...")
    emb_model = TextEmbedding(model_name=EMBEDDING_MODEL)

    # 3 — Clasificar (Filtro 1: ML — detecta basura semántica)
    etiqueta, vector_nuevo = clasificar(texto_limpio, emb_model)
    if etiqueta == "Ruido":
        print("\n🚫 [FILTRO 1] RECHAZADO — El documento no parece una propuesta de proyecto.")
        sys.exit(0)

    # ── FILTRO 2A: Blacklist ───────────────────────────────────────
    print("\n[PASO 3.5 / FILTRO 2A] Verificando blacklist de documentos...")
    palabra_bloqueada = validar_blacklist(texto_crudo)
    if palabra_bloqueada:
        print(f"   🚫 [FILTRO 2A] RECHAZADO — Documento bloqueado.")
        print(f"         Razón: contiene la expresión prohibida '»{palabra_bloqueada}«'")
        print("         Este tipo de documento (CV, manual, carta) no es una propuesta.")
        sys.exit(0)
    print("         ✅ Blacklist: OK")

    # ── FILTRO 2B: Secciones que los profes piden ─────────────────────
    print("[PASO 3.5 / FILTRO 2B] Verificando secciones de la propuesta...")
    resultado_secciones = validar_secciones(texto_crudo)
    print(f"         Secciones encontradas ({len(resultado_secciones['encontradas'])}/{len(_SECCIONES_PROFESOR)}):")
    for s in resultado_secciones['encontradas']:
        print(f"           ✅ {s}")
    if resultado_secciones['faltantes']:
        for s in resultado_secciones['faltantes']:
            print(f"           ❌ {s} (falta)")

    if not resultado_secciones['ok']:
        print(f"\n🚫 [FILTRO 2B] RECHAZADO — La propuesta no tiene todas las secciones requeridas.")
        print("         Secciones faltantes:")
        for s in resultado_secciones['faltantes']:
            print(f"           • {s}")
        sys.exit(0)
    print("         ✅ Secciones: todas presentes")

    # ── FILTRO 3: Coherencia semántica entre secciones ───────────────────
    print("\n[PASO 3.7 / FILTRO 3] Verificando coherencia entre secciones...")
    resultado_coherencia = validar_coherencia(texto_crudo, emb_model)

    print(f"         Secciones analizadas: {', '.join(resultado_coherencia['secciones_extraidas']) or 'ninguna extraída'}")
    for linea in resultado_coherencia['detalles']:
        print(f"        {linea}")

    if resultado_coherencia['advertencias']:
        print("         ⚠️  Coherencia baja en algunos pares (no se rechaza, pero revisar)")

    if not resultado_coherencia['ok']:
        print("\n🚫 [FILTRO 3] RECHAZADO — Las secciones del documento son incoherentes entre sí.")
        print("         Los siguientes pares no hablan del mismo tema:")
        for sec_a, sec_b, sim in resultado_coherencia['pares_invalidos']:
            print(f"           • {sec_a} ↔ {sec_b} (similitud: {sim:.2f} — mínimo requerido: {COHERENCIA_UMBRAL:.2f})")
        print("         Asegúrate de que la Problemática, el Objetivo y la Justificación sean del mismo proyecto.")
        sys.exit(0)
    print("         ✅ Coherencia: todas las secciones son consistentes entre sí")

    # 4 — Ecosistema + K-Means
    df, pca_todos, labels, idx_nuevo, cluster_nuevo, k, dist, pos = \
        kmeans_pipeline(vector_nuevo, emb_model)

    # 5 — Visualizar
    nombre_pdf = args.pdf.split("/")[-1].replace(".pdf", "")
    visualizar(df, pca_todos, labels, idx_nuevo,
               cluster_nuevo, k, etiqueta, dist, pos, nombre_pdf)

    print("\n" + "=" * 65)
    print("  ANÁLISIS COMPLETADO")
    print(f"  PDF:            {nombre_pdf}")
    print(f"  Clasificación:  {etiqueta}")
    print(f"  Clúster:        {cluster_nuevo} de {k}")
    print(f"  Posición:       {pos:.0f}% del radio del clúster")
    print("=" * 65)


if __name__ == "__main__":
    main()
