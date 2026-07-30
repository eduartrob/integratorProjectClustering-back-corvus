# Flujo de Inteligencia Artificial (Ecosistema Corvus)

El ecosistema de Corvus no se compone únicamente de lo que pasa cuando el usuario sube un PDF, sino de toda la **Ingeniería de Datos y Entrenamiento (MLOps)** que construimos en el "laboratorio" (la carpeta de pruebas) para darle un cerebro a la plataforma. 

Aquí tienes el diagrama arquitectónico completo, dividido en la **Fase de Entrenamiento (Laboratorio)** y la **Fase de Inferencia (Producción)**.

## Arquitectura de Datos (Mermaid)

```mermaid
graph TD
    %% ============================================
    %% FASE 0: EL LABORATORIO (ENTRENAMIENTO Y MLOPS)
    %% ============================================
    subgraph Fase 0: Laboratorio (Ingeniería de Datos y Entrenamiento)
        direction TB
        
        Z1(Extracción de Ideas Reales) --> Z2[proyectos_sinteticos.csv <br/> 249 Registros Maestros]
        Z3(Simulación de Caos y OCR) --> Z4[antigravity_dataset_50.csv <br/> 250 Registros Sucios]
        
        Z2 & Z4 --> Z5{test_clasificacion_embeddings.py}
        
        Z5 -->|Vectorización FastEmbed| Z6[Entrenamiento de Regresión Logística]
        Z6 -->|Exportación Joblib| Z7[(modelo_clasificacion_embeddings.pkl)]
        
        Z6 -->|Cálculo de Silueta y Codo| Z8[Determinación Matemática: K=9]
    end

    %% ============================================
    %% FASE 1-7: PRODUCCIÓN (FLUJO DEL ESTUDIANTE)
    %% ============================================
    A[Estudiante sube PDF/Docs] -->|Extracción de Texto OCR| B(Texto Crudo / Caos)
    
    subgraph 1. Limpieza de NLP
    B --> C{limpieza_dataset.py / test_limpieza.py}
    C -->|Elimina vacíos, fragmenta por oraciones| D[Texto Listo]
    end
    
    subgraph 2. Fase Semántica
    D --> E((FastEmbed))
    E -->|384 Dimensiones| F[Vectores Densos]
    end
    
    subgraph 3. La Barrera (El Cadenero)
    Z7 -.->|Carga del Cerebro en RAM| G
    F --> G{test_clasificacion_embeddings.py}
    G -->|Ruido / Mal Hecho| H[Basura Eliminada]
    G -->|Excelente / Regular| I[Proyectos Aprobados]
    end
    
    subgraph 4. Océanos Azules (El Descubridor)
    Z8 -.->|Usa K=9| J
    I --> J{descubrir_clusters.py}
    J -->|Reducción PCA 10D| K(K-Means)
    K --> L[9 Grupos Semánticos]
    end
    
    subgraph 5. Innovación (El Cazador)
    L --> M{detectar_nichos.py}
    M -->|Isolation Forest| N[10% Nichos Innovadores]
    M -->|Isolation Forest| O[90% Mainstream]
    end
    
    subgraph 6. Bautizo (El Nombrador)
    N & O --> P{nombrar_clusters.py}
    P -->|Envía Núcleos al LLM| Q[Etiquetas: 'Visión Edge', 'RAG'...]
    end
    
    subgraph 7. Dashboard / App Móvil
    Q --> R((visualizar_clusters.py))
    R -->|t-SNE + KDE| S[Gráficas Topográficas y Cuadrículas]
    end
```

---

## Explicación del Ciclo de Vida del Proyecto

### Fase 0: El Laboratorio (Ingeniería y Entrenamiento)
Antes de que la app pudiera clasificar algo, tuvimos que construir su cerebro desde cero. 
1. **Generación de Datasets:** Creamos un dataset maestro limpio (`proyectos_sinteticos.csv`) con 249 registros etiquetados, y luego desarrollamos un motor para generar "Caos Humano" (`antigravity_dataset_50.csv`) simulando mala ortografía y errores de OCR para poner a prueba a la IA.
2. **Entrenamiento (MLOps):** Usamos el dataset maestro para entrenar matemáticamente a una Regresión Logística y la congelamos en un archivo binario `.pkl` (El Cerebro) para no tener que entrenarla en cada petición de la API.
3. **Validación de Clústeres:** Mediante el Método del Codo y el Score de Silueta (llegando a 0.53), descubrimos que la naturaleza de los proyectos de tu universidad se divide óptimamente en **9 Océanos Azules**, parámetro que dejamos fijo para el entorno de producción.

### Fase 1 a 7: El Entorno de Producción
1. **Limpieza NLP (`test_limpieza.py`):** Los textos del alumno pasan por una estandarización de caracteres y fragmentación.
2. **Vectorización:** FastEmbed traduce las palabras a coordenadas matemáticas (384 dimensiones).
3. **El Cadenero:** La API carga en milisegundos el modelo `.pkl` que entrenamos en el laboratorio y desecha la basura administrativa o proyectos mal elaborados.
4. **K-Means (El Descubridor):** Agrupa el proyecto aprobado en uno de los 9 Océanos Azules identificados previamente.
5. **Isolation Forest (El Cazador):** Analiza la densidad topográfica del clúster y define si el alumno es un "Nicho Innovador" (está solo en la orilla) o es "Mainstream".
6. **El Nombrador:** Asigna una etiqueta comercial llamando a un LLM (Ollama/OpenAI) analizando a los vecinos más cercanos del alumno.
7. **Visualización:** Generación de mapas semánticos en 2D (t-SNE) para nutrir de gráficas tu panel de administración.
