# Sistema de Optimización de Rutas de Última Milla con Algoritmos Genéticos

## Resumen
Plataforma de logística basada en la nube que optimiza las rutas de entrega de última milla para flotillas de reparto considerando variables dinámicas como tráfico en tiempo real, ventanas de tiempo de entrega del cliente, y capacidad volumétrica de los vehículos. Utiliza algoritmos genéticos y heurísticas de optimización para reducir los costos de combustible y el tiempo en ruta.

## Introducción
La logística de última milla es el eslabón más costoso e ineficiente de la cadena de suministro, representando hasta el 53% del costo total de envío. En zonas urbanas densamente pobladas, los cuellos de botella por tráfico y las entregas fallidas reducen drásticamente la rentabilidad del comercio electrónico. Las soluciones de enrutamiento estáticas no pueden adaptarse a las condiciones cambiantes del entorno urbano.

## Objetivo General
Desarrollar un sistema de enrutamiento dinámico inteligente que reduzca los costos operativos (combustible y tiempo) en un 20% mediante la aplicación de algoritmos evolutivos para la optimización de rutas de reparto de última milla.

## Objetivos Específicos
- Modelar el problema de enrutamiento de vehículos con ventanas de tiempo (VRPTW) adaptado a las restricciones vehiculares de la ciudad.
- Implementar un algoritmo genético cruzado con búsqueda local (Memetic Algorithm) para encontrar rutas cuasi-óptimas en menos de 5 minutos de procesamiento.
- Integrar APIs de tráfico en tiempo real (Google Maps API / Waze) para el ajuste dinámico de pesos en los arcos del grafo de la ciudad.
- Desarrollar una aplicación móvil para los conductores que reciba y actualice la ruta óptima en tiempo real.
- Crear un panel de control web para despachadores que muestre la ubicación GPS de la flotilla y el estado de cada entrega.

## Justificación
El auge del comercio electrónico ha saturado las capacidades logísticas de las empresas de paquetería tradicionales. La optimización de rutas no solo tiene un impacto económico directo al reducir el consumo de combustible, sino que también disminuye la huella de carbono de las operaciones logísticas y mejora la experiencia del cliente al cumplir con las ventanas de entrega prometidas.

## Metodología
Investigación aplicada con desarrollo iterativo. El algoritmo se programará y probará primero en entornos simulados usando instancias estandarizadas del problema de Solomon para VRPTW. Posteriormente, se realizará una prueba piloto de 4 semanas con una empresa local de mensajería (flotilla de 10 camionetas), comparando los KPIs logísticos contra su ruteo manual tradicional.

## Stack Tecnológico
- Backend: Python (FastAPI), Celery para procesamiento asíncrono
- Algoritmia: DEAP (Distributed Evolutionary Algorithms in Python), NetworkX
- Frontend web: Vue.js, Mapbox GL JS para renderizado de mapas
- App Móvil: React Native con geolocalización en background
- Base de datos: PostgreSQL con extensión PostGIS para datos espaciales

## Alcance
El sistema optimizará rutas para una flotilla máxima de 50 vehículos simultáneos. Se enfoca exclusivamente en la entrega terrestre urbana (última milla). No incluye módulos de gestión de inventario, facturación o mantenimiento de vehículos.

## Conclusión
La combinación de algoritmos bio-inspirados con datos geoespaciales en tiempo real ofrece una solución robusta y escalable al problema de la última milla, permitiendo a las empresas logísticas locales competir en eficiencia operativa con los gigantes del comercio electrónico.
