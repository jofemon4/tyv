import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 1. Cargar datos del CSV
nombre_csv = "medidas_adc_arduino.csv"
print(f"Leyendo datos desde '{nombre_csv}'...")
df = pd.read_csv(nombre_csv, delimiter=";")
df["ADC_Code"] = pd.to_numeric(df["ADC_Code"], errors="coerce")
df = df.dropna()

x = df["V_Generador"].values
y = df["ADC_Code"].values

# 2. Regresión Lineal (Ganancia y Offset)
pendiente, intercepto = np.polyfit(x, y, 1)
y_ideal = pendiente * x + intercepto

# 3. Cálculo de INL (Integral Non-Linearity)
# El INL se calcula como la diferencia entre el valor real y el ideal, expresado en LSBs
# LSB ideal en términos de voltaje o códigos
inl = (y - y_ideal) / pendiente  # Convertido a equivalencia en voltios / LSB

# 4. Cálculo de DNL (Differential Non-Linearity)
# Obtenemos el ancho de cada código encontrando el cambio de voltaje medio por cada código
codigos_unicos = np.unique(y)
anchos_codigo = []
codigos_validos = []

for c in range(int(min(codigos_unicos)), int(max(codigos_unicos))):
  mask = y == c
  if np.sum(mask) > 1:
    v_asociados = x[mask]
    ancho = np.max(v_asociados) - np.min(v_asociados)
    if ancho > 0:
      anchos_codigo.append(ancho)
      codigos_validos.append(c)

if len(anchos_codigo) > 0:
  ancho_ideal = 1.0 / pendiente
  dnl = (np.array(anchos_codigo) - ancho_ideal) / ancho_ideal
else:
  dnl = np.array([0])
  codigos_validos = [0]

# --- 5. GENERACIÓN DE GRÁFICAS MULTIPANEL ---
fig, axs = plt.subplots(2, 2, figsize=(14, 10))

# Gráfica 1: Función de Transferencia y Ajuste Lineal
axs[0, 0].scatter(x, y, color="blue", s=5, alpha=0.5, label="Datos Medidos")
axs[0, 0].plot(x, y_ideal, color="red", linestyle="--", label="Ajuste Ideal")
axs[0, 0].setTitle("1. Función de Transferencia")
axs[0, 0].set_xlabel("Tensión de Entrada (V)")
axs[0, 0].set_ylabel("Código ADC")
axs[0, 0].grid(True, linestyle="--", alpha=0.6)
axs[0, 0].legend(loc="upper left")

# Gráfica 2: INL (Non-Linearity Integral)
axs[0, 1].plot(x, inl, color="purple", linewidth=1.5)
axs[0, 1].set_title("2. INL (Integral Non-Linearity)")
axs[0, 1].set_xlabel("Tensión de Entrada (V)")
axs[0, 1].set_ylabel("Error INL (LSB)")
axs[0, 1].grid(True, linestyle="--", alpha=0.6)

# Gráfica 3: DNL (Differential Non-Linearity)
axs[1, 0].plot(
    codigos_validos, dnl, color="green", linewidth=1, marker=".", markersize=2
)
axs[1, 0].set_title("3. DNL (Differential Non-Linearity)")
axs[1, 0].set_xlabel("Código ADC")
axs[1, 0].set_ylabel("Error DNL (LSB)")
axs[1, 0].grid(True, linestyle="--", alpha=0.6)
axs[1, 0].axhline(0, color="black", linewidth=0.8, linestyle="--")

# Gráfica 4: Resumen Estadístico Textual
axs[1, 1].axis("off")
texto_resumen = (
    f"RESUMEN DE CARACTERIZACIÓN ADC:\n\n"
    f" • Ganancia (Pendiente): {pendiente:.4f} códigos/V\n"
    f" • Error de Offset: {intercepto:.4f} códigos\n"
    f" • INL Máximo: {np.max(np.abs(inl)):.3f} LSB\n"
    f" • DNL Máximo: {np.max(np.abs(dnl)):.3f} LSB\n"
    f" • Rango analizado: {len(df)} muestras"
)
axs[1, 1].text(
    0.1,
    0.5,
    texto_resumen,
    fontsize=12,
    family="monospace",
    bbox=dict(boxstyle="round,pad=1", facecolor="wheat", alpha=0.5),
)

plt.tight_layout()
plt.savefig("caracterizacion_adc_completa.png", dpi=300, bbox_inches="tight")
print(
    "Informe gráfico guardado con éxito como 'caracterizacion_adc_completa.png'."
)
plt.show()