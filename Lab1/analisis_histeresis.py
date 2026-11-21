import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

nombre_csv = "medidas_histeresis.csv"
df = pd.read_csv(nombre_csv, delimiter=";")
df["ADC_Code"] = pd.to_numeric(df["ADC_Code"], errors="coerce")
df = df.dropna()

ida = df[df["Direccion"] == "Ida"].sort_values("V_Generador")
vuelta = df[df["Direccion"] == "Vuelta"].sort_values("V_Generador")

# Interpolación para comparar códigos en los mismos voltajes si hay ligero desajuste
v_comun = np.linspace(
    max(ida["V_Generador"].min(), vuelta["V_Generador"].min()),
    min(ida["V_Generador"].max(), vuelta["V_Generador"].max()),
    len(ida),
)
y_ida_interp = np.interp(v_comun, ida["V_Generador"], ida["ADC_Code"])
y_vuelta_interp = np.interp(v_comun, vuelta["V_Generador"], vuelta["ADC_Code"])
diff_histeresis = y_ida_interp - y_vuelta_interp

print("\n" + "=" * 50)
print("        RESULTADOS NUMÉRICOS - ENSAYO DE HISTÉRESIS   ")
print("=" * 50)
print(f" • Diferencia Máx. absoluta : {np.max(np.abs(diff_histeresis)):.3f} códigos")
print(f" • Diferencia Media absoluta: {np.mean(np.abs(diff_histeresis)):.3f} códigos")
print("=" * 50 + "\n")

plt.figure(figsize=(9, 6))
plt.plot(
    ida["V_Generador"],
    ida["ADC_Code"],
    "o-",
    color="royalblue",
    markersize=4,
    label="Ida (0V -> 5V)",
)
plt.plot(
    vuelta["V_Generador"],
    vuelta["ADC_Code"],
    "s--",
    color="darkorange",
    markersize=4,
    label="Vuelta (5V -> 0V)",
)
plt.title(
    "Ensayo de Histéresis (Barrido Bidireccional)",
    fontsize=13,
    fontweight="bold",
)
plt.xlabel("Tensión de Entrada (V)", fontsize=11)
plt.ylabel("Código ADC", fontsize=11)
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.tight_layout()
plt.savefig("histeresis_adc.png", dpi=300, bbox_inches="tight")
print("Guardada: 'histeresis_adc.png'")
plt.show()