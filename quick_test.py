import pyvisa
import time

rm = pyvisa.ResourceManager()
gen = rm.open_resource("USB0::0x0400::0x09C4::DG1D182202731::INSTR")

# 1. Asegurar salida encendida

# 2. Forzar modo DC en el canal 1
gen.write("SOUR1:FUNC DC")

# 3. Intentar cambiar la tensión a 2.5 Voltios mediante el offset
gen.write("OUTP1 ON")
gen.write("SOUR1:VOLT:OFFS 5")
time.sleep(5)
gen.write("OUTP1 OFF")

