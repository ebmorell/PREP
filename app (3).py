import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# Configuración general
st.set_page_config(page_title="Modelo de PrEP en VIH", layout="centered")
st.title("🧪 Simulador del impacto de la PrEP en VIH")
st.markdown("Comparación entre estrategias de profilaxis preexposición (PrEP) para reducir nuevas infecciones por VIH.")

# Parámetros generales de simulación
N = 10000
initial_infected = 100
days = 365
contact_rate = 0.5
trans_prob = 0.001  # Riesgo de transmisión por contacto sexual

# Escenarios definidos
scenarios = {
    "Sin PrEP": {
        "oral_coverage": 0, "oral_adherence": 0, "oral_efficacy": 0,
        "inj_coverage": 0, "inj_efficacy": 0
    },
    "PrEP oral": {
        "oral_coverage": 0.5, "oral_adherence": 0.8, "oral_efficacy": 0.95,
        "inj_coverage": 0, "inj_efficacy": 0
    },
    "Lenacapavir": {
        "oral_coverage": 0, "oral_adherence": 0, "oral_efficacy": 0,
        "inj_coverage": 0.5, "inj_efficacy": 0.96
    }
}

# Simulación
results_daily = {}
results_cumulative = {}

for name, params in scenarios.items():
    S = np.zeros(days)
    daily_new = np.zeros(days)
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
        new_inf = min(new_inf, S[t-1])  # evitar infecciones mayores que susceptibles

        daily_new[t] = new_inf
        I_cum[t] = I_cum[t-1] + new_inf
        S[t] = S[t-1] - new_inf

    results_daily[name] = daily_new
    results_cumulative[name] = I_cum

# Crear DataFrame con resultados
df_result = pd.DataFrame({
    "Día": np.arange(days),
    "Nuevas (Sin PrEP)": results_daily["Sin PrEP"],
    "Nuevas (PrEP oral)": results_daily["PrEP oral"],
    "Nuevas (Lenacapavir)": results_daily["Lenacapavir"],
    "Acumuladas (Sin PrEP)": results_cumulative["Sin PrEP"],
    "Acumuladas (PrEP oral)": results_cumulative["PrEP oral"],
    "Acumuladas (Lenacapavir)": results_cumulative["Lenacapavir"],
}).round(0).astype(int)

# Mostrar tabla completa
st.subheader("📊 Tabla de evolución diaria")
st.dataframe(df_result)

# Descargar como Excel
output = BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as writer:
    df_result.to_excel(writer, index=False, sheet_name='Resultados')
    writer.save()
    processed_data = output.getvalue()

st.download_button(
    label="📥 Descargar tabla como Excel",
    data=processed_data,
    file_name="simulacion_prep_vih.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Gráfica de nuevas infecciones diarias
st.subheader("📈 Nuevas infecciones por día")
fig1, ax1 = plt.subplots()
ax1.plot(df_result["Día"], df_result["Nuevas (Sin PrEP)"], label="Sin PrEP", linestyle="--")
ax1.plot(df_result["Día"], df_result["Nuevas (PrEP oral)"], label="PrEP oral")
ax1.plot(df_result["Día"], df_result["Nuevas (Lenacapavir)"], label="Lenacapavir")
ax1.set_xlabel("Días")
ax1.set_ylabel("Nuevas infecciones")
ax1.set_title("Nuevas infecciones diarias por VIH")
ax1.grid(True)
ax1.legend()
st.pyplot(fig1)

# Gráfica de infecciones acumuladas
st.subheader("🧮 Infecciones acumuladas")
fig2, ax2 = plt.subplots()
ax2.plot(df_result["Día"], df_result["Acumuladas (Sin PrEP)"], label="Sin PrEP", linestyle="--")
ax2.plot(df_result["Día"], df_result["Acumuladas (PrEP oral)"], label="PrEP oral")
ax2.plot(df_result["Día"], df_result["Acumuladas (Lenacapavir)"], label="Lenacapavir")
ax2.set_xlabel("Días")
ax2.set_ylabel("Total infectados")
ax2.set_title("Infecciones acumuladas por VIH")
ax2.grid(True)
ax2.legend()
st.pyplot(fig2)



