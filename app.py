app_code = """
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

# Título principal
st.title("🚇 Simulador de Delitos en el Metro CDMX con Cadenas de Markov")

# Instrucciones
st.markdown('''
Este simulador muestra cómo podrían evolucionar los incidentes delictivos CON violencia y SIN violencia en el Metro de la CDMX a través de cadenas de Markov.
Puedes comparar distintos escenarios:

🔹 **Escenario base:** Representa el comportamiento natural de los trayectos basados solo en datos de incidentes.  
🔹 **Con refuerzo policial:** Simula qué pasaría si la policía fija vigilancia en estaciones muy peligrosas.  
🔹 **Vigilancia móvil:** Simula una estrategia que anticipa zonas de riesgo antes de que empeoren.  

El modelo generará una secuencia de estaciones basada en una cadena de Markov.
''')

# Cargar matrices
matriz_violencia = pd.read_csv("matriz_transicion_violencia.csv", index_col=0)
matriz_violencia_refuerzo = pd.read_csv("matriz_transicion_violencia_refuerzo.csv", index_col=0)
matriz_violencia_refuerzo_b = pd.read_csv("matriz_violencia_refuerzo_b.csv", index_col=0)

matriz_sin_violencia = pd.read_csv("matriz_transicion_sin_violencia.csv", index_col=0)
matriz_sin_violencia_refuerzo = pd.read_csv("matriz_transicion_sin_violencia_refuerzo.csv", index_col=0)
matriz_sin_violencia_refuerzo_b = pd.read_csv("matriz_sin_violencia_refuerzo_b.csv", index_col=0)

# Puedes modificar estas listas con las estaciones reales que tengan media/alta peligrosidad
estaciones_media_alta_cv = ['Agrícola Oriental', 'Allende', 'Apatlaco', 'Auditorio', 'Balbuena', 'Buenavista', 'Centro Médico', 'Cerro de la Estrella', 'Chilpancingo', 'Ciudad Deportiva', 'Constitución de 1917', 'División del Norte', 'Fray Servando', 'General Anaya', 'Insurgentes', 'Moctezuma', 'Observatorio', 'Potrero', 'Puebla', 'Refinería', 'Revolución', 'Ricardo Flores Magón', 'Santa Anita', 'Tasqueña', 'Tepalcates', 'Vallejo', 'Villa de Aragón', 'Xola']
estaciones_media_alta_sv = ['Barranca del Muerto', 'Camarones', 'Chapultepec', 'Copilco', 'Coyoacán', 'Coyuya', 'División del Norte', 'Gomez Farías', 'Guelatao', 'Instituto del Petróleo', 'Insurgentes Sur', 'Isabel La Católica', 'Iztacalco', 'Jamaica', 'Juárez', 'Lagunilla', 'Martín Carrera', 'Miguel Ángel de Quevedo', 'Moctezuma', 'Morelos', 'Nativitas', 'Normal', 'Observatorio', 'Portales', 'Puebla', 'San Joaquín', 'San Juan de Letrán', 'San Pedro de Los Pinos', 'Sevilla', 'Tepalcates', 'Tlatelolco', 'Universidad', 'Viaducto', 'Villa de Aragón', 'Xola', 'Zaragoza']

# Funciones de simulación
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

# Interfaz de usuario
tipo_delito = st.radio("Selecciona el tipo de incidente:", ["CON violencia", "SIN violencia"])
tipo_simulacion = st.radio("Selecciona el tipo de simulación:", ["Escenario base", "Con refuerzo policial", "Vigilancia móvil"])

if tipo_delito == "CON violencia":
    estaciones_disponibles = matriz_violencia.index.tolist()
else:
    estaciones_disponibles = matriz_sin_violencia.index.tolist()

estacion_inicio = st.selectbox("📍 Selecciona estación de inicio:", estaciones_disponibles)
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

# Simulación al presionar botón
if st.button("Simular"):
    if tipo_simulacion == "Vigilancia móvil":
        secuencia = sim_func(matriz, estacion_inicio, pasos, refuerzo_estaciones)
    else:
        secuencia = sim_func(matriz, estacion_inicio, pasos)

    st.write(f"### 🔄 Simulación: {tipo_delito} - {tipo_simulacion}")
    for i, est in enumerate(secuencia, 1):
        st.write(f"{i}: {est}")

    frecuencia = Counter(secuencia)
    estaciones = list(frecuencia.keys())
    visitas = list(frecuencia.values())

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(estaciones, visitas, color='darkgreen')
    ax.set_xticks(range(len(estaciones)))
    ax.set_xticklabels(estaciones, rotation=90)
    ax.set_xlabel("Estación")
    ax.set_ylabel("Número de visitas")
    ax.set_title("Frecuencia de estaciones visitadas en la simulación")
    st.pyplot(fig)

    st.markdown('''
    **Interpretación:**

    - Esta simulación muestra la trayectoria posible de incidentes en el Metro según la matriz seleccionada.
    - Las barras indican qué estaciones son más visitadas o con mayor probabilidad en el recorrido.
    - En el caso de vigilancia móvil, la probabilidad de visitar estaciones reforzadas se reduce, cambiando la trayectoria.
    ''')
# Descarga como CSV
csv = pd.DataFrame({'Paso': range(1, pasos + 1), 'Estación': secuencia})
csv_file = csv.to_csv(index=False).encode('utf-8')
st.download_button(
    label="⬇️ Descargar secuencia como CSV",
    data=csv_file,
    file_name="simulacion_metro.csv",
    mime="text/csv"
)

"""
