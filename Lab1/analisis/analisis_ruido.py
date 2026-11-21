from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT_DIR = Path(__file__).resolve().parent.parent / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)
csv_entrada = OUT_DIR / "medidas_ruido.csv"

df = pd.read_csv(csv_entrada, delimiter=";")
lecturas = pd.to_numeric(df["ADC_Code"], errors="coerce").dropna().values

media = np.mean(lecturas)
std_dev = np.std(lecturas)
pico_a_pico = np.ptp(lecturas)
min_val = int(np.min(lecturas))
max_val = int(np.max(lecturas))

print("\n" + "=" * 50)
print("        RESULTADOS NUMÉRICOS - ANÁLISIS DE RUIDO      ")
print("=" * 50)
print(f" • Muestras analizadas : {len(lecturas)}")
print(f" • Media (µ)           : {media:.3f} códigos")
print(f" • Desviación Est. (σ) : {std_dev:.4f} códigos")
print(f" • Rango Pico a Pico   : {pico_a_pico} códigos ({min_val} a {max_val})")
print("=" * 50 + "\n")

plt.figure(figsize=(9, 6))
bins = np.arange(min_val - 0.5, max_val + 1.5, 1)
plt.hist(
    lecturas,
    bins=bins,
    color="steelblue",
    edgecolor="black",
    alpha=0.8,
    rwidth=0.85,
)
plt.axvline(
    media, color="red", linestyle="--", linewidth=1.8, label=f"Media: {media:.2f}"
)
plt.title(
    "Histograma de Ruido y Estabilidad del ADC", fontsize=13, fontweight="bold"
)
plt.xlabel("Código ADC", fontsize=11)
plt.ylabel("Frecuencia (nº de muestras)", fontsize=11)
plt.grid(axis="y", linestyle="--", alpha=0.6)
plt.legend()
plt.tight_layout()
plt.savefig(
    OUT_DIR / "ruido_histograma_adc.png", dpi=300, bbox_inches="tight"
)
print(f"Gráfica guardada en: {OUT_DIR / 'ruido_histograma_adc.png'}")
plt.show()