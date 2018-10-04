"""
Autor: Camilo Esteban Nieto Barrera
Lenguaje: Python 3

Descripción: Algoritmo para hallar el conjunto de primeros, siguientes y predicciones de una gramatica.

Recomendaciones:
Para le uso de este algoritmo, la gramatica debe tener unas ciertas recomendaciones
1. No puede haber recursión por la izquierda en las reglas
2. No puede haber factores comunes por la izquierda
3. El programa recibe la gramatica entera vía stdin
4. la forma que debe tener cada regla debe ser A -> E n D as HOLA donde A, E, D y HOLA dondo los nodos no terminales deben ir en mayuscula  y los terminales en minuscula, cada nodo debe ir separado por un espacio y el -> es obligatorio
5. Para finalizar la entrada o agregar EOF oprima <CTRL>-D
"""

import sys
import re
import copy

row_rules = 0 #Contador para guardar el número de la regla actual de la gramatica que se esta procesando
firsts = {} #Diccionario de primeros
nexts = {} #Diccionario de siguientes
predictions = [] #Arreglo de predicciones
dict_rules = {} #Diccionario en el que se guardara un arreglo con todas las reglas que un nodo no terminal pueda tener
array_nodes = [] #Contendra los nodos no terminales en orden de la gframatica
where_nodes = {} #Diccionario que por cada nodo no terminal guardara una tupla conn la fila y columna en la que esta ese nodo en las reglas de la gramatica

node_terminal = re.compile("[a-z]*") #Los nodos terminales son en minuscula
node_not_terminal = re.compile("[A-Z]*") #Los nodos no terminales son en mayuscula

#Función que comparara un caracter con una de las reglas puestas en las variables de las expresiones regulares
def match(rule, character):
  result = re.search(rule, character)
  if result != None and result.group() == character:
    return True
  return False
  
#Funcion para unir dos listas quitando elementos repetidos y el simbolo "e"
def join_lists(list1, list2):
    return list1 + [x for x in list2 if x not in list1 and x != "e"]

#Separa las entradas por espacios y llena el diccionario where_nodes el cual contendra las reglas en las que se encuentran dicho no terminal
def split(rule, row):
  global where_nodes

  aux_rule = []
  aux_node = ""
  col = 0 #Columna o posición del terminal en la regla
  for letter_i in rule:
    if letter_i == '\n':
        continue
    if letter_i != ' ':
      aux_node += letter_i
    else:
        if len(aux_rule) >= 2 and match(node_not_terminal, aux_node): #Esto para evitar guardar las posiciones de la parte izquierda de la gramatica (A ->)
          if aux_node not in where_nodes:
            where_nodes[aux_node] = [(row, col)]
          else:
            where_nodes[aux_node].append((row, col))
      
        aux_rule.append(aux_node)
        aux_node = ""
        col += 1

  return aux_rule
  
 #Encuentra el conjunto de primeros del nodo node
def find_firsts(node, a_r, dict_rules):
    global firsts
    aux_node = []

    if node not in firsts:
        firsts[node] = []
        
    for rule_i in range(len(a_r)):
        next_node = a_r[-1-rule_i][0]
        next_node_firsts = []
        if match(node_terminal, next_node):
            if next_node not in aux_node: 
                aux_node.append(next_node)
        else:
            next_node_firsts = find_firsts(next_node, dict_rules[next_node], dict_rules)
            if 'e' in next_node_firsts:
                if len(a_r[-1-rule_i]) == 1:
                    if "e" not in aux_node:
                        aux_node.append("e")       
                else:
                    a_r[-1-rule_i] = a_r[-1-rule_i][1:]
                    aux_node_firsts = find_firsts(node, a_r, dict_rules)
                    next_node_firsts = join_lists(next_node_firsts, aux_node_firsts)
                    
            aux_node = join_lists(aux_node, next_node_firsts)
                    
    firsts[node] = firsts[node] + [x for x in aux_node if x not in firsts[node]]
    return firsts[node]

#Encuentra el conjunto de segundos del nodo node
def find_nexts(node, initial_rules):
    global nexts
    global where_nodes
    global dict_rules
    
    if node not in nexts:
        nexts[node] = []
    else:
        return nexts[node]
    
    for i in where_nodes[node]:
        row = i[0]
        col = i[1] + 1
        rule = initial_rules[row]
        stop = False
        
        while (not stop):
            if col <= len(rule) - 1:
                if match(node_terminal, rule[col]): #Si es un terminal agreguelo a siguientes de node
                    if rule[col] not in nexts[node]:
                        nexts[node].append(rule[col])
                    stop = True
                else:
                    nexts[node] = join_lists(nexts[node], firsts[rule[col]])
                    if "e" not in firsts[rule[col]]:
                        stop = True
                col += 1
            else:
                nexts[node] = join_lists(nexts[node], find_nexts(rule[0], initial_rules))
                stop = True
        
    return nexts[node]

#Encuentra el conjunto de predicciones de la regla rule
def find_predictions(rule):
    aux_predictions = []
    stop = False
    node = 2
    while not stop:
        if rule[node] == "e": #Si la regla es vacia
            return nexts[rule[0]]
        if match(node_terminal, rule[node]): #Si es un termianl
            aux_predictions = join_lists(aux_predictions, [rule[node]])
            return aux_predictions
        aux_predictions = join_lists(aux_predictions, firsts[rule[node]])
        if "e" not in firsts[rule[node]]: #Si no hay "e" significa que no puede tomar el siguiente no terminal
            return aux_predictions
        if node == len(rule)-1: #Si llega al final significa que toda la regla puede ser "e"
            aux_predictions = join_lists(aux_predictions, nexts[rule[0]])
            return aux_predictions
        node += 1

#Recoger datos, separarlos por espacio, llenar el diccionario de reglas con sus respectivos arrays (contiene todas las reglas de un mismo termino) y llenar el arreglo de terminos no terminales en el orden ascendente
rules_in = sys.stdin.readlines()
for rule_i in range(len(rules_in)):
    rules_in[rule_i] = split(rules_in[rule_i]+" ", row_rules)
    rule = rules_in[rule_i]
    if rule[0] not in dict_rules:
        dict_rules[rule[0]] = [rule[2:]]
    else:
        dict_rules[rule[0]].append(rule[2:])
    if len(array_nodes) == 0 or array_nodes[len(array_nodes)-1] != rule[0]:
        array_nodes.append(rule[0])
        
    row_rules += 1
    

#Hallar primeros
copy_dict_rules = copy.deepcopy(dict_rules)
for node_i in range(len(array_nodes)):
    node = array_nodes[-1-node_i]
    find_firsts(node, copy_dict_rules[node], copy_dict_rules)

#Hallar segundos
array_nodes_1 = array_nodes[1:]
for node in array_nodes_1:
    nexts[array_nodes[0]] = ["$"]
    find_nexts(node, rules_in)

#Hallar predicciones
for rule in rules_in:
    predictions.append(find_predictions(rule))
    
print("Predicciones: ")
for rule_i in range(len(rules_in)):
    print(rules_in[rule_i], "->", predictions[rule_i])