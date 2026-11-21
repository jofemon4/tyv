import time
import numpy as np
import pyvisa
import serial

VISA_GEN_ADDRESS = "USB0::0x0400::0x09C4::DG1D182202731::INSTR"
PUERTO_ARDUINO = "COM3"
BAUDIOS = 115200

TENSION_FIJA = 2.5
NUM_MUESTRAS = 300

rm = pyvisa.ResourceManager()
gen = rm.open_resource(VISA_GEN_ADDRESS)
gen.timeout = 3000

arduino = serial.Serial(PUERTO_ARDUINO, BAUDIOS, timeout=1.5)
time.sleep(2)

lecturas = []

try:
  print(f"Configurando tensión fija en {TENSION_FIJA}V...")
  gen.write("SOUR1:FUNC DC")
  gen.write(f"VOLT:OFFS {TENSION_FIJA}")
  gen.write("OUTP1 ON")
  time.sleep(2.0)  # Estabilización

  print(f"Capturando {NUM_MUESTRAS} muestras consecutivas...")
  for _ in range(NUM_MUESTRAS):
    arduino.reset_input_buffer()
    arduino.write(b"r")
    val = arduino.readline().decode("utf-8").strip()
    try:
      lecturas.append(int(val))
    except ValueError:
      pass
    time.sleep(0.02)

  lecturas = np.array(lecturas)
  print("\n--- RESULTADOS DE RUIDO ---")
  print(f" • Media: {np.mean(lecturas):.2f}")
  print(f" • Desviación Estándar (σ): {np.std(lecturas):.4f} códigos")
  print(
      f" • Pico a Pico: {np.ptp(lecturas)} códigos (Min:"
      f" {np.min(lecturas)}, Max: {np.max(lecturas)})"
  )

finally:
  gen.write("OUTP1 OFF")
  arduino.close()
  gen.close()
  rm.close()