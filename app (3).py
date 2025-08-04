import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# Funciones de eficacia
def efficacy_prep_oral(adherence):
    if adherence >= 0.9:
        return 0.99
    elif adherence >= 0.7:
        return 0.90
    elif adherence >= 0.5:
        return 0.70
    elif adherence >= 0.3:
        return 0.50
    else:
        return 0.30

def efficacy_lenacapavir(adherence):
    if adherence >= 0.95:
        return 0.98
    elif adherence >= 0.8:
        return 0.95
    elif adherence >= 0.6:
        return 0.90
    else:
        return 0.85

# Página
st.set_page_config(page_title="Simulador PrEP VIH", layout="centered")
st.title("🧪 Simulador de PrEP (oral vs lenacapavir) en VIH")
st.markdown("Simula nuevas infecciones por VIH según tipo de relación sexual, cobertura y adherencia.")

# Parámetros generales
N = st.number_input("Población en riesgo (personas)", 1000, 100000, value=10000)
days = st.slider("Días de simulación", 30, 1095, value=365)
initial_infected = st.slider("Personas VIH+ al inicio", 0, N, value=100)
contact_rate = st.slider("Contactos sexuales por persona/día", 0.1, 5.0, value=0.5)

tipo_relacion = st.selectbox("Tipo de relación sexual", {
    "Receptivo anal (sin condón)": 0.0138,
    "Insertivo anal (sin condón)": 0.0011,
    "Vaginal receptiva": 0.0008,
    "Vaginal insertiva": 0.0004
})
trans_prob = {
    "Receptivo anal (sin condón)": 0.0138,
    "Insertivo anal (sin condón)": 0.0011,
    "Vaginal receptiva": 0.0008,
    "Vaginal insertiva": 0.0004
}[tipo_relacion]

# PrEP oral
st.subheader("💊 PrEP oral")
coverage_oral = st.slider("Cobertura oral (%)", 0.0, 1.0, 0.5)
adherence_oral = st.slider("Adherencia oral (%)", 0.0, 1.0, 0.8)
eff_oral = efficacy_prep_oral(adherence_oral)

# Lenacapavir
st.subheader("💉 Lenacapavir")
coverage_len = st.slider("Cobertura lenacapavir (%)", 0.0, 1.0, 0.2)
adherence_len = st.slider("Adherencia lenacapavir (%)", 0.0, 1.0, 0.9)
eff_len = efficacy_lenacapavir(adherence_len)

# Simulación
t = np.arange(0, days)
new_infections = []
cum_infections = []

S = np.zeros(days)
I = np.zeros(days)
S[0] = N - initial_infected
I[0] = initial_infected

for i in range(1, days):
    protected_oral = coverage_oral * eff_oral
    protected_len = coverage_len * eff_len
    unprotected = 1 - protected_oral - protected_len
    beta_eff = trans_prob * unprotected * (I[i-1] / N)

    new_inf = beta_eff * S[i-1]
    new_infections.append(new_inf)
    cum_infections.append(sum(new_infections))

    S[i] = max(S[i-1] - new_inf, 0)
    I[i] = I[i-1] + new_inf

# Resultados
df = pd.DataFrame({
    "Día": t[1:],
    "Nuevas infecciones": new_infections,
    "Infecciones acumuladas": cum_infections
})

st.subheader("📈 Infecciones acumuladas")
fig, ax = plt.subplots()
ax.plot(df["Día"], df["Infecciones acumuladas"], color="crimson")
ax.set_xlabel("Días")
ax.set_ylabel("Casos acumulados")
ax.set_title("Evolución acumulada de nuevas infecciones")
ax.grid(True)
st.pyplot(fig)

st.subheader("📋 Tabla completa de simulación")
st.dataframe(df)

# Descargar Excel
output = BytesIO()
with pd.ExcelWriter(output, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="Simulación")
st.download_button(
    label="📥 Descargar Excel",
    data=output.getvalue(),
    file_name="simulacion_vih_prep.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


