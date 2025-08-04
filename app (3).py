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
# 🔁 Comparación entre estrategias (tabla y gráfico)
st.subheader("📊 Comparación de estrategias de PrEP")

scenarios = {
    "Sin PrEP": {"oral_coverage": 0, "oral_adherence": 0, "oral_efficacy": 0, "inj_coverage": 0, "inj_efficacy": 0},
    "PrEP oral": {"oral_coverage": 0.5, "oral_adherence": 0.8, "oral_efficacy": 0.95, "inj_coverage": 0, "inj_efficacy": 0},
    "Lenacapavir": {"oral_coverage": 0, "oral_adherence": 0, "oral_efficacy": 0, "inj_coverage": 0.5, "inj_efficacy": 0.96}
}

results = {}

for name, params in scenarios.items():
    S = np.zeros(days)
    I = np.zeros(days)
    S[0] = N - initial_infected
    I[0] = initial_infected

    for t in range(1, days):
        beta_eff = (contact_rate * trans_prob) * (1 - (
            params["oral_efficacy"] * params["oral_adherence"] * params["oral_coverage"] +
            params["inj_efficacy"] * params["inj_coverage"]
        )) / N

        new_infections = beta_eff * S[t-1] * I[t-1]
        recoveries = gamma * I[t-1]

        S[t] = S[t-1] - new_infections
        I[t] = I[t-1] + new_infections - recoveries

    results[name] = I

# Crear tabla de comparación
df_compare = pd.DataFrame({
    "Día": np.arange(days),
    "Sin PrEP": results["Sin PrEP"],
    "PrEP oral": results["PrEP oral"],
    "Lenacapavir": results["Lenacapavir"]
})

st.markdown("### 📉 Evolución de infectados según estrategia")
fig2, ax2 = plt.subplots()
ax2.plot(df_compare["Día"], df_compare["Sin PrEP"], label="Sin PrEP", linestyle="--")
ax2.plot(df_compare["Día"], df_compare["PrEP oral"], label="PrEP oral")
ax2.plot(df_compare["Día"], df_compare["Lenacapavir"], label="Lenacapavir")
ax2.set_xlabel("Días")
ax2.set_ylabel("Infectados")
ax2.set_title("Comparación de estrategias de prevención")
ax2.grid(True)
ax2.legend()
st.pyplot(fig2)

# Tabla final de comparación
st.markdown("### 📄 Tabla final (últimos 10 días)")
df_final = df_compare.tail(10).round(0).astype(int)
st.dataframe(df_final)

