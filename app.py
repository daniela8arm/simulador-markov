import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

st.set_page_config(page_title="Simulador CDMX", page_icon="🚇", layout="wide")

# Función para cargar matrices con cache
@st.cache_data
def cargar_matriz(nombre_archivo):
    return pd.read_csv(nombre_archivo, index_col=0)

# ---- ENCABEZADO ----
st.title("🚇 Simulador de Incidentes en el Metro CDMX")
st.subheader("Modelo de Cadenas de Markov en escenarios con y sin refuerzo policial")
st.markdown("---")

# ---- INSTRUCCIONES ----
with st.expander("ℹ️ ¿Cómo funciona esta simulación?"):
    st.markdown("""
    Este simulador permite observar cómo se podrían propagar los incidentes **CON violencia** y **SIN violencia** en el Metro de la CDMX utilizando un modelo probabilístico de **cadenas de Markov**.  
    Puedes comparar tres escenarios distintos:

    - 🔵 **Escenario base**: sin intervención, solo datos históricos.
    - 👮‍♂️ **Con refuerzo policial**: policía fija en estaciones con más delitos.
    - 🚓 **Vigilancia móvil**: patrullas que se adaptan dinámicamente.

    Cada simulación genera una secuencia de estaciones, visualizada con un gráfico de barras.
    """)

# ---- CARGA DE MATRICES ----
matriz_violencia = cargar_matriz("matriz_transicion_violencia.csv")
matriz_violencia_refuerzo = cargar_matriz("matriz_transicion_violencia_refuerzo.csv")
matriz_violencia_refuerzo_b = cargar_matriz("matriz_violencia_refuerzo_b.csv")

matriz_sin_violencia = cargar_matriz("matriz_transicion_sin_violencia.csv")
matriz_sin_violencia_refuerzo = cargar_matriz("matriz_transicion_sin_violencia_refuerzo.csv")
matriz_sin_violencia_refuerzo_b = cargar_matriz("matriz_sin_violencia_refuerzo_b.csv")

# ---- ESTACIONES REFORZADAS ----
estaciones_media_alta_cv = [...]  # lista igual
estaciones_media_alta_sv = [...]  # lista igual

# ---- FUNCIONES ----
def simular_cadena_markov(P, estado_inicial, n_pasos):
    estados = [estado_inicial]
    for _ in range(n_pasos - 1):
        distribucion = P.loc[estados[-1]]
        siguiente = np.random.choice(distribucion.index, p=distribucion.values)
        estados.append(siguiente)
    return estados

def simular_cadena_markov_movil(P, estado_inicial, n_pasos, estaciones_refuerzo):
    estados = [estado_inicial]
    for _ in range(n_pasos - 1):
        distribucion = P.loc[estados[-1]].copy()
        for est in estaciones_refuerzo:
            if est in distribucion.index:
                distribucion[est] *= 0.5
        distribucion /= distribucion.sum()
        siguiente = np.random.choice(distribucion.index, p=distribucion.values)
        estados.append(siguiente)
    return estados

# ---- INTERFAZ USUARIO ----
col1, col2 = st.columns(2)
with col1:
    tipo_delito = st.radio("🎯 Tipo de incidente:", ["CON violencia", "SIN violencia"])
with col2:
    tipo_simulacion = st.radio("🛠️ Tipo de simulación:", ["Escenario base", "Con refuerzo policial", "Vigilancia móvil"])

estaciones_disponibles = (
    matriz_violencia.index.tolist() if tipo_delito == "CON violencia"
    else matriz_sin_violencia.index.tolist()
)

estacion_inicio = st.selectbox("📍 Estación de inicio:", estaciones_disponibles)
pasos = st.slider("🔁 Pasos a simular:", min_value=5, max_value=50, value=20)

# ---- SELECCIÓN DE MATRIZ Y FUNCIÓN ----
if tipo_delito == "CON violencia":
    if tipo_simulacion == "Escenario base":
        matriz, sim_func = matriz_violencia, simular_cadena_markov
    elif tipo_simulacion == "Con refuerzo policial":
        matriz, sim_func = matriz_violencia_refuerzo, simular_cadena_markov
    else:
        matriz, sim_func = matriz_violencia_refuerzo_b, simular_cadena_markov_movil
        refuerzo_estaciones = estaciones_media_alta_cv
else:
    if tipo_simulacion == "Escenario base":
        matriz, sim_func = matriz_sin_violencia, simular_cadena_markov
    elif tipo_simulacion == "Con refuerzo policial":
        matriz, sim_func = matriz_sin_violencia_refuerzo, simular_cadena_markov
    else:
        matriz, sim_func = matriz_sin_violencia_refuerzo_b, simular_cadena_markov_movil
        refuerzo_estaciones = estaciones_media_alta_sv

# ---- BOTÓN Y RESULTADOS ----
if st.button("🚦 Iniciar simulación"):
    secuencia = (
        sim_func(matriz, estacion_inicio, pasos, refuerzo_estaciones)
        if tipo_simulacion == "Vigilancia móvil" else
        sim_func(matriz, estacion_inicio, pasos)
    )

    st.success("✅ Simulación completada")
    st.markdown(f"### 📍 Ruta simulada ({pasos} pasos):")
    st.write(", ".join(secuencia))

    frecuencia = Counter(secuencia)
    estaciones, visitas = list(frecuencia.keys()), list(frecuencia.values())

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(estaciones, visitas, color='#00BFFF')
    ax.set_xticklabels(estaciones, rotation=90)
    ax.set_title("📊 Frecuencia de visitas a estaciones")
    st.pyplot(fig)

    st.info("**Interpretación:** Las estaciones con más visitas en la simulación podrían representar puntos críticos.")

    # ---- DESCARGA DE RESULTADOS ----
    csv = pd.DataFrame({'Paso': range(1, pasos + 1), 'Estación': secuencia})
    st.download_button(
        "⬇️ Descargar como CSV",
        data=csv.to_csv(index=False).encode('utf-8'),
        file_name="simulacion_metro.csv",
        mime="text/csv"
    )

# ---- PIE DE PÁGINA ----
st.markdown("---")
st.markdown("👩‍🔬 Desarrollado por estudiantes de Ciencia de Datos — LCDN 2025 🚇")
