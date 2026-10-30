import time
import pyvisa

# 1. Inicializar el Resource Manager de VISA[cite: 5, 6]
rm = pyvisa.ResourceManager()

# 2. Abrir la conexión con el generador usando tu dirección exacta
visa_address = "USB0::0x0400::0x09C4::DG1D182202731::INSTR"
gen = rm.open_resource(visa_address)

# 3. Comprobar la identificación del equipo con el comando SCPI '*IDN?'
gen.write("*IDN?")
time.sleep(0.5)  # Espera obligatoria para dar tiempo al equipo a responder[cite: 8]
idn = gen.read()
print(f"Instrumento conectado: {idn.strip()}")

# 4. Configurar el generador en modo DC y fijar tensión inicial (0V)[cite: 6, 7]
# (Nota: Debes consultar la programming guide del generador para el comando exacto de DC)
# gen.write('APPL:DC 1E3, 5.0, 0, 2.5') # Ejemplo de sintaxis habitual en generadores Rigol

# 5. Habilitar la salida del generador usando 'OUTP <ON|OFF>'[cite: 6, 7]
gen.write("OUTP ON")

# --- (Aquí integrarías el bucle de medidas con el Arduino y el fichero CSV) ---

# 6. Al finalizar la práctica: deshabilitar la salida y cerrar recursos[cite: 6, 7]
gen.write("OUTP OFF")
gen.close()
rm.close()