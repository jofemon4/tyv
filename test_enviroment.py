import pyvisa

# Obtener una referencia al Resource Manager
rm = pyvisa.ResourceManager()

# Obtener una lista de los recursos que devuelve el Resource Manager
recursos = rm.list_resources()

# Imprimir la lista en pantalla
print(recursos)