import csv
import time
import pyvisa
import serial

# --- 1. CONFIGURACIÓN DE PARÁMETROS ---
VISA_GEN_ADDRESS = "USB0::0x0400::0x09C4::DG1D182202731::INSTR"
PUERTO_ARDUINO = "COM3"
BAUDIOS = 115200

V_INICIO = 0.0
V_FIN = 5.0
PASO_V = 0.01
TIEMPO_ESTABILIZACION = 0.5  # Tus 2 segundos de pausa física
NOMBRE_CSV = "medidas_adc_arduino.csv"

print("Inicializando recursos...")

# --- 2. INICIALIZACIÓN ---
rm = pyvisa.ResourceManager()
gen = rm.open_resource(VISA_GEN_ADDRESS)
gen.timeout = 3000

arduino = serial.Serial(PUERTO_ARDUINO, BAUDIOS, timeout=1.5)
time.sleep(2)

f_csv = open(NOMBRE_CSV, mode="w", newline="")
escritor_csv = csv.writer(f_csv, delimiter=";")
escritor_csv.writerow(["Timestamp", "V_Generador", "ADC_Code"])

try:
  print("Configurando generador en modo DC...")
  gen.write("SOUR1:FUNC DC")
  time.sleep(0.2)

  # Fijar tensión inicial y encender la salida una sola vez antes del bucle
  gen.write(f"VOLT:OFFS {V_INICIO}")
  time.sleep(0.2)
  gen.write("OUTP1 ON")
  time.sleep(0.5)

  print(
      f"Iniciando barrido de {V_INICIO}V a {V_FIN}V con pasos de {PASO_V}V..."
  )

  v_actual = V_INICIO
  while v_actual <= V_FIN + 1e-9:
    try:
      # 1. Cambiar el voltaje usando el comando oficial de offset del manual
      gen.write(f"VOLT:OFFS {v_actual}")

      # 2. Esperar tus 2 segundos de estabilización física en el circuito
      # (Este tiempo de espera evita por completo la saturación del búfer USB del Rigol)
      time.sleep(TIEMPO_ESTABILIZACION)

      # 3. Solicitar lectura del ADC al Arduino
      arduino.reset_input_buffer()
      arduino.write(b"r")

      raw_data = arduino.readline()
      adc_code = raw_data.decode("utf-8").strip()

      if not adc_code:
        adc_code = "TIMEOUT_ARDUINO"

    except Exception as e:
      print(f"[AVISO] Error en paso V={v_actual:.4f}V: {e}")
      adc_code = "ERROR_COM"

    # 4. Guardar datos en el CSV y mostrar por pantalla
    timestamp = time.strftime("%H:%M:%S")
    escritor_csv.writerow([timestamp, f"{v_actual:.4f}", adc_code])
    print(f"V_gen: {v_actual:.4f} V ---> ADC Code: {adc_code}")

    v_actual += PASO_V

  print("Barrido completado con éxito.")

finally:
  print("Cerrando conexiones y liberando recursos...")
  try:
    gen.write("OUTP1 OFF")
  except:
    pass
  f_csv.close()
  arduino.close()
  gen.close()
  rm.close()
  print("Proceso finalizado.")