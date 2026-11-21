from pathlib import Path
import time
import pandas as pd
import pyvisa
import serial

VISA_GEN_ADDRESS = "USB0::0x0400::0x09C4::DG1D182202731::INSTR"
PUERTO_ARDUINO = "COM3"
BAUDIOS = 115200

TENSION_FIJA = 2.5
NUM_MUESTRAS = 300

OUT_DIR = Path(__file__).resolve().parent.parent / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)
csv_salida = OUT_DIR / "medidas_ruido.csv"

rm = pyvisa.ResourceManager()
gen = rm.open_resource(VISA_GEN_ADDRESS)
gen.timeout = 3000

arduino = serial.Serial(PUERTO_ARDUINO, BAUDIOS, timeout=1.5)
time.sleep(2)

resultados = []

try:
  print(f"Fijando tensión en {TENSION_FIJA}V...")
  gen.write("SOUR1:FUNC DC")
  gen.write(f"VOLT:OFFS {TENSION_FIJA}")
  gen.write("OUTP1 ON")
  time.sleep(2.0)

  print(f"Capturando {NUM_MUESTRAS} muestras consecutivas...")
  for i in range(NUM_MUESTRAS):
    arduino.reset_input_buffer()
    arduino.write(b"r")
    adc_str = arduino.readline().decode("utf-8").strip()
    try:
      codigo_adc = int(adc_str)
      resultados.append({
          "Muestra": i,
          "V_Generador": TENSION_FIJA,
          "ADC_Code": codigo_adc,
      })
    except ValueError:
      pass
    time.sleep(0.02)

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
print(f"Datos de ruido guardados en: {csv_salida}")