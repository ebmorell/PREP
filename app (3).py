import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Simulador de PrEP", layout="centered")
st.title("🧪 Simulador del impacto de la PrEP (oral vs. lenacapavir)")
st.markdown("Este simulador estima la reducción de nuevas infecciones por VIH según la estrategia de profilaxis preexposición (PrEP) empleada.")

# Parámetros definidos por el usuario
N = st.number_input("Población total", min_value=1000, max_value=1000000, value=10000, step=1000)
days = st.slider("Duración del seguimiento (días)", 30, 1095, value=365, step=30)
initial_infected = st.slider("Infectados iniciales", 0, N, value=100, step=10)
contact_rate = st.slider("Contactos sexuales por persona y día", 0.1, 3.0, value=0.5, step=0.1)

st.markdown("### 🧬 Supuestos del modelo")
st.info(
    "📌 El riesgo de transmisión por contacto sexual se fija en un **0,1 % por acto sexual** (basado en relaciones anales receptivas sin protección), "
    "en línea con los datos de referencia de los CDC y la OMS. Este valor es fijo en la simulación actual.",
    icon="ℹ️"
)
# Riesgo de transmisión por contacto (0.1%)
trans_prob = 0.001

st.markdown("### 💊 Parámetros de PrEP oral")
oral_coverage = st.slider("Cobertura poblacional PrEP oral", 0.0, 1.0, 0.5)
oral_adherence = st.slider("Adherencia media PrEP oral", 0.0, 1.0, 0.8)
oral_efficacy = st.slider("Eficacia de PrEP oral con buena adherencia", 0.0, 1.0, 0.95)

st.markdown("### 💉 Parámetros de lenacapavir")
inj_coverage = st.slider("Cobertura poblacional lenacapavir", 0.0, 1.0, 0.5)
inj_efficacy = st.slider("Eficacia de lenacapavir", 0.0, 1.0, 0.96)

# Diccionario de escenarios
scenarios = {
    "Sin PrEP": {
        "oral_coverage": 0.0, "oral_adherence": 0.0, "oral_efficacy": 0.0,
        "inj_coverage": 0.0, "inj_efficacy": 0.0
    },
    "PrEP oral": {
        "oral_coverage": oral_coverage, "oral_adherence": oral_adherence, "oral_efficacy": oral_efficacy,
        "inj_coverage": 0.0, "inj_efficacy": 0.0
    },
    "Lenacapavir": {
        "oral_coverage": 0.0, "oral_adherence": 0.0, "oral_efficacy": 0.0,
        "inj_coverage": inj_coverage, "inj_efficacy": inj_efficacy
    }
}

# Simulación
results_cumulative = {}

for name, params in scenarios.items():
    S = np.zeros(days)
    I_cum = np.zeros(days)

    S[0] = N - initial_infected
    I_cum[0] = initial_infected

    for t in range(1, days):
        protection = (
            params["oral_efficacy"] * params["oral_adherence"] * params["oral_coverage"] +
            params["inj_efficacy"] * params["inj_coverage"]
        )
        beta_eff = (contact_rate * trans_prob) * (1 - protection) / N

        new_inf = beta_eff * S[t-1] * I_cum[t-1]
        new_inf = min(new_inf, S[t-1])

        I_cum[t] = I_cum[t-1] + new_inf
        S[t] = S[t-1] - new_inf

    results_cumulative[name] = I_cum

# Crear DataFrame con resultados
df_result = pd.DataFrame({
    "Día": np.arange(days),
    "Infectados acumulados (Sin PrEP)": results_cumulative["Sin PrEP"],
    "Infectados acumulados (PrEP oral)": results_cumulative["PrEP oral"],
    "Infectados acumulados (Lenacapavir)": results_cumulative["Lenacapavir"],
}).round(0).astype(int)

# Mostrar tabla
st.subheader("📊 Evolución de infecciones acumuladas por estrategia")
st.dataframe(df_result)

# Descargar Excel
output = BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as writer:
    df_result.to_excel(writer, index=False, sheet_name='Resultados')

st.download_button(
    label="📥 Descargar resultados como Excel",
    data=output.getvalue(),
    file_name="simulacion_prep_vih.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Gráfica de infecciones acumuladas
st.subheader("📉 Infecciones acumuladas")
fig, ax = plt.subplots()
ax.plot(df_result["Día"], df_result["Infectados acumulados (Sin PrEP)"], label="Sin PrEP", linestyle="--")
ax.plot(df_result["Día"], df_result["Infectados acumulados (PrEP oral)"], label="PrEP oral")
ax.plot(df_result["Día"], df_result["Infectados acumulados (Lenacapavir)"], label="Lenacapavir")
ax.set_xlabel("Días")
ax.set_ylabel("Infectados acumulados")
ax.set_title("Reducción de nuevas infecciones por VIH")
ax.grid(True)
ax.legend()
st.pyplot(fig)


