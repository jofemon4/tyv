import time
import numpy as np
import pyvisa
import serial

VISA_GEN_ADDRESS = "USB0::0x0400::0x09C4::DG1D182202731::INSTR"
PUERTO_ARDUINO = "COM3"
BAUDIOS = 115200

frecuencias = np.logspace(2, 3.7, 15)  # De 100 Hz a ~5 kHz
AMPLITUD_VPP = 2.0
OFFSET_V = 2.5

rm = pyvisa.ResourceManager()
gen = rm.open_resource(VISA_GEN_ADDRESS)
gen.timeout = 3000

arduino = serial.Serial(PUERTO_ARDUINO, BAUDIOS, timeout=1.5)
time.sleep(2)

resultados_bw = []

try:
  print("Iniciando test de Ancho de Banda...")
  gen.write("SOUR1:FUNC SIN")
  gen.write(f"VOLT {AMPLITUD_VPP}")
  gen.write(f"VOLT:OFFS {OFFSET_V}")
  gen.write("OUTP1 ON")
  time.sleep(1.0)

  for freq in frecuencias:
    gen.write(f"FREQ {freq}")
    time.sleep(0.5)  # Estabilizar frecuencia

    muestras = []
    for _ in range(40):  # Capturar suficientes ciclos para hallar el pico
      arduino.reset_input_buffer()
      arduino.write(b"r")
      val = arduino.readline().decode("utf-8").strip()
      try:
        muestras.append(int(val))
      except ValueError:
        pass

    if muestras:
      amp_pico_a_pico = np.max(muestras) - np.min(muestras)
      resultados_bw.append({"Frecuencia_Hz": freq, "Amp_PicoPico": amp_pico_a_pico})
      print(f" • Freq: {freq:7.1f} Hz  --->  Amp P-P: {amp_pico_a_pico} códigos")

finally:
  gen.write("OUTP1 OFF")
  arduino.close()
  gen.close()
  rm.close()

import pandas as pd

df_bw = pd.DataFrame(resultados_bw)
df_bw.to_csv("medidas_ancho_de_banda.csv", sep=";", index=False)
print("Ensayo de ancho de banda finalizado. Guardado en 'medidas_ancho_de_banda.csv'.")