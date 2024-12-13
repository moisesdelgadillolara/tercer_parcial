import re
import string
import json
import os
import itertools
import matplotlib.pyplot as plt
import networkx as nx

# Operadores booleanos
operadores = {
    'y': '∧',   # "y" se convierte en "∧" (AND)
    'o': '∨',   # "o" se convierte en "∨" (OR)
    'no': '¬',   # "no" se convierte en "¬" (NOT)
    'y no': '∧ ¬',   # "y no" se convierte en "∧ ¬"
    'o no': '∨ ¬'    # "o no" se convierte en "∨ ¬"
}

def check_create_json(file_name):
    if not os.path.exists(file_name):
        with open(file_name, 'w') as file:
            json.dump({}, file) if file_name == 'atomos.json' else json.dump([], file)

def load_json(file_name):
    if not os.path.exists(file_name):
        print(f"El archivo {file_name} no existe.")
        return {} if file_name == 'atomos.json' else []
    with open(file_name, 'r') as file:
        try:
            data = json.load(file)
            return data
        except json.JSONDecodeError as e:
            return {}

def save_json(data, file_name):
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)

def expresion_regla(texto):
    check_create_json('atomos.json')
    existing_oraciones = load_json('atomos.json')
    
    texto = texto.lower()
    partes = re.split(r'\s+(o no|y no|y|o|no)\s+', texto)

    # Inicializa diccionario para almacenar las oraciones nuevas
    oraciones = existing_oraciones.copy()  # Átomos existentes
    operador_actual = []  # El operador u operadores que se están usando en lo solicitado

    # Asignar oraciones a variables (a, b, c, ...)
    variable_index = len(existing_oraciones)  # Continuar desde donde se quedó
    for i, parte in enumerate(partes):
        # Si la parte actual es un operador, lo almacenamos
        if parte in operadores:
            operador_actual.append(operadores[parte])
        else:
            # Elimina espacios extra de la oración
            oracion = parte.strip()
            if oracion and oracion not in oraciones.values():
                # Asigna la oración a una variable en orden alfabético
                variable = f"A{variable_index}"
                oraciones[variable] = oracion
                variable_index += 1
                print(f"Átomo {variable}: '{oracion}'")  # Muestra el número de átomo y el texto

    # Guardar solo nuevas oraciones en atomos.json
    new_oraciones = {k: v for k, v in oraciones.items() if v not in existing_oraciones.values()}
    if new_oraciones:
        save_json(oraciones, 'atomos.json')
    
    # Construye la expresión lógica y el array con variables y operadores
    expresion = ""
    elementos = []
    oraciones_en_regla = []

    for parte in partes:
        parte_limpia = parte.strip()
        if parte_limpia in oraciones.values():
            # Si la parte es una oración, busca la clave correspondiente
            key = [k for k, v in oraciones.items() if v == parte_limpia][0]
            expresion += key + " "
            elementos.append(key)
            oraciones_en_regla.append((key, parte_limpia))
        elif parte_limpia in operadores:
            # Si la parte es un operador, añade su representación
            expresion += operadores[parte_limpia] + " "
            elementos.append(operadores[parte_limpia])

    # Imprime los átomos y sus textos
    for oracion in oraciones_en_regla:
        print(f"{oracion[0]}: {oracion[1]}")
    
    return elementos, expresion.strip(), oraciones_en_regla, operador_actual

def guardar_regla(regla):
    check_create_json('reglas.json')
    reglas = load_json('reglas.json')
    if regla in reglas:
        print("\n\nEsta regla ya existe")
    else:
        reglas.append(regla)
        save_json(reglas, 'reglas.json')
        print("\n\nRegla guardada")

def generar_tabla_verdad(atomos, operador):
    n = len(atomos)
    combinaciones = list(itertools.product([0, 1], repeat=n))
    
    # Imprimir encabezado de la tabla
    print(' | '.join(atomos) + ' | Resultado')
    print('-' * (len(atomos) * 4 + 11))
    
    for combinacion in combinaciones:
        valores = ' | '.join(map(str, combinacion))
        if operador == '∧':
            resultado = all(combinacion)
        elif operador == '∨':
            resultado = any(combinacion)
        else:
            resultado = "N/A"  # No se reconoce el operador
        print(f'{valores} | {int(resultado)}')

def draw_binary_tree(atomos, operador):
    num_levels = len(atomos)
    G = nx.DiGraph()
    combinaciones = list(itertools.product([0, 1], repeat=num_levels))

    # Create the nodes for the tree
    for level in range(num_levels + 1):
        nodes_at_level = 2 ** level
        for i in range(nodes_at_level):
            node_name = f"{level}-{i}"
            if level < num_levels:
                label = atomos[level] if i < len(atomos) else ""
                node_color = 'lightblue'
            else:
                combinacion = combinaciones[i]
                resultado = all(combinacion) if operador == '∧' else any(combinacion)
                label = str(int(resultado))
                node_color = 'green' if resultado else 'lightblue'
            G.add_node(node_name, subset=level, label=label, color=node_color)

    # Create the edges for the tree and label them with 0 or 1
    edge_labels = {}
    for level in range(num_levels):
        nodes_at_level = 2 ** level
        for i in range(nodes_at_level):
            parent_node = f"{level}-{i}"
            child_node_left = f"{level+1}-{2*i}"
            child_node_right = f"{level+1}-{2*i+1}"
            G.add_edge(parent_node, child_node_left)
            G.add_edge(parent_node, child_node_right)
            edge_labels[(parent_node, child_node_left)] = '0'
            edge_labels[(parent_node, child_node_right)] = '1'

    pos = nx.multipartite_layout(G, subset_key="subset")
    labels = nx.get_node_attributes(G, 'label')
    colors = nx.get_node_attributes(G, 'color')

    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, labels=labels, with_labels=True, node_size=500, node_color=[colors[node] for node in G.nodes()], font_size=8, font_weight="bold", edge_color="gray")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
    plt.title(f"Arbol Binario para {operador}")
    plt.show()

def obtener_regla_texto_natural(regla, atomos):
    # Dividir la regla en partes
    partes = regla.split()
    regla_texto = []

    # Reemplazar las variables por sus correspondientes oraciones
    for parte in partes:
        if parte in atomos:
            regla_texto.append(atomos[parte])
        else:
            # Si es un operador, se usa tal cual
            operador_texto = [key for key, value in operadores.items() if value == parte]
            if operador_texto:
                regla_texto.append(operador_texto[0])
            else:
                regla_texto.append(parte)

    return ' '.join(regla_texto)

# Función del menú
def menu():
    while True:
        print("\nMENU")
        print("1) Insertar nueva regla")
        print("2) Mostrar átomos")
        print("3) Mostrar reglas")
        print("4) Mostrar tabla de verdad de nueva regla")
        print("5) Mostrar árbol binario de nueva regla")
        print("6) Cerrar")

        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            texto = input("Inserte la nueva regla: ")
            elementos, regla, oraciones_en_regla, operador_actual = expresion_regla(texto)
            print("Regla:", regla)
            guardar_regla(regla)
        elif opcion == '2':
            check_create_json('atomos.json')
            atomos = load_json('atomos.json')
            for i, (variable, oracion) in enumerate(atomos.items()):
                print(f"{i+1}) {variable}: {oracion}")
        elif opcion == '3':
            check_create_json('reglas.json')
            reglas = load_json('reglas.json')
            reglas.sort()  # Ordena las reglas alfabéticamente
            check_create_json('atomos.json')
            atomos = load_json('atomos.json')
            for i, regla in enumerate(reglas):
                regla_texto_natural = obtener_regla_texto_natural(regla, atomos)
                print(f"{i+1}) {regla}")
                print(f"   Regla en texto natural: {regla_texto_natural}")
        elif opcion == '4':
            texto = input("Inserte la regla: ")
            elementos, regla, oraciones_en_regla, operador_actual = expresion_regla(texto)
            check_create_json('reglas.json')
            reglas = load_json('reglas.json')
            if regla in reglas:
                print("La regla ya existe.")
            else:
                guardar_regla(regla)
            atomos = [oracion[0] for oracion in oraciones_en_regla]
            primer_operador = operador_actual[0] if operador_actual else None
            generar_tabla_verdad(atomos, primer_operador)
        elif opcion == '5':
            texto = input("Inserte la regla: ")
            elementos, regla, oraciones_en_regla, operador_actual = expresion_regla(texto)
            check_create_json('reglas.json')
            reglas = load_json('reglas.json')
            if regla in reglas:
                print("La regla ya existe.")
            else:
                guardar_regla(regla)
            atomos = [oracion[0] for oracion in oraciones_en_regla]
            primer_operador = operador_actual[0] if operador_actual else None
            draw_binary_tree(atomos, primer_operador)
        elif opcion == '6':
            print("Cerrando el programa.")
            break
        else:
            print("Opción inválida. Intente de nuevo.")

# Ejecutar el menú
menu()
