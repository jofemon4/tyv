from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT_DIR = Path(__file__).resolve().parent.parent / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)
csv_entrada = OUT_DIR / "medidas_ancho_de_banda.csv"

df = pd.read_csv(csv_entrada, delimiter=";")
df = df.sort_values("Frecuencia_Hz").dropna()

freqs = df["Frecuencia_Hz"].values
amps = df["Amp_PicoPico"].values

amp_ref = np.max(amps[:3]) if len(amps) >= 3 else amps[0]
ganancia_db = 20 * np.log10(np.maximum(amps, 1e-6) / max(amp_ref, 1e-6))

idx_3db = np.where(ganancia_db <= -3.0)[0]
f_3db = freqs[idx_3db[0]] if len(idx_3db) > 0 else None

print("\n" + "=" * 50)
print("       RESULTADOS NUMÉRICOS - ANCHO DE BANDA          ")
print("=" * 50)
print(f" • Amplitud de referencia   : {amp_ref:.1f} códigos P-P")
print(f" • Amplitud mínima medida   : {np.min(amps):.1f} códigos P-P")
if f_3db is not None:
  print(f" • Corte -3 dB estimado     : ~{f_3db:.1f} Hz")
else:
  print(
      " • Corte -3 dB estimado     : No alcanzado en el rango medido"
      f" ({freqs[-1]:.1f} Hz)"
  )
print("=" * 50 + "\n")

plt.figure(figsize=(9, 6))
plt.semilogx(
    freqs,
    ganancia_db,
    "o-",
    color="teal",
    linewidth=1.8,
    label="Respuesta Normalizada (dB)",
)
plt.axhline(
    -3.0, color="red", linestyle="--", linewidth=1.2, label="Límite -3 dB"
)
plt.title(
    "Respuesta en Frecuencia / Ancho de Banda del ADC",
    fontsize=13,
    fontweight="bold",
)
plt.xlabel("Frecuencia (Hz)", fontsize=11)
plt.ylabel("Ganancia Relativa (dB)", fontsize=11)
plt.grid(True, which="both", linestyle="--", alpha=0.6)
plt.legend()
plt.tight_layout()
plt.savefig(OUT_DIR / "ancho_de_banda_adc.png", dpi=300, bbox_inches="tight")
print(f"Gráfica guardada en: {OUT_DIR / 'ancho_de_banda_adc.png'}")
plt.show()