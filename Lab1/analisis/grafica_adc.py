from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT_DIR = Path(__file__).resolve().parent.parent / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)
csv_entrada = OUT_DIR / "medidas_adc_arduino.csv"

df = pd.read_csv(csv_entrada, delimiter=";")
df["ADC_Code"] = pd.to_numeric(df["ADC_Code"], errors="coerce")
df = df.dropna()

x = df["V_Generador"].values
y = df["ADC_Code"].values

pendiente, intercepto = np.polyfit(x, y, 1)
y_ideal = pendiente * x + intercepto

ss_res = np.sum((y - y_ideal) ** 2)
ss_tot = np.sum((y - np.mean(y)) ** 2)
r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 1.0

inl = y - y_ideal

codigos_unicos = np.unique(y)
anchos_codigo = []
codigos_validos = []

for c in range(int(np.min(codigos_unicos)), int(np.max(codigos_unicos))):
  mask = y == c
  if np.sum(mask) > 1:
    v_asociados = x[mask]
    ancho = np.max(v_asociados) - np.min(v_asociados)
    if ancho > 0:
      anchos_codigo.append(ancho)
      codigos_validos.append(c)

if anchos_codigo:
  ancho_ideal = 1.0 / pendiente
  dnl = (np.array(anchos_codigo) - ancho_ideal) / ancho_ideal
else:
  dnl = np.array([0.0])
  codigos_validos = [0]

print("\n" + "=" * 52)
print("       RESULTADOS NUMÉRICOS - CARACTERIZACIÓN ADC      ")
print("=" * 52)
print(f" • Muestras válidas analizadas : {len(df)}")
print(f" • Ganancia (Pendiente)        : {pendiente:.4f} códigos/V")
print(f" • Error de Offset (Intercepto): {intercepto:.4f} códigos")
print(f" • Linealidad (R^2)            : {r_squared:.6f}")
print("-" * 52)
print(f" • INL Máximo absoluto         : {np.max(np.abs(inl)):.4f} LSB")
print(
    f" • INL Rango (Min / Max)       : {np.min(inl):.4f} LSB  / "
    f" {np.max(inl):.4f} LSB"
)
print(f" • DNL Máximo absoluto         : {np.max(np.abs(dnl)):.4f} LSB")
print(
    f" • DNL Rango (Min / Max)       : {np.min(dnl):.4f} LSB  / "
    f" {np.max(dnl):.4f} LSB"
)
print("=" * 52 + "\n")

# Gráfica 1: Función de Transferencia
plt.figure(figsize=(9, 6))
plt.scatter(x, y, color="blue", s=12, alpha=0.5, label="Datos Medidos")
plt.plot(
    x,
    y_ideal,
    color="red",
    linestyle="--",
    linewidth=2,
    label=f"Ajuste Lineal: y = {pendiente:.2f}x + {intercepto:.2f}",
)
plt.title(
    "Función de Transferencia y Ajuste Lineal del ADC",
    fontsize=13,
    fontweight="bold",
)
plt.xlabel("Tensión de Entrada (V)", fontsize=11)
plt.ylabel("Código ADC", fontsize=11)
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend(loc="upper left")
plt.tight_layout()
plt.savefig(
    OUT_DIR / "funcion_transferencia_adc.png", dpi=300, bbox_inches="tight"
)

# Gráfica 2: INL
plt.figure(figsize=(9, 6))
plt.plot(x, inl, color="purple", linewidth=1.5, label="INL")
plt.axhline(0, color="black", linewidth=0.8, linestyle="--")
plt.title(
    "No Linealidad Integral (INL) del ADC", fontsize=13, fontweight="bold"
)
plt.xlabel("Tensión de Entrada (V)", fontsize=11)
plt.ylabel("Error INL (LSB)", fontsize=11)
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend(loc="best")
plt.tight_layout()
plt.savefig(OUT_DIR / "inl_adc.png", dpi=300, bbox_inches="tight")

# Gráfica 3: DNL
plt.figure(figsize=(9, 6))
plt.plot(
    codigos_validos,
    dnl,
    color="green",
    linewidth=1,
    marker=".",
    markersize=3,
    label="DNL",
)
plt.axhline(0, color="black", linewidth=0.8, linestyle="--")
plt.axhline(1, color="red", linewidth=0.8, linestyle=":", label="Límite ±1 LSB")
plt.axhline(-1, color="red", linewidth=0.8, linestyle=":")
plt.title(
    "No Linealidad Diferencial (DNL) del ADC", fontsize=13, fontweight="bold"
)
plt.xlabel("Código ADC", fontsize=11)
plt.ylabel("Error DNL (LSB)", fontsize=11)
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend(loc="upper right")
plt.tight_layout()
plt.savefig(OUT_DIR / "dnl_adc.png", dpi=300, bbox_inches="tight")

print(f"Gráficas guardadas en: {OUT_DIR}")
plt.show()