# Análisis Automatizado de Índices de Vegetación para QGIS

## Breve Explicación

Este proyecto es una herramienta de agricultura de precisión que automatiza el análisis de imágenes multiespectrales de drones. Consiste en un flujo de trabajo de dos scripts para PyQGIS que primero calculan índices de vegetación clave (NDVI, NDWI, NDRE) a partir de un ortomosaico crudo y luego generan un reporte estadístico detallado sobre la salud, el estado hídrico y la variabilidad del cultivo.

El sistema está diseñado para ser eficiente, preciso y fácil de usar, transformando datos complejos de drones en información accionable para la toma de decisiones agrícolas.

---

## Características Principales

*   **Automatización Completa:** Procesa desde el ortomosaico hasta el reporte final con mínima intervención manual.
*   **Análisis Multíndice:** Calcula y analiza simultáneamente NDVI, NDWI y NDRE para un diagnóstico integral.
*   **Reportes Detallados:** Genera estadísticas clave como promedio, desviación estándar, coeficiente de variación y distribución por categorías en hectáreas y porcentaje.
*   **Diagnóstico Inteligente:** Proporciona una interpretación del estado del cultivo y un análisis cruzado entre índices (ej. NDVI vs. NDWI).
*   **Alta Eficiencia:** Utiliza la librería NumPy для un procesamiento numérico extremadamente rápido, incluso con imágenes grandes.
*   **Visualización Automática:** Carga y simboliza automáticamente las capas de índices generadas en el proyecto de QGIS con una rampa de color intuitiva.

## Flujo de Trabajo

El proceso está dividido en dos fases para garantizar la precisión y modularidad de los datos.

1.  **Fase 1: Cálculo de Índices (`calcular_indices.py`)**
    *   **Entrada:** Un único ortomosaico multiespectral en formato GeoTIFF (`.tif`) que contiene todas las bandas del sensor (ej. Rojo, Verde, Borde Rojo, NIR).
    *   **Proceso:** El script utiliza la Calculadora Ráster de QGIS para generar los archivos de índice individuales (`NDVI.tif`, `NDWI.tif`, etc.).
    *   **Salida:** Archivos GeoTIFF de una sola banda y tipo `Float32`, donde cada píxel contiene el valor numérico real del índice (entre -1.0 y +1.0).

2.  **Fase 2: Análisis y Reporte (`analizar_indices.py`)**
    *   **Entrada:** Los archivos de índice (`.tif`) generados en la Fase 1.
    *   **Proceso:** El script carga cada índice, calcula estadísticas detalladas usando NumPy y genera un reporte en la consola de Python de QGIS.
    *   **Salida:** Un informe de texto completo y la visualización de las capas en QGIS.

## Requisitos

*   **Software:** QGIS 3.x.
*   **Datos de Entrada:** Un ortomosaico en formato GeoTIFF multiespectral. Es **crucial** que este archivo contenga las bandas **Infrarrojo Cercano (NIR)** y **Borde Rojo (RedEdge)** para el cálculo de los índices.
*   **Información Clave:** El **mapeo de bandas** del sensor. Necesitas saber qué número de banda en el archivo `.tif` corresponde a cada espectro (ej. Banda 5 = Rojo, Banda 7 = NIR).

## Instrucciones de Uso

### Paso 1: Configurar y Ejecutar el Script de Cálculo

1.  Abre el archivo `calcular_indices.py` en un editor.
2.  Modifica la sección de `CONFIGURACIÓN` con las rutas a tu ortomosaico y la carpeta de salida.
    ```python
    # Ejemplo de configuración
    ruta_ortomosaico_multiespectral = "/ruta/a/tu/ortomosaico.tif"
    ruta_salida_indices = "/ruta/a/tus/resultados/indices"
    ```
3.  **Ajusta el `mapeo_bandas` con la información correcta de tu sensor.** Este es el paso más importante para la precisión del resultado.
    ```python
    # Ejemplo de mapeo
    mapeo_bandas = {
        "Verde": 2,
        "Rojo": 5,
        "BordeRojo": 6,
        "NIR": 7
    }
    ```
4.  Copia y pega el código en la **Consola de Python de QGIS** y ejecútalo.
5.  Verifica que los nuevos archivos de índice se hayan creado en tu carpeta de salida.

### Paso 2: Configurar y Ejecutar el Script de Análisis

1.  Abre tu script de análisis (`analizar_indices.py`).
2.  Asegúrate de que la función `calcular_estadisticas_numpy` **NO contenga la línea de normalización** (la que convierte de `0-255` a `-1 a 1`), ya que los datos de entrada ya son `Float32`.
3.  Ajusta la `ruta_carpeta` para que apunte a la carpeta donde se guardaron los índices calculados en el paso anterior.
    ```python
    # Ejemplo de configuración
    ruta_carpeta = "/ruta/a/tus/resultados/indices"
    ruta_salida = "/ruta/a/tus/resultados/reporte"
    ```
4.  Copia y pega el código en la **Consola de Python de QGIS** y ejecútalo.

### Paso 3: Interpretar los Resultados

El script imprimirá en la consola un reporte detallado que incluye:

*   **Análisis Individual por Índice:**
    *   **Información Espacial:** Resolución, dimensiones y área total en hectáreas.
    *   **Estadísticas:** Promedio, desviación estándar y coeficiente de variación.
    *   **Distribución por Categorías:** Un desglose visual y numérico del porcentaje y área que ocupa cada nivel del índice (ej. 'Vegetación Vigorosa', 'Estrés Hídrico', etc.).
    *   **Interpretación:** Un diagnóstico automático del estado general y la variabilidad del campo.
*   **Reporte Comparativo Final:**
    *   Una tabla resumen para comparar los valores promedio de todos los índices.
    *   Un diagnóstico integrado que cruza los datos (ej. NDVI vs. NDWI) para detectar problemas específicos como estrés hídrico en zonas de alta vegetación.

---
**Autor:** [Martin Luis Alejandro]
**Fecha:** Noviembre 2025
**Licencia:** [-]