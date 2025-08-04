import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Configuración inicial
st.set_page_config(page_title="Simulador de PrEP vs. VIH", layout="centered")
st.title("🧪 Simulador del impacto de la PrEP en la transmisión del VIH")
st.markdown("""
Este modelo permite explorar el impacto de diferentes niveles de cobertura, adherencia y eficacia de la PrEP oral y la PrEP con lenacapavir
en la incidencia de nuevas infecciones por VIH.
""")

# Parámetros generales
N = st.slider("Tamaño poblacional (personas en riesgo)", 1000, 100000, 10000)
days = st.slider("Duración de la simulación (días)", 30, 730, 365)
initial_infected = st.slider("Número inicial de infectados", 0, N, 100)

contact_rate = st.slider("Contactos sexuales por persona por día", 0.1, 5.0, 0.5)
trans_prob = st.slider("Probabilidad de transmisión por contacto", 0.0001, 0.01, 0.001)

gamma = 1 / 180  # Tasa de salida de infectados (media 6 meses)

st.subheader("💊 Parámetros de PrEP oral")
oral_coverage = st.slider("Cobertura de PrEP oral (%)", 0, 100, 50) / 100
oral_adherence = st.slider("Adherencia a PrEP oral (%)", 0, 100, 80) / 100
oral_efficacy = st.select_slider("Eficacia estimada según adherencia", options=[0.70, 0.85, 0.95, 1.00], value=0.95)

st.subheader("💉 Parámetros de PrEP inyectable (lenacapavir)")
inj_coverage = st.slider("Cobertura de lenacapavir (%)", 0, 100, 30) / 100
inj_efficacy = st.select_slider("Eficacia de lenacapavir", options=[0.96, 0.98, 1.00], value=0.96)

# Simulación
S = np.zeros(days)
I = np.zeros(days)
S[0] = N - initial_infected
I[0] = initial_infected

for t in range(1, days):
    beta_eff = (contact_rate * trans_prob) * (1 - (
        oral_efficacy * oral_adherence * oral_coverage +
        inj_efficacy * inj_coverage
    )) / N

    new_infections = beta_eff * S[t-1] * I[t-1]
    recoveries = gamma * I[t-1]

    S[t] = S[t-1] - new_infections
    I[t] = I[t-1] + new_infections - recoveries

# Gráfica
st.subheader("📈 Evolución diaria de infectados")
fig, ax = plt.subplots()
ax.plot(np.arange(days), I, label="Infectados", color="red")
ax.plot(np.arange(days), S, label="Susceptibles", color="green")
ax.set_xlabel("Días")
ax.set_ylabel("Personas")
ax.set_title("Evolución de la transmisión del VIH")
ax.grid(True)
ax.legend()
st.pyplot(fig)

# Tabla resumen
st.subheader("📊 Resumen final")
summary_df = pd.DataFrame({
    "Día": np.arange(days),
    "Infectados": I.astype(int),
    "Susceptibles": S.astype(int)
})
st.dataframe(summary_df.tail(10))

