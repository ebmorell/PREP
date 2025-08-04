st.subheader("📊 Comparación de estrategias de PrEP (nuevas infecciones y acumuladas)")

scenarios = {
    "Sin PrEP": {"oral_coverage": 0, "oral_adherence": 0, "oral_efficacy": 0, "inj_coverage": 0, "inj_efficacy": 0},
    "PrEP oral": {"oral_coverage": 0.5, "oral_adherence": 0.8, "oral_efficacy": 0.95, "inj_coverage": 0, "inj_efficacy": 0},
    "Lenacapavir": {"oral_coverage": 0, "oral_adherence": 0, "oral_efficacy": 0, "inj_coverage": 0.5, "inj_efficacy": 0.96}
}

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

# Crear DataFrame para tabla
df_result = pd.DataFrame({
    "Día": np.arange(days),
    "Nuevas (Sin PrEP)": results_daily["Sin PrEP"],
    "Nuevas (PrEP oral)": results_daily["PrEP oral"],
    "Nuevas (Lenacapavir)": results_daily["Lenacapavir"],
    "Acumuladas (Sin PrEP)": results_cumulative["Sin PrEP"],
    "Acumuladas (PrEP oral)": results_cumulative["PrEP oral"],
    "Acumuladas (Lenacapavir)": results_cumulative["Lenacapavir"],
}).round(0).astype(int)

# Mostrar tabla
st.markdown("### 📄 Evolución diaria de nuevas y acumuladas")
st.dataframe(df_result)

# Gráfica de nuevas infecciones diarias
st.markdown("### 📈 Nuevas infecciones diarias por estrategia")
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

# Gráfica de acumuladas
st.markdown("### 🧮 Infecciones acumuladas por estrategia")
fig2, ax2 = plt.subplots()
ax2.plot(df_result["Día"], df_result["Acumuladas (Sin PrEP)"], label="Sin PrEP", linestyle="--")
ax2.plot(df_result["Día"], df_result["Acumuladas (PrEP oral)"], label="PrEP oral")
ax2.plot(df_result["Día"], df_result["Acumuladas (Lenacapavir)"], label="Lenacapavir")
ax2.set_xlabel("Días")
ax2.set_ylabel("Infectados acumulados")
ax2.set_title("Infecciones acumuladas por VIH")
ax2.grid(True)
ax2.legend()
st.pyplot(fig2)

# Descargar CSV
csv = df_result.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Descargar tabla como CSV",
    data=csv,
    file_name='simulacion_prep_vih.csv',
    mime='text/csv'
)

