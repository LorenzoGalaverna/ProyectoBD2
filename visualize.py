"""
Módulo de Visualización de Datos
Genera gráficos y análisis visuales usando matplotlib
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os
import config

# Configurar estilo de matplotlib
plt.style.use('default')


def configure_plot_style():
    """Configura el estilo global de los gráficos"""
    plt.rcParams['figure.figsize'] = config.FIGURE_SIZE
    plt.rcParams['figure.dpi'] = config.DPI
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.labelsize'] = 11
    plt.rcParams['xtick.labelsize'] = 9
    plt.rcParams['ytick.labelsize'] = 9
    plt.rcParams['legend.fontsize'] = 9


def add_figure_footer(fig, footer_text, y_position=-0.05):
    """
    Agrega una nota al pie del gráfico de forma consistente

    Args:
        fig: Figura de matplotlib
        footer_text: Texto de la nota al pie
        y_position: Posición vertical (default: -0.05)
    """
    fig.text(0.5, y_position, footer_text,
             ha='center', va='top', fontsize=8, style='italic',
             color='gray', wrap=True)


def plot_consumo_agua_por_pais(fact_table, dim_geografia):
    """
    Gráfico de barras: Top 10 países por consumo de agua estimado
    
    Args:
        fact_table: DataFrame de tabla de hechos
        dim_geografia: DataFrame de dimensión geografía
    """
    print("   📊 Generando gráfico: Consumo de agua por país...")
    
    # Unir con dimensión geografía
    df = fact_table.merge(dim_geografia, on='GeografiaID')
    
    # Agrupar por país
    consumo_por_pais = df.groupby('Country').agg({
        'ConsumoAguaEstimado': 'sum',
        'TotalPrompts': 'sum'
    }).sort_values('ConsumoAguaEstimado', ascending=False).head(10)
    
    # Crear gráfico
    fig, ax = plt.subplots(figsize=(12, 6))
    
    bars = ax.bar(range(len(consumo_por_pais)), 
                   consumo_por_pais['ConsumoAguaEstimado'],
                   color='steelblue', alpha=0.8, edgecolor='black')
    
    ax.set_xlabel('País', fontweight='bold')
    ax.set_ylabel('Consumo de Agua Estimado (Litros)', fontweight='bold')
    ax.set_title('Top 10 Países por Consumo de Agua Estimado en Uso de IA\n' +
                 'Período: Junio 2024 - Junio 2025 (Acumulado Anual)',
                 fontweight='bold', fontsize=14, pad=20)
    ax.set_xticks(range(len(consumo_por_pais)))
    ax.set_xticklabels(consumo_por_pais.index, rotation=45, ha='right')
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # Agregar valores en las barras
    for i, (bar, value) in enumerate(zip(bars, consumo_por_pais['ConsumoAguaEstimado'])):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                f'{value:,.0f}L', ha='center', va='bottom', fontsize=9)

    # Agregar nota al pie
    add_figure_footer(fig, 'Factor: 0.5L/prompt | Países asignados aleatoriamente a sesiones')

    plt.tight_layout()
    filepath = os.path.join(config.VISUALIZATIONS_DIR, '01_consumo_agua_por_pais.png')
    plt.savefig(filepath, dpi=config.DPI, bbox_inches='tight')
    plt.close()
    
    print(f"      ✓ Guardado: {filepath}")


def plot_uso_por_disciplina(fact_table, dim_estudiante):
    """
    Gráfico de barras horizontales: Uso de IA por disciplina
    
    Args:
        fact_table: DataFrame de tabla de hechos
        dim_estudiante: DataFrame de dimensión estudiante
    """
    print("   📊 Generando gráfico: Uso de IA por disciplina...")
    
    # Unir con dimensión estudiante
    df = fact_table.merge(dim_estudiante, on='EstudianteID')
    
    # Agrupar por disciplina
    uso_por_disciplina = df.groupby('Discipline').agg({
        'TotalPrompts': 'sum',
        'NumeroSesiones': 'sum',
        'SessionLengthMin': 'sum'
    }).sort_values('TotalPrompts', ascending=True)
    
    # Crear gráfico
    fig, ax = plt.subplots(figsize=(12, 8))
    
    bars = ax.barh(range(len(uso_por_disciplina)), 
                   uso_por_disciplina['TotalPrompts'],
                   color='coral', alpha=0.8, edgecolor='black')
    
    ax.set_ylabel('Disciplina', fontweight='bold')
    ax.set_xlabel('Total de Prompts', fontweight='bold')
    ax.set_title('Uso de Asistente de IA por Disciplina Académica\n' +
                 'Total de Prompts (Junio 2024 - Junio 2025)',
                 fontweight='bold', fontsize=14, pad=20)
    ax.set_yticks(range(len(uso_por_disciplina)))
    ax.set_yticklabels(uso_por_disciplina.index)
    ax.grid(axis='x', alpha=0.3, linestyle='--')

    # Agregar valores en las barras
    for i, (bar, value) in enumerate(zip(bars, uso_por_disciplina['TotalPrompts'])):
        ax.text(bar.get_width() + 100, bar.get_y() + bar.get_height()/2,
                f'{value:,}', va='center', fontsize=9)

    # Agregar nota al pie
    add_figure_footer(fig, 'Datos basados en 10,000 sesiones de estudiantes')

    plt.tight_layout()
    filepath = os.path.join(config.VISUALIZATIONS_DIR, '02_uso_por_disciplina.png')
    plt.savefig(filepath, dpi=config.DPI, bbox_inches='tight')
    plt.close()
    
    print(f"      ✓ Guardado: {filepath}")


def plot_tendencia_temporal(fact_table, dim_tiempo):
    """
    Gráfico de líneas: Tendencia temporal del uso de IA
    
    Args:
        fact_table: DataFrame de tabla de hechos
        dim_tiempo: DataFrame de dimensión tiempo
    """
    print("   📊 Generando gráfico: Tendencia temporal...")
    
    # Unir con dimensión tiempo
    df = fact_table.merge(dim_tiempo, on='TiempoID')
    
    # Agrupar por año y mes
    df['AñoMes'] = pd.to_datetime(df['Fecha']).dt.to_period('M')
    tendencia = df.groupby('AñoMes').agg({
        'TotalPrompts': 'sum',
        'ConsumoAguaEstimado': 'sum',
        'NumeroSesiones': 'sum'
    }).reset_index()
    
    tendencia['AñoMes'] = tendencia['AñoMes'].dt.to_timestamp()
    
    # Crear gráfico con dos ejes Y
    fig, ax1 = plt.subplots(figsize=(14, 6))
    
    color1 = 'tab:blue'
    ax1.set_xlabel('Mes', fontweight='bold')
    ax1.set_ylabel('Total de Prompts', color=color1, fontweight='bold')
    line1 = ax1.plot(tendencia['AñoMes'], tendencia['TotalPrompts'], 
                     color=color1, marker='o', linewidth=2, label='Total Prompts')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True, alpha=0.3, linestyle='--')
    
    ax2 = ax1.twinx()
    color2 = 'tab:orange'
    ax2.set_ylabel('Consumo de Agua (Litros)', color=color2, fontweight='bold')
    line2 = ax2.plot(tendencia['AñoMes'], tendencia['ConsumoAguaEstimado'], 
                     color=color2, marker='s', linewidth=2, label='Consumo Agua')
    ax2.tick_params(axis='y', labelcolor=color2)
    
    # Formato de fechas en eje X
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')

    # Título
    ax1.set_title('Tendencia Temporal: Uso de IA y Consumo de Agua Estimado\n' +
                  'Evolución Mensual (Junio 2024 - Junio 2025)',
                  fontweight='bold', fontsize=14, pad=20)

    # Leyenda combinada
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    # Agregar nota al pie
    add_figure_footer(fig, 'Consumo calculado como: Prompts × 0.5L/prompt')

    plt.tight_layout()
    filepath = os.path.join(config.VISUALIZATIONS_DIR, '03_tendencia_temporal.png')
    plt.savefig(filepath, dpi=config.DPI, bbox_inches='tight')
    plt.close()
    
    print(f"      ✓ Guardado: {filepath}")


def plot_uso_por_nivel_academico(fact_table, dim_estudiante):
    """
    Gráfico de pastel: Distribución de sesiones por nivel académico
    
    Args:
        fact_table: DataFrame de tabla de hechos
        dim_estudiante: DataFrame de dimensión estudiante
    """
    print("   📊 Generando gráfico: Distribución por nivel académico...")
    
    # Unir con dimensión estudiante
    df = fact_table.merge(dim_estudiante, on='EstudianteID')
    
    # Agrupar por nivel académico
    uso_por_nivel = df.groupby('StudentLevel').agg({
        'NumeroSesiones': 'sum'
    }).sort_values('NumeroSesiones', ascending=False)
    
    # Crear gráfico
    fig, ax = plt.subplots(figsize=(10, 8))
    
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc']
    explode = [0.05] * len(uso_por_nivel)  # Separar ligeramente todos los segmentos
    
    wedges, texts, autotexts = ax.pie(uso_por_nivel['NumeroSesiones'], 
                                        labels=uso_por_nivel.index,
                                        autopct='%1.1f%%',
                                        colors=colors[:len(uso_por_nivel)],
                                        explode=explode,
                                        startangle=90,
                                        textprops={'fontsize': 11})
    
    # Mejorar apariencia de los textos
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')

    ax.set_title('Distribución de Sesiones de IA por Nivel Académico\n' +
                 'Total: 10,000 sesiones (Junio 2024 - Junio 2025)',
                 fontweight='bold', fontsize=14, pad=20)

    # Agregar leyenda con conteos
    legend_labels = [f'{level}: {count:,} sesiones'
                    for level, count in uso_por_nivel['NumeroSesiones'].items()]
    ax.legend(legend_labels, loc='upper left', bbox_to_anchor=(1, 1))

    # Agregar nota al pie
    add_figure_footer(fig, 'Cada sesión representa una interacción completa con el asistente de IA', y_position=-0.08)

    plt.tight_layout()
    filepath = os.path.join(config.VISUALIZATIONS_DIR, '04_distribucion_nivel_academico.png')
    plt.savefig(filepath, dpi=config.DPI, bbox_inches='tight')
    plt.close()
    
    print(f"      ✓ Guardado: {filepath}")


def plot_escasez_vs_consumo(fact_table, dim_geografia):
    """
    Gráfico de barras agrupadas: Consumo de agua vs nivel de escasez
    
    Args:
        fact_table: DataFrame de tabla de hechos
        dim_geografia: DataFrame de dimensión geografía
    """
    print("   📊 Generando gráfico: Consumo vs escasez de agua...")
    
    # Unir con dimensión geografía
    df = fact_table.merge(dim_geografia, on='GeografiaID')
    
    # Agrupar por nivel de escasez
    consumo_por_escasez = df.groupby('WaterScarcityLevel').agg({
        'ConsumoAguaEstimado': 'sum',
        'NumeroSesiones': 'sum',
        'TotalPrompts': 'sum'
    })
    
    # Ordenar por un orden lógico
    order = ['Low', 'Moderate', 'High']
    consumo_por_escasez = consumo_por_escasez.reindex(
        [o for o in order if o in consumo_por_escasez.index]
    )
    
    # Crear gráfico
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = np.arange(len(consumo_por_escasez))
    width = 0.25
    
    bars1 = ax.bar(x - width, consumo_por_escasez['ConsumoAguaEstimado'], 
                   width, label='Consumo Agua (L)', color='skyblue', edgecolor='black')
    bars2 = ax.bar(x, consumo_por_escasez['NumeroSesiones'] * 10, 
                   width, label='Sesiones (x10)', color='lightcoral', edgecolor='black')
    bars3 = ax.bar(x + width, consumo_por_escasez['TotalPrompts'], 
                   width, label='Total Prompts', color='lightgreen', edgecolor='black')
    
    ax.set_xlabel('Nivel de Escasez de Agua', fontweight='bold')
    ax.set_ylabel('Valores', fontweight='bold')
    ax.set_title('Relación entre Uso de IA y Nivel de Escasez Hídrica\n' +
                 'Comparativa por Nivel de Escasez (Junio 2024 - Junio 2025)',
                 fontweight='bold', fontsize=14, pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(consumo_por_escasez.index)
    ax.legend()
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # Agregar nota al pie
    add_figure_footer(fig, 'Sesiones ×10 para escala visual | Países clasificados según dataset global de agua')

    plt.tight_layout()
    filepath = os.path.join(config.VISUALIZATIONS_DIR, '05_escasez_vs_consumo.png')
    plt.savefig(filepath, dpi=config.DPI, bbox_inches='tight')
    plt.close()
    
    print(f"      ✓ Guardado: {filepath}")


def plot_promedio_duracion_por_trimestre(fact_table, dim_tiempo):
    """
    Gráfico de líneas: Duración promedio de sesiones por trimestre
    
    Args:
        fact_table: DataFrame de tabla de hechos
        dim_tiempo: DataFrame de dimensión tiempo
    """
    print("   📊 Generando gráfico: Duración promedio por trimestre...")
    
    # Unir con dimensión tiempo
    df = fact_table.merge(dim_tiempo, on='TiempoID')
    
    # Agrupar por año y trimestre
    duracion_trimestral = df.groupby(['Año', 'Trimestre']).agg({
        'SessionLengthMin': 'mean',
        'TotalPrompts': 'mean'
    }).reset_index()
    
    duracion_trimestral['Periodo'] = (duracion_trimestral['Año'].astype(str) + 
                                       '-Q' + duracion_trimestral['Trimestre'].astype(str))
    
    # Crear gráfico
    fig, ax = plt.subplots(figsize=(14, 6))
    
    ax.plot(duracion_trimestral['Periodo'], duracion_trimestral['SessionLengthMin'], 
            marker='o', linewidth=2, markersize=8, color='purple', label='Duración Promedio')
    
    ax.set_xlabel('Trimestre', fontweight='bold')
    ax.set_ylabel('Duración Promedio (Minutos)', fontweight='bold')
    ax.set_title('Duración Promedio de Sesiones de IA por Trimestre\n' +
                 'Minutos promedio por sesión (Q3 2024 - Q2 2025)',
                 fontweight='bold', fontsize=14, pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    ax.legend()

    # Agregar línea de tendencia
    z = np.polyfit(range(len(duracion_trimestral)), duracion_trimestral['SessionLengthMin'], 1)
    p = np.poly1d(z)
    ax.plot(duracion_trimestral['Periodo'], p(range(len(duracion_trimestral))),
            "r--", alpha=0.5, linewidth=2, label='Tendencia')
    ax.legend()

    # Agregar nota al pie
    add_figure_footer(fig, 'Línea roja indica tendencia general')

    plt.tight_layout()
    filepath = os.path.join(config.VISUALIZATIONS_DIR, '06_duracion_promedio_trimestre.png')
    plt.savefig(filepath, dpi=config.DPI, bbox_inches='tight')
    plt.close()
    
    print(f"      ✓ Guardado: {filepath}")


def plot_heatmap_disciplina_nivel(fact_table, dim_estudiante):
    """
    Gráfico de matriz: Prompts por disciplina y nivel académico
    
    Args:
        fact_table: DataFrame de tabla de hechos
        dim_estudiante: DataFrame de dimensión estudiante
    """
    print("   📊 Generando gráfico: Matriz disciplina vs nivel...")
    
    # Unir con dimensión estudiante
    df = fact_table.merge(dim_estudiante, on='EstudianteID')
    
    # Crear tabla pivote
    pivot = df.pivot_table(values='TotalPrompts', 
                           index='Discipline', 
                           columns='StudentLevel', 
                           aggfunc='sum',
                           fill_value=0)
    
    # Crear gráfico
    fig, ax = plt.subplots(figsize=(12, 8))
    
    im = ax.imshow(pivot.values, cmap='YlOrRd', aspect='auto')
    
    # Configurar ejes
    ax.set_xticks(np.arange(len(pivot.columns)))
    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_xticklabels(pivot.columns)
    ax.set_yticklabels(pivot.index)
    
    # Rotar etiquetas
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    # Agregar valores en cada celda
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            value = pivot.values[i, j]
            text = ax.text(j, i, f'{value:,.0f}',
                          ha="center", va="center", color="black" if value < pivot.values.max()/2 else "white",
                          fontsize=9)
    
    ax.set_title('Total de Prompts por Disciplina y Nivel Académico\n' +
                 'Distribución Acumulada (Junio 2024 - Junio 2025)',
                 fontweight='bold', fontsize=14, pad=20)
    ax.set_xlabel('Nivel Académico', fontweight='bold')
    ax.set_ylabel('Disciplina', fontweight='bold')

    # Barra de color
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Total de Prompts', rotation=270, labelpad=20, fontweight='bold')

    # Agregar nota al pie
    add_figure_footer(fig, 'Intensidad de color indica mayor uso de IA')

    plt.tight_layout()
    filepath = os.path.join(config.VISUALIZATIONS_DIR, '07_matriz_disciplina_nivel.png')
    plt.savefig(filepath, dpi=config.DPI, bbox_inches='tight')
    plt.close()
    
    print(f"      ✓ Guardado: {filepath}")


def generate_dashboard_summary(fact_table, dim_tiempo, dim_geografia, dim_estudiante):
    """
    Genera un dashboard con múltiples métricas
    
    Args:
        fact_table: DataFrame de tabla de hechos
        dim_tiempo: DataFrame de dimensión tiempo
        dim_geografia: DataFrame de dimensión geografía
        dim_estudiante: DataFrame de dimensión estudiante
    """
    print("   📊 Generando dashboard resumen...")
    
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 3, hspace=0.4, wspace=0.3)
    
    # 1. KPIs principales
    ax1 = fig.add_subplot(gs[0, :])
    ax1.axis('off')
    
    total_prompts = fact_table['TotalPrompts'].sum()
    total_agua = fact_table['ConsumoAguaEstimado'].sum()
    total_sesiones = fact_table['NumeroSesiones'].sum()
    duracion_total = fact_table['SessionLengthMin'].sum()
    
    kpi_text = f"""
    INDICADORES CLAVE DEL DATA WAREHOUSE (Junio 2024 - Junio 2025)

    📊 Total de Prompts (Anual): {total_prompts:,}                 💧 Consumo de Agua Estimado (Anual): {total_agua:,.2f} Litros

    🎯 Número de Sesiones (Anual): {total_sesiones:,}              ⏱️ Duración Total (Anual): {duracion_total:,.2f} Minutos ({duracion_total/60:,.2f} Horas)

    📈 Promedio de Prompts/Sesión: {total_prompts/total_sesiones:.2f}    ⏰ Duración Promedio/Sesión: {duracion_total/total_sesiones:.2f} Min
    """
    
    ax1.text(0.5, 0.5, kpi_text, ha='center', va='center', fontsize=11, 
             family='monospace', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
    
    # 2. Top 5 países
    ax2 = fig.add_subplot(gs[1, 0])
    df_geo = fact_table.merge(dim_geografia, on='GeografiaID')
    top_paises = df_geo.groupby('Country')['ConsumoAguaEstimado'].sum().nlargest(5)
    ax2.barh(range(len(top_paises)), top_paises.values, color='steelblue')
    ax2.set_yticks(range(len(top_paises)))
    ax2.set_yticklabels(top_paises.index, fontsize=8)
    ax2.set_title('Top 5 Países - Consumo Agua', fontweight='bold', fontsize=10)
    ax2.grid(axis='x', alpha=0.3)
    
    # 3. Distribución por nivel
    ax3 = fig.add_subplot(gs[1, 1])
    df_est = fact_table.merge(dim_estudiante, on='EstudianteID')
    nivel_dist = df_est.groupby('StudentLevel')['NumeroSesiones'].sum()
    ax3.pie(nivel_dist.values, labels=nivel_dist.index, autopct='%1.1f%%', 
            colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99'])
    ax3.set_title('Distribución por Nivel', fontweight='bold', fontsize=10)
    
    # 4. Top 5 disciplinas
    ax4 = fig.add_subplot(gs[1, 2])
    top_disc = df_est.groupby('Discipline')['TotalPrompts'].sum().nlargest(5)
    ax4.bar(range(len(top_disc)), top_disc.values, color='coral')
    ax4.set_xticks(range(len(top_disc)))
    ax4.set_xticklabels(top_disc.index, rotation=45, ha='right', fontsize=8)
    ax4.set_title('Top 5 Disciplinas - Prompts', fontweight='bold', fontsize=10)
    ax4.grid(axis='y', alpha=0.3)
    
    # 5. Tendencia mensual
    ax5 = fig.add_subplot(gs[2, :])
    df_time = fact_table.merge(dim_tiempo, on='TiempoID')
    df_time['AñoMes'] = pd.to_datetime(df_time['Fecha']).dt.to_period('M')
    tendencia = df_time.groupby('AñoMes')['ConsumoAguaEstimado'].sum()
    ax5.plot(range(len(tendencia)), tendencia.values, marker='o', linewidth=2, color='green')
    ax5.set_xticks(range(0, len(tendencia), max(1, len(tendencia)//10)))
    ax5.set_xticklabels([str(tendencia.index[i]) for i in range(0, len(tendencia), max(1, len(tendencia)//10))], 
                        rotation=45, ha='right', fontsize=8)
    ax5.set_title('Tendencia Mensual - Consumo de Agua', fontweight='bold', fontsize=10)
    ax5.set_ylabel('Litros', fontsize=9)
    ax5.grid(True, alpha=0.3)
    
    fig.suptitle('DASHBOARD DE ANÁLISIS - USO DE IA Y CONSUMO DE AGUA ESTIMADO\n' +
                 'Período: Junio 2024 - Junio 2025',
                 fontweight='bold', fontsize=16, y=0.98)

    # Agregar nota al pie
    fig.text(0.5, 0.01, 'Consumo de agua: Estimación basada en factor hipotético de 0.5L/prompt',
             ha='center', va='bottom', fontsize=8, style='italic', color='gray')

    filepath = os.path.join(config.VISUALIZATIONS_DIR, '08_dashboard_resumen.png')
    plt.savefig(filepath, dpi=config.DPI, bbox_inches='tight')
    plt.close()
    
    print(f"      ✓ Guardado: {filepath}")


def visualize_all_data(dim_tiempo, dim_geografia, dim_estudiante, fact_table):
    """
    Genera todas las visualizaciones
    
    Args:
        dim_tiempo: Dimensión Tiempo
        dim_geografia: Dimensión Geografía
        dim_estudiante: Dimensión Estudiante
        fact_table: Tabla de hechos
    """
    print("\n" + "="*80)
    print("FASE 4: VISUALIZACIÓN DE DATOS")
    print("="*80)
    
    print("\n🎨 Configurando estilo de gráficos...")
    configure_plot_style()
    
    print("\n🎨 Generando visualizaciones...")
    
    plot_consumo_agua_por_pais(fact_table, dim_geografia)
    plot_uso_por_disciplina(fact_table, dim_estudiante)
    plot_tendencia_temporal(fact_table, dim_tiempo)
    plot_uso_por_nivel_academico(fact_table, dim_estudiante)
    plot_escasez_vs_consumo(fact_table, dim_geografia)
    plot_promedio_duracion_por_trimestre(fact_table, dim_tiempo)
    plot_heatmap_disciplina_nivel(fact_table, dim_estudiante)
    generate_dashboard_summary(fact_table, dim_tiempo, dim_geografia, dim_estudiante)
    
    print("\n✅ Visualización completada:")
    print(f"   - 8 gráficos generados")
    print(f"   - Ubicación: {config.VISUALIZATIONS_DIR}")


if __name__ == "__main__":
    # Prueba del módulo
    from extract import extract_all_data
    from transform import transform_all_data
    
    df_ai, df_water = extract_all_data()
    
    if not df_ai.empty and not df_water.empty:
        dim_tiempo, dim_geografia, dim_estudiante, fact_table = transform_all_data(df_ai, df_water)
        visualize_all_data(dim_tiempo, dim_geografia, dim_estudiante, fact_table)
