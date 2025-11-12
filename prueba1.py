# ======================================================================
# SCRIPT DEFINITIVO (VERSIÓN CON CORRECCIÓN VISUAL)
# ======================================================================
from qgis.core import (
    QgsRasterLayer, QgsProject, QgsSingleBandPseudoColorRenderer,
    QgsColorRampShader, QgsRasterShader, QgsRasterBandStats
)
from PyQt5.QtGui import QColor
import os
import numpy as np
import datetime
from pathlib import Path

# ==========================================================
# CONFIGURACIÓN
# ==========================================================
ruta_carpeta = "/home/lgo/Escritorio/Dev/roja/imagenes/prueba1" # <-- ¡AJUSTA ESTA RUTA!
nombres_archivos = { "NDVI": "NDVI.tif" }
INVERTIR_VISUAL_NDVI = True

# ==========================================================
# FUNCIONES (CON LA CORRECCIÓN)
# ==========================================================

def cargar_y_simbolizar_indice(nombre_capa, nombre_archivo, color_1, color_2, invertir_visual=False):
    """
    Carga una capa de índice (Float32) y le aplica una simbología de color dinámica.
    VERSIÓN CORREGIDA.
    """
    ruta = os.path.join(ruta_carpeta, nombre_archivo)
    if not os.path.exists(ruta):
        print(f"⚠️ No se encontró el archivo: {nombre_archivo}")
        return None

    capa = QgsRasterLayer(ruta, nombre_capa)
    if not capa.isValid():
        print(f"❌ Error cargando {nombre_archivo}")
        return None

    provider = capa.dataProvider()
    stats = provider.bandStatistics(1, QgsRasterBandStats.All, capa.extent(), 0)
    valor_min = stats.minimumValue
    valor_max = stats.maximumValue

    # --- LÓGICA DE COLOR CORREGIDA ---
    if invertir_visual:
        # Verde para valores altos, Rojo para bajos
        color_alto = color_2
        color_bajo = color_1
    else:
        # Rojo para valores altos, Verde para bajos
        color_alto = color_1
        color_bajo = color_2
        
    items = [
        QgsColorRampShader.ColorRampItem(valor_min, QColor(color_bajo), f"Bajo ({valor_min:.2f})"),
        QgsColorRampShader.ColorRampItem(0, QColor("#FFFFFF"), "Neutro (0.00)"),
        QgsColorRampShader.ColorRampItem(valor_max, QColor(color_alto), f"Alto ({valor_max:.2f})")
    ]
    # --- FIN DE LA CORRECCIÓN ---

    shader = QgsColorRampShader()
    shader.setColorRampType(QgsColorRampShader.Interpolated)
    shader.setColorRampItemList(items)
    
    raster_shader = QgsRasterShader()
    raster_shader.setRasterShaderFunction(shader)

    renderer = QgsSingleBandPseudoColorRenderer(capa.dataProvider(), 1, raster_shader)
    capa.setRenderer(renderer)
    QgsProject.instance().addMapLayer(capa)
    return capa

# (El resto de las funciones son idénticas y ya funcionan bien)

def calcular_estadisticas_numpy(capa):
    provider = capa.dataProvider()
    extent = provider.extent()
    width, height = capa.width(), capa.height()
    block = provider.block(1, extent, width, height)
    no_data = provider.sourceNoDataValue(1)
    valores_brutos = np.array([block.value(i, j) for i in range(height) for j in range(width)])
    valores_validos = valores_brutos[valores_brutos != no_data]
    if valores_validos.size == 0:
        return {'promedio': 0, 'std_dev': 0, 'rangos': {}}
    valores_indice = valores_validos
    total = valores_indice.size
    promedio = np.mean(valores_indice)
    std_dev = np.std(valores_indice)
    rangos_counts = {
        'muy_bajo': np.sum(valores_indice < -0.5), 'bajo': np.sum((valores_indice >= -0.5) & (valores_indice < 0.0)),
        'medio_bajo': np.sum((valores_indice >= 0.0) & (valores_indice < 0.2)), 'medio': np.sum((valores_indice >= 0.2) & (valores_indice < 0.4)),
        'medio_alto': np.sum((valores_indice >= 0.4) & (valores_indice < 0.6)), 'alto': np.sum((valores_indice >= 0.6) & (valores_indice < 0.8)),
        'muy_alto': np.sum(valores_indice >= 0.8)
    }
    rangos_pct = {k: (v / total) * 100 for k, v in rangos_counts.items()}
    return {'promedio': promedio, 'std_dev': std_dev, 'rangos': rangos_pct}

def analizar_capa_detallado(capa):
    provider = capa.dataProvider()
    stats = provider.bandStatistics(1)
    ancho, alto = capa.width(), capa.height()
    resolucion = capa.rasterUnitsPerPixelX()
    area_ha = (ancho * resolucion * alto * resolucion) / 10000
    print("=" * 75); print(f"📊 ANÁLISIS: {capa.name()}"); print("=" * 75)
    print("\n🌍 INFORMACIÓN ESPACIAL:")
    print(f"  • Resolución: {resolucion:.4f} m/píxel"); print(f"  • Dimensiones: {ancho} x {alto} píxeles ({ancho*alto:,} píxeles)"); print(f"  • Área total: {area_ha:.3f} ha")
    print("\n📈 ESTADÍSTICAS DEL ÍNDICE:")
    print(f"  • Rango de valores: {stats.minimumValue:.3f} a {stats.maximumValue:.3f}"); print(f"  • Promedio: {stats.mean:.3f}"); print(f"  • Desviación estándar: {stats.stdDev:.3f}")
    print("\n📊 DISTRIBUCIÓN POR CATEGORÍAS (Calculado con NumPy):")
    stats_np = calcular_estadisticas_numpy(capa)
    rangos = stats_np['rangos']
    print_distribucion(rangos, area_ha, capa.name())
    print("\n🌾 INTERPRETACIÓN:"); interpretar_indice(capa.name(), stats.mean, rangos); print()
    return {'nombre': capa.name(), 'promedio': stats.mean, 'area_ha': area_ha, 'rangos': rangos}

def print_distribucion(rangos, area_total, tipo_indice):
    if not rangos: print("  ⚠️ No hay datos disponibles"); return
    if "NDVI" in tipo_indice or "NDRE" in tipo_indice:
        categorias = {'muy_bajo': ('🔴 Crítico (<-0.5)', '█'), 'bajo': ('🟠 Muy bajo (-0.5 a 0)', '█'), 'medio_bajo': ('🟡 Bajo (0 a 0.2)', '█'), 'medio': ('🟢 Moderado (0.2 a 0.4)', '█'), 'medio_alto': ('💚 Bueno (0.4 a 0.6)', '█'), 'alto': ('🌿 Muy bueno (0.6 a 0.8)', '█'), 'muy_alto': ('🌟 Excelente (>0.8)', '█')}
    else:
        categorias = {'muy_bajo': ('🟤 Muy seco (<-0.5)', '█'), 'bajo': ('🟠 Seco (-0.5 a 0)', '█'), 'medio_bajo': ('🟡 Baja humedad (0 a 0.2)', '█'), 'medio': ('💚 Humedad normal (0.2 a 0.4)', '█'), 'medio_alto': ('💙 Buena humedad (0.4 a 0.6)', '█'), 'alto': ('💧 Alta humedad (0.6 a 0.8)', '█'), 'muy_alto': ('🌊 Saturado/Agua (>0.8)', '█')}
    for key, (label, symbol) in categorias.items():
        pct = rangos.get(key, 0); area = (pct / 100) * area_total; barra = symbol * min(int(pct / 2), 50)
        print(f"  {label:35} {pct:5.1f}% ({area:6.3f} ha) {barra}")

def interpretar_indice(nombre, promedio, rangos):
    if "NDVI" in nombre:
        if promedio < 0.2: estado = "⚠️ VEGETACIÓN ESCASA O ESTRESADA"
        elif promedio < 0.5: estado = "🟡 VEGETACIÓN MODERADA"
        else: estado = "🌟 VEGETACIÓN VIGOROSA"
    else: estado = "ℹ️ Índice personalizado"
    print(f"  • Estado General (basado en el promedio): {estado}")
    if rangos:
        pct_critico = rangos.get('muy_bajo', 0) + rangos.get('bajo', 0)
        if pct_critico > 10: print(f"  • Atención: Un {pct_critico:.1f}% del área muestra bajo vigor. Se recomienda inspección.")

# ==========================================================
# EJECUCIÓN PRINCIPAL
# ==========================================================
print("=" * 75); print("🌾 ANÁLISIS DE ÍNDICES ESPECTRALES (Desde Archivos Pre-calculados)"); print(f"📅 {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"); print("=" * 75)
print("\n🚀 Cargando y simbolizando capas...\n")
capas = {}
if "NDVI" in nombres_archivos:
    capas["NDVI"] = cargar_y_simbolizar_indice("NDVI", nombres_archivos["NDVI"], "#8B0000", "#00FF00", INVERTIR_VISUAL_NDVI)
capas = {k:v for k,v in capas.items() if v is not None}
if not capas:
    print("\n❌ No se cargaron capas. Verifica la `ruta_carpeta` y los `nombres_archivos` en la configuración.")
else:
    print(f"\n✅ {len(capas)} capa(s) cargada(s) y simbolizada(s).\n")
    resultados = []
    for nombre, capa in capas.items():
        resultados.append(analizar_capa_detallado(capa))
print("\n" + "=" * 75); print("✅ ANÁLISIS COMPLETADO EXITOSAMENTE"); print("=" * 75)