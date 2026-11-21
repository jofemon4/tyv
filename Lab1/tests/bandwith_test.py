from pathlib import Path
import time
import numpy as np
import pandas as pd
import pyvisa
import serial

VISA_GEN_ADDRESS = "USB0::0x0400::0x09C4::DG1D182202731::INSTR"
PUERTO_ARDUINO = "COM3"
BAUDIOS = 115200

frecuencias = np.logspace(2, 3.7, 15)  # ~100 Hz a ~5 kHz
AMPLITUD_VPP = 2.0
OFFSET_V = 2.5

OUT_DIR = Path(__file__).resolve().parent.parent / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)
csv_salida = OUT_DIR / "medidas_ancho_de_banda.csv"

rm = pyvisa.ResourceManager()
gen = rm.open_resource(VISA_GEN_ADDRESS)
gen.timeout = 3000

arduino = serial.Serial(PUERTO_ARDUINO, BAUDIOS, timeout=1.5)
time.sleep(2)

resultados_bw = []

try:
  print("Iniciando test de ancho de banda...")
  gen.write("SOUR1:FUNC SIN")
  gen.write(f"VOLT {AMPLITUD_VPP}")
  gen.write(f"VOLT:OFFS {OFFSET_V}")
  gen.write("OUTP1 ON")
  time.sleep(1.5)

  for freq in frecuencias:
    gen.write(f"FREQ {freq}")
    time.sleep(0.5)

    muestras = []
    for _ in range(40):
      arduino.reset_input_buffer()
      arduino.write(b"r")
      val = arduino.readline().decode("utf-8").strip()
      try:
        muestras.append(int(val))
      except ValueError:
        pass

    if muestras:
      amp_pp = int(np.max(muestras) - np.min(muestras))
      resultados_bw.append({"Frecuencia_Hz": freq, "Amp_PicoPico": amp_pp})
      print(f" • Freq: {freq:7.1f} Hz  --->  Amp P-P: {amp_pp} códigos")

finally:
  try:
    gen.write("OUTP1 OFF")
  except Exception:
    pass
  arduino.close()
  gen.close()
  rm.close()

df_bw = pd.DataFrame(resultados_bw)
df_bw.to_csv(csv_salida, sep=";", index=False)
print(f"Datos de ancho de banda guardados en: {csv_salida}")