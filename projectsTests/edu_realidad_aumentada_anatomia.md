# Aplicación de Realidad Aumentada para Enseñanza de Anatomía Humana

## Resumen
Aplicación de realidad aumentada para tablets y smartphones que superpone modelos 3D interactivos del cuerpo humano sobre el cuerpo real del estudiante usando la cámara del dispositivo. Los estudiantes de medicina y enfermería pueden explorar órganos, sistemas y estructuras anatómicas en contexto espacial real, rotarlos, segmentarlos y ver animaciones de funciones fisiológicas en tiempo real.

## Introducción
El estudio de la anatomía humana ha sido históricamente dependiente de cadáveres y modelos plásticos costosos. Las restricciones post-COVID en laboratorios de anatomía y el alto costo de mantenimiento de cadáveres han generado una brecha educativa significativa. La realidad aumentada permite el estudio de anatomía con precisión científica, sin restricciones éticas y con una disponibilidad ilimitada para práctica individual.

## Objetivo General
Desarrollar una aplicación de realidad aumentada para iOS y Android que provea modelos anatómicos 3D interactivos y contextualmente situados en el cuerpo del estudiante para el estudio de anatomía humana en carreras de ciencias de la salud.

## Objetivos Específicos
- Crear una biblioteca de 200 modelos anatómicos 3D de alta fidelidad basados en el Visible Human Project y segmentaciones de TAC anónimas.
- Implementar detección de cuerpo completo en tiempo real usando MediaPipe para anclar los modelos 3D en la posición anatómica correcta sobre el cuerpo del usuario.
- Desarrollar modo disección virtual donde el estudiante puede activar y desactivar capas anatómicas (piel, tejido subcutáneo, músculo, hueso, órganos).
- Crear ejercicios de identificación cronometrados donde el sistema señala estructuras al azar y el estudiante debe nombrarlas correctamente.
- Integrar narración de audio con descripción anatómica, función fisiológica e importancia clínica de cada estructura seleccionada.

## Justificación
Un modelo plástico de torso completo cuesta entre 15,000 y 50,000 pesos. Una sala de anatomía con cadáveres requiere inversiones de millones de pesos y costos de mantenimiento continuos. La aplicación puede distribuirse a cualquier estudiante con smartphone a costo marginal cero y está disponible fuera del horario de laboratorio.

## Metodología
Diseño iterativo de UX con estudiantes de medicina del 2° semestre como usuarios piloto. Los modelos 3D se validarán con médicos especialistas en anatomía. La efectividad pedagógica se evaluará mediante pruebas de identificación anatómica cronometradas comparando grupos con y sin la aplicación.

## Stack Tecnológico
- AR: ARKit (iOS), ARCore (Android), Unity 3D con XR Interaction Toolkit
- Modelos 3D: Blender para optimización de meshes, formato glTF 2.0
- Detección de cuerpo: MediaPipe Pose Landmarks
- Backend: Firebase Realtime Database para progreso del estudiante
- Audio: texto a voz neural en español con Amazon Polly

## Alcance
La aplicación cubre los sistemas esquelético, muscular, cardiovascular, digestivo y nervioso central. Diseñada para estudiantes de primero y segundo año de medicina y enfermería. No incluye anatomía de desarrollo fetal ni de regiones genitales.

## Conclusión
La realidad aumentada democratiza el acceso al estudio de anatomía de alta calidad, eliminando las barreras logísticas, económicas y éticas del laboratorio convencional, y provee una experiencia de aprendizaje espacialmente intuitiva que mejora la retención de estructuras complejas.
