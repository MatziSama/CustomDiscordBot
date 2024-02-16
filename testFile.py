#
# Este es un archivo de pruebas
# Se puede borrar y reescribir por completo, este modulo no se usa en ninguna aplicación

import json

search = "374711888409395212"

path = "./roles.json"

file = open(path, encoding='utf-8')
data = json.load(file)

if search in data.keys():
    print(data[f"{search}"])
else:
    print("No se encontró esa id")