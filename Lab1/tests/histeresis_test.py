from pathlib import Path
import time
import pandas as pd
import pyvisa
import serial

VISA_GEN_ADDRESS = "USB0::0x0400::0x09C4::DG1D182202731::INSTR"
PUERTO_ARDUINO = "COM3"
BAUDIOS = 115200

V_MIN = 0.0
V_MAX = 5.0
NUM_PASOS = 50

OUT_DIR = Path(__file__).resolve().parent.parent / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)
csv_salida = OUT_DIR / "medidas_histeresis.csv"

rm = pyvisa.ResourceManager()
gen = rm.open_resource(VISA_GEN_ADDRESS)
gen.timeout = 3000

arduino = serial.Serial(PUERTO_ARDUINO, BAUDIOS, timeout=1.5)
time.sleep(2)

voltajes_ida = [
    V_MIN + i * (V_MAX - V_MIN) / (NUM_PASOS - 1) for i in range(NUM_PASOS)
]
voltajes_vuelta = list(reversed(voltajes_ida))
resultados = []

try:
  print("Iniciando ensayo de histéresis...")
  gen.write("SOUR1:FUNC DC")
  gen.write(f"VOLT:OFFS {V_MIN}")
  gen.write("OUTP1 ON")
  time.sleep(2.0)

  print("Barrido de IDA (0V -> 5V)...")
  for v in voltajes_ida:
    gen.write(f"VOLT:OFFS {v}")
    time.sleep(1.5)
    arduino.reset_input_buffer()
    arduino.write(b"r")
    val = arduino.readline().decode("utf-8").strip()
    try:
      resultados.append(
          {"Direccion": "Ida", "V_Generador": v, "ADC_Code": int(val)}
      )
    except ValueError:
      pass

  print("Barrido de VUELTA (5V -> 0V)...")
  for v in voltajes_vuelta:
    gen.write(f"VOLT:OFFS {v}")
    time.sleep(1.5)
    arduino.reset_input_buffer()
    arduino.write(b"r")
    val = arduino.readline().decode("utf-8").strip()
    try:
      resultados.append(
          {"Direccion": "Vuelta", "V_Generador": v, "ADC_Code": int(val)}
      )
    except ValueError:
      pass

finally:
  try:
    gen.write("OUTP1 OFF")
  except Exception:
    pass
  arduino.close()
  gen.close()
  rm.close()

df = pd.DataFrame(resultados)
df.to_csv(csv_salida, sep=";", index=False)
print(f"Datos de histéresis guardados en: {csv_salida}")