
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Título principal
st.title("🚇 Simulador de Delitos en el Metro CDMX con Cadenas de Markov")

# Instrucciones
st.markdown('''
Este simulador muestra cómo podrían evolucionar los incidentes delictivos CON violencia y SIN violencia en el Metro de la CDMX a través de cadenas de Markov.
Selecciona entre distintos escenarios de simulación:

🔹 **Escenario base:** Representa el comportamiento natural de los trayectos basados solo en datos de incidentes.
🔹 **Con refuerzo policial:** Simula qué pasaría si la policía fija vigilancia en estaciones muy peligrosas.
🔹 **Vigilancia móvil:** Simula una estrategia que anticipa zonas de riesgo antes de que empeoren.

El modelo generará una secuencia de estaciones basada en una cadena de Markov.

''')

#Cargar datos (matrices)
    
