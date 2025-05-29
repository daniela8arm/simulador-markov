import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

# --- Estilos CSS inyectados ---
st.markdown(
    """
    <style>
    /* Fondo general y fuente */
    .main {
        background: linear-gradient(135deg, #f0f8ff, #cde9ff);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #003366;
    }
    /* Título principal con sombra y padding */
    .title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #004080;
        text-shadow: 1px 1px 4px #a3c1ff;
        padding-bottom: 10px;
        margin-bottom: 10px;
        border-bottom: 2px solid #004080;
    }
    /* Botón con fondo azul y efecto hover */
    div.stButton > button:first-child {
        background-color: #0078d7;
        color: white;
        border-radius: 10px;
        height: 3em;
        width: 100%;
        font-size: 1.1rem;
        font-weight: 600;
        transition: background-color 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #005a9e;
        color: #d1e7ff;
    }
    /* Subtítulos */
    h3 {
        color: #004080;
    }
    /* Labels y radios */
    label, div[role="radiogroup"] {
        font-size: 1.1rem;
        font-weight: 600;
        color: #002244;
    }
    /* Scroll barras de gráfico */
    .stPlotlyChart > div {
        overflow-x: auto;
    }
    /* Footer */
    footer {
        font-size: 0.8rem;
        color: #666666;
        padding: 10px;
        text-align: center;
        border-top: 1px solid #cccccc;
        margin-top: 30px;
    }
    </style>
    """, unsafe_allow_html=True
)

# --- Título principal ---
st.markdown('<div class="title">🚇 Simulador de Delitos en el Metro CDMX con Cadenas de Markov</div>', unsafe_allow_html=True)
st.markdown("---")

# --- Instrucciones ---
st.markdown('''
Este simulador muestra cómo podrían evolucionar los incidentes delictivos **CON violencia** y **SIN violencia** en el Metro de la CDMX a través de cadenas de Markov.
Puedes comparar distintos escenarios:

🔵 **Escenario base:** Movimiento natural de incidentes según datos históricos.

👮‍♂️ **Con refuerzo policial:** Vigilancia fija en estaciones críticas.

🚓 **Vigilancia móvil:** Policía se desplaza anticipando zonas de riesgo.

🧠 El modelo genera secuencias basadas en la matriz de transición de Markov.
''')

# --- Función para cargar matrices ---
@st.cache_data
def cargar_matriz(nombre_archivo):
    return pd.read_csv(nombre_archivo, index_col=0)

# Carga matrices
matriz_violencia = cargar_matriz("matriz_transicion_violencia.csv")
matriz_violencia_refuerzo = cargar_matriz("matriz_transicion_violencia_refuerzo.csv")
matriz_violencia_refuerzo_b = cargar_matriz("matriz_violencia_refuerzo_b.csv")
matriz_sin_violencia = cargar_matriz("matriz_transicion_sin_violencia.csv")
matriz_sin_violencia_refuerzo = cargar_matriz("matriz_transicion_sin_violencia_refuerzo.csv")
matriz_sin_violencia_refuerzo_b = cargar_matriz("matriz_sin_violencia_refuerzo_b.csv")

estaciones_media_alta_cv = ['Agrícola Oriental', 'Allende', 'Apatlaco', 'Auditorio', 'Balbuena', 'Buenavista', 'Centro Médico', 'Cerro de la Estrella', 'Chilpancingo', 'Ciudad Deportiva', 'Constitución de 1917', 'División del Norte', 'Fray Servando', 'General Anaya', 'Insurgentes', 'Moctezuma', 'Observatorio', 'Potrero', 'Puebla', 'Refinería', 'Revolución', 'Ricardo Flores Magón', 'Santa Anita', 'Tasqueña', 'Tepalcates', 'Vallejo', 'Villa de Aragón', 'Xola']
estaciones_media_alta_sv = ['Barranca del Muerto', 'Camarones', 'Chapultepec', 'Copilco', 'Coyoacán', 'Coyuya', 'División del Norte', 'Gomez Farías', 'Guelatao', 'Instituto del Petróleo', 'Insurgentes Sur', 'Isabel La Católica', 'Iztacalco', 'Jamaica', 'Juárez', 'Lagunilla', 'Martín Carrera', 'Miguel Ángel de Quevedo', 'Moctezuma', 'Morelos', 'Nativitas', 'Normal', 'Observatorio', 'Portales', 'Puebla', 'San Joaquín', 'San Juan de Letrán', 'San Pedro de Los Pinos', 'Sevilla', 'Tepalcates', 'Tlatelolco', 'Universidad', 'Viaducto', 'Villa de Aragón', 'Xola', 'Zaragoza']

def simular_cadena_markov(P, estado_inicial, n_pasos):
    estados = [estado_inicial]
    for _ in range(n_pasos - 1):
        estado_actual = estados[-1]
        distribucion = P.loc[estado_actual]
        siguiente_estado = np.random.choice(distribucion.index, p=distribucion.values)
        estados.append(siguiente_estado)
    return estados

def simular_cadena_markov_movil(P, estado_inicial, n_pasos, estaciones_refuerzo):
    estados = [estado_inicial]
    for _ in range(n_pasos - 1):
        estado_actual = estados[-1]
        distribucion = P.loc[estado_actual].copy()
        for est in estaciones_refuerzo:
            if est in distribucion.index:
                distribucion[est] *= 0.5
        distribucion /= distribucion.sum()
        siguiente_estado = np.random.choice(distribucion.index, p=distribucion.values)
        estados.append(siguiente_estado)
    return estados

# --- Layout en columnas ---
col1, col2 = st.columns([1, 2])

with col1:
    tipo_delito = st.radio("**Selecciona tipo de incidente:**", ["CON violencia", "SIN violencia"])
    tipo_simulacion = st.radio("**Selecciona tipo de simulación:**", ["Escenario base", "Con refuerzo policial", "Vigilancia móvil"])

    if tipo_delito == "CON violencia":
        estaciones_disponibles = matriz_violencia.index.tolist()
    else:
        estaciones_disponibles = matriz_sin_violencia.index.tolist()

    estacion_inicio = st.selectbox("📍 Estación de inicio:", estaciones_disponibles)
    pasos = st.slider("🔢 Número de pasos a simular:", min_value=5, max_value=50, value=20)

    # Selección de matriz y función
    if tipo_delito == "CON violencia":
        if tipo_simulacion == "Escenario base":
            matriz = matriz_violencia
            sim_func = simular_cadena_markov
        elif tipo_simulacion == "Con refuerzo policial":
            matriz = matriz_violencia_refuerzo
            sim_func = simular_cadena_markov
        else:
            matriz = matriz_violencia_refuerzo_b
            sim_func = simular_cadena_markov_movil
            refuerzo_estaciones = estaciones_media_alta_cv
    else:
        if tipo_simulacion == "Escenario base":
            matriz = matriz_sin_violencia
            sim_func = simular_cadena_markov
        elif tipo_simulacion == "Con refuerzo policial":
            matriz = matriz_sin_violencia_refuerzo
            sim_func = simular_cadena_markov
        else:
            matriz = matriz_sin_violencia_refuerzo_b
            sim_func = simular_cadena_markov_movil
            refuerzo_estaciones = estaciones_media_alta_sv

    simular = st.button("Simular")

with col2:
    if 'simular' in locals() and simular:
        if tipo_simulacion == "Vigilancia móvil":
            secuencia = sim_func(matriz, estacion_inicio, pasos, refuerzo_estaciones)
        else:
            secuencia = sim_func(matriz, estacion_inicio, pasos)

        st.markdown(f"### 🔄 Simulación: {tipo_delito} - {tipo_simulacion}")
        for i, est in enumerate(secuencia, 1):
            st.write(f"{i}: {est}")

        frecuencia = Counter(secuencia)
        estaciones = list(frecuencia.keys())
        visitas = list(frecuencia.values())

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(estaciones, visitas, color='#0078d7')
        ax.set_xticks(range(len(estaciones)))
        ax.set_xticklabels(estaciones, rotation=90)
        ax.set_xlabel("Estación")
        ax.set_ylabel("Número de visitas")
        ax.set_title("Frecuencia de estaciones visitadas en la simulación")
        st.pyplot(fig)

        st.markdown('''
        **Interpretación:**

        - Esta simulación muestra la trayectoria posible de incidentes en el Metro según la matriz seleccionada.
        - Las barras indican qué estaciones son más visitadas o con mayor probabilidad en la trayectoria.
        - En vigilancia móvil, la probabilidad en estaciones reforzadas se reduce, cambiando la trayectoria.
        ''')

        csv = pd.DataFrame({'Paso': range(1, pasos + 1), 'Estación': secuencia})
        csv_file = csv.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Descargar secuencia como CSV",
            data=csv_file,
            file_name="simulacion_metro.csv",
            mime="text/csv"
        )

st.markdown("---")
st.markdown('<footer>📊 <b>Simulación desarrollada por estudiantes LCDN</b> — Ciencia de Datos, Metro CDMX 2025 🚇</footer>', unsafe_allow_html=True)
