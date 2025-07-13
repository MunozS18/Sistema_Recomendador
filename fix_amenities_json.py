import json

INPUT_FILE = 'hoteles_scrapeados.json'

with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    hoteles = json.load(f)

cambios = 0
faltantes = 0
for hotel in hoteles:
    if 'name' not in hotel:
        if 'nombre' in hotel:
            hotel['name'] = hotel.pop('nombre')
            cambios += 1
        else:
            print(f"Hotel sin clave 'name' ni 'nombre': {hotel}")
            faltantes += 1
    elif 'nombre' in hotel:
        # Si existen ambos, elimina 'nombre'
        hotel.pop('nombre')
        cambios += 1

if cambios > 0 or faltantes > 0:
    with open(INPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(hoteles, f, ensure_ascii=False, indent=2)

print(f"Corrección completada. Hoteles corregidos: {cambios}. Hoteles sin 'name' ni 'nombre': {faltantes}.") 