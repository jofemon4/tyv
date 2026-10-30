import time
import serial

# IMPORTANTE: Cambia 'COM3' por el puerto exacto donde esté conectado tu Arduino
# (puedes consultarlo en el Administrador de dispositivos de Windows)
puerto_arduino = "COM3"
baudios = 115200

print(f"Conectando con Arduino en {puerto_arduino}...")
s = serial.Serial(puerto_arduino, baudios)
time.sleep(2)  # Pausa breve para estabilizar la conexión serie

# Enviar el carácter 'r' que solicita una medida del ADC al programa de Arduino[cite: 2, 6]
s.write(bytes("r", "utf-8"))

# Leer la respuesta enviada por el microcontrolador[cite: 2, 6]
medida = s.readline()
print(f"Valor leído del ADC: {medida.decode('utf-8').strip()}")

# Cerrar la conexión serie
s.close()