import time
import pandas as pd
import pyvisa
import serial

VISA_GEN_ADDRESS = "USB0::0x0400::0x09C4::DG1D182202731::INSTR"
PUERTO_ARDUINO = "COM3"
BAUDIOS = 115200

V_MIN = 0.0
V_MAX = 5.0
NUM_PASOS = 50  # Pasos para la ida y para la vuelta

rm = pyvisa.ResourceManager()
gen = rm.open_resource(VISA_GEN_ADDRESS)
gen.timeout = 3000

arduino = serial.Serial(PUERTO_ARDUINO, BAUDIOS, timeout=1.5)
time.sleep(2)

voltajes_ida = [
    V_MIN + i * (V_MAX - V_MIN) / (NUM_PASOS - 1) for i in range(NUM_PASOS)
]
voltajes_vuelta = list(reversed(voltajes_ida))
resultados_histeresis = []

try:
  print("Iniciando Ensayo de Histéresis...")
  gen.write("SOUR1:FUNC DC")
  gen.write(f"VOLT:OFFS {V_MIN}")
  gen.write("OUTP1 ON")
  time.sleep(2.0)

  # --- BARRIDO DE IDA (0V -> 5V) ---
  print("Ejecutando barrido de IDA (0V -> 5V)...")
  for v in voltajes_ida:
    gen.write(f"VOLT:OFFS {v}")
    time.sleep(1.5)  # Pausa de seguridad
    arduino.reset_input_buffer()
    arduino.write(b"r")
    val = arduino.readline().decode("utf-8").strip()
    try:
      resultados_histeresis.append(
          {"Direccion": "Ida", "V_Generador": v, "ADC_Code": int(val)}
      )
    except ValueError:
      pass

  # --- BARRIDO DE VUELTA (5V -> 0V) ---
  print("Ejecutando barrido de VUELTA (5V -> 0V)...")
  for v in voltajes_vuelta:
    gen.write(f"VOLT:OFFS {v}")
    time.sleep(1.5)
    arduino.reset_input_buffer()
    arduino.write(b"r")
    val = arduino.readline().decode("utf-8").strip()
    try:
      resultados_histeresis.append(
          {"Direccion": "Vuelta", "V_Generador": v, "ADC_Code": int(val)}
      )
    except ValueError:
      pass

finally:
  gen.write("OUTP1 OFF")
  arduino.close()
  gen.close()
  rm.close()

df = pd.DataFrame(resultados_histeresis)
df.to_csv("medidas_histeresis.csv", sep=";", index=False)
print("Ensayo de histéresis finalizado. Guardado en 'medidas_histeresis.csv'.")