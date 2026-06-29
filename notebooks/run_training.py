"""
Script de entrenamiento del modelo HDBSCAN + UMAP para Corvus.
Equivale a ejecutar el notebook entrenamiento_hdbscan.ipynb completo.
Genera las gráficas PNG y los artefactos .joblib.

Uso:
    cd notebooks/
    python run_training.py
"""

import os
import sys
import warnings
warnings.filterwarnings('ignore')

from pathlib import Path
from collections import Counter

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Backend sin pantalla para servidores
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import joblib

from sentence_transformers import SentenceTransformer
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.preprocessing import normalize
import umap
import hdbscan

# ────────────────────────────────────────────────────────────────
RANDOM_SEED  = 42
# Con 50 muestras: n_neighbors << 50, n_components << n_neighbors
N_NEIGHBORS  = 5    # seguro para corpus de 50 docs
N_COMPONENTS = 15   # reducción a 15D para HDBSCAN (mucho < n_neighbors no es requerido, pero sí razonable)
MODELS_DIR   = Path(__file__).resolve().parent.parent / "app" / "models"
FIGURES_DIR  = Path(__file__).resolve().parent / "figures"
CORPUS_PATH  = Path("/home/eduartrob/Documentos/project9no/pruebas/corvus-backend-local/projectsTests")

np.random.seed(RANDOM_SEED)
MODELS_DIR.mkdir(exist_ok=True)
FIGURES_DIR.mkdir(exist_ok=True)

# ────────────────────────────────────────────────────────────────
print("=" * 60)
print("  🦅 CORVUS — Entrenamiento HDBSCAN + UMAP")
print("=" * 60)

# ── 1. CARGA DEL CORPUS ─────────────────────────────────────────
print("\n📂 Cargando corpus...")
docs, labels_raw = [], []

for fp in sorted(CORPUS_PATH.glob("*.md")):
    category = fp.stem.split("_")[0]
    docs.append(fp.read_text(encoding="utf-8"))
    labels_raw.append(category)

print(f"   Proyectos cargados : {len(docs)}")
print(f"   Categorías únicas  : {sorted(set(labels_raw))}")

# ── 2. EDA — DISTRIBUCIÓN ───────────────────────────────────────
print("\n📊 Generando gráfica de distribución...")
category_counts = Counter(labels_raw)
categories      = list(category_counts.keys())
counts          = list(category_counts.values())
palette         = sns.color_palette("husl", len(categories))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
bars = ax1.barh(categories, counts, color=palette)
ax1.set_xlabel("Número de proyectos")
ax1.set_title("Distribución por Dominio Temático", fontweight="bold")
ax1.bar_label(bars, padding=3)
ax1.set_xlim(0, max(counts) + 2)
ax2.pie(counts, labels=categories, autopct="%1.0f%%", colors=palette, startangle=90)
ax2.set_title("Proporción del Corpus", fontweight="bold")
plt.suptitle(f"Corpus Corvus — {len(docs)} Propuestas de Proyectos Integradores", fontsize=13)
plt.tight_layout()
out_dist = FIGURES_DIR / "corpus_distribucion.png"
plt.savefig(out_dist, dpi=120, bbox_inches="tight")
plt.close()
print(f"   ✅ Guardada: {out_dist}")

# ── 3. VECTORIZACIÓN ─────────────────────────────────────────────
print("\n⏳ Cargando SentenceTransformer...")
encoder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
print("⏳ Vectorizando corpus (puede tardar ~30s)...")
embeddings_raw = encoder.encode(docs, convert_to_numpy=True, show_progress_bar=True)
embeddings     = normalize(embeddings_raw, norm="l2")
print(f"   ✅ Embeddings: {embeddings.shape}  (proyectos × dimensiones)")

# ── 4. UMAP (reducción dimensional) ──────────────────────────────
print(f"\n⏳ Entrenando UMAP {N_COMPONENTS}D (n_neighbors={N_NEIGHBORS})...")
reducer_nd = umap.UMAP(
    n_components = N_COMPONENTS,
    n_neighbors  = N_NEIGHBORS,
    min_dist     = 0.0,
    metric       = "cosine",
    random_state = RANDOM_SEED,
)
embeddings_nd = reducer_nd.fit_transform(embeddings)
print(f"   ✅ UMAP {N_COMPONENTS}D: {embeddings_nd.shape}")

umap_path = MODELS_DIR / "umap_50d_model.joblib"
joblib.dump(reducer_nd, umap_path)
print(f"   💾 Artefacto: {umap_path}  ({umap_path.stat().st_size/1024:.1f} KB)")

# ── 5. HDBSCAN ───────────────────────────────────────────────────
print("\n⏳ Entrenando HDBSCAN...")
clusterer = hdbscan.HDBSCAN(
    min_cluster_size       = 3,
    min_samples            = 2,
    metric                 = "euclidean",
    cluster_selection_method = "eom",
    prediction_data        = True,
)
cluster_labels = clusterer.fit_predict(embeddings_nd)

n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
n_noise    = list(cluster_labels).count(-1)

print(f"\n   📊 Resultados:")
print(f"      Clústeres detectados    : {n_clusters}")
print(f"      Puntos ruido (Océano Azul): {n_noise}")
print(f"      Proyectos en clústeres  : {len(cluster_labels) - n_noise}")

hdbscan_path = MODELS_DIR / "hdbscan_model.joblib"
joblib.dump(clusterer, hdbscan_path)
print(f"   💾 Artefacto: {hdbscan_path}  ({hdbscan_path.stat().st_size/1024:.1f} KB)")

# ── 6. MÉTRICAS ──────────────────────────────────────────────────
print("\n📐 Calculando métricas de calidad del clustering...")
mask = cluster_labels != -1
if mask.sum() >= 2 and len(set(cluster_labels[mask])) >= 2:
    sil = silhouette_score(embeddings_nd[mask], cluster_labels[mask])
    dbi = davies_bouldin_score(embeddings_nd[mask], cluster_labels[mask])
    print(f"   Silhouette Score : {sil:.4f}  (>0.3 = aceptable, >0.5 = bueno)")
    print(f"   Davies-Bouldin   : {dbi:.4f}  (<1.0 = bueno)")
else:
    print("   ⚠️ No hay suficientes clústeres para métricas globales")

print("\n   Distribución de clústeres:")
for lbl in sorted(set(cluster_labels)):
    count = list(cluster_labels).count(lbl)
    name  = "RUIDO / Océano Azul" if lbl == -1 else f"Clúster {lbl:2d}"
    print(f"      {name}: {'█' * count} ({count})")

# ── 7. VISUALIZACIÓN 2D ──────────────────────────────────────────
print("\n⏳ Generando mapa semántico 2D...")
reducer_2d = umap.UMAP(
    n_components = 2,
    n_neighbors  = N_NEIGHBORS,
    min_dist     = 0.1,
    metric       = "cosine",
    random_state = RANDOM_SEED,
)
embeddings_2d = reducer_2d.fit_transform(embeddings)

fig, axes = plt.subplots(1, 2, figsize=(18, 7))

# Plot 1: Coloreado por clúster HDBSCAN
unique_labels = sorted(set(cluster_labels))
cmap = plt.colormaps["tab10"].resampled(max(len(unique_labels), 2))

for i, lbl in enumerate(unique_labels):
    m      = cluster_labels == lbl
    color  = "#888888" if lbl == -1 else cmap(i)
    marker = "x"       if lbl == -1 else "o"
    lname  = f"Ruido/Océano Azul ({m.sum()})" if lbl == -1 else f"Clúster {lbl} ({m.sum()})"
    axes[0].scatter(embeddings_2d[m, 0], embeddings_2d[m, 1],
                    c=[color], marker=marker, s=100, alpha=0.85, label=lname, linewidths=1.5)

axes[0].set_title("Mapa Semántico — Clústeres HDBSCAN", fontweight="bold", fontsize=13)
axes[0].legend(loc="best", fontsize=8)
axes[0].set_xlabel("UMAP Dim 1")
axes[0].set_ylabel("UMAP Dim 2")

# Plot 2: Coloreado por dominio real
unique_cats = sorted(set(labels_raw))
cmap2       = plt.colormaps["tab10"].resampled(len(unique_cats))
cat2color   = {c: cmap2(i) for i, c in enumerate(unique_cats)}
colors_cat  = [cat2color[c] for c in labels_raw]

axes[1].scatter(embeddings_2d[:, 0], embeddings_2d[:, 1], c=colors_cat, s=100, alpha=0.85)
patches = [mpatches.Patch(color=cat2color[c], label=c) for c in unique_cats]
axes[1].legend(handles=patches, loc="best", fontsize=8)
axes[1].set_title("Mapa Semántico — Dominios Reales", fontweight="bold", fontsize=13)
axes[1].set_xlabel("UMAP Dim 1")
axes[1].set_ylabel("UMAP Dim 2")

plt.suptitle("Visualización UMAP 2D del Corpus Corvus (50 proyectos)", fontsize=14, fontweight="bold")
plt.tight_layout()
out_map = FIGURES_DIR / "mapa_semantico_2d.png"
plt.savefig(out_map, dpi=150, bbox_inches="tight")
plt.close()
print(f"   ✅ Guardada: {out_map}")

# ── 8. RESUMEN FINAL ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  RESUMEN FINAL — CORVUS CLUSTERING")
print("=" * 60)
print(f"  Corpus            : {len(docs)} proyectos integradores")
print(f"  Embedding model   : paraphrase-multilingual-MiniLM-L12-v2")
print(f"  Dimensión raw     : 384D → {N_COMPONENTS}D (UMAP)")
print(f"  Algoritmo ML      : HDBSCAN")
print(f"  Clústeres         : {n_clusters}")
print(f"  Océanos Azules    : {n_noise} detectados")
print(f"  Semilla           : {RANDOM_SEED}")
print("  Artefactos:")
for f in [umap_path, hdbscan_path]:
    print(f"    {f.name:40s} {f.stat().st_size/1024:.1f} KB")
print("  Figuras:")
for f in [out_dist, out_map]:
    print(f"    {f.name:40s} {f.stat().st_size/1024:.1f} KB")
print("=" * 60)
print("\n✅ Entrenamiento completado.")
