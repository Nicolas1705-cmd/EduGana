# LISTAS -> [] 
# caracteristicas: ordenada, indexada, mutable
# contener diferentes tipos de datos, tamaño dinamico
# mi primera lista vacia
lista=[]
print(lista)
# mi primera lista con elementos 
lista=["Manzana","Banana","Cereza","Uva","Pera","Sandia"]
print(type(lista))
print(lista)
# Lista con varios elementos 
lista=[1,2.5,"Fruta",True,4+5j]
# crear una lista de nuemero del 1 al 5
print(lista)
numeros= [x for x in range(1,6)]
print(numeros)
# ejemplo de bucle for
"""
    1 vuelta: x=1
    2 vuelta: x=2
    3 vuelta: x=3
    4 vuelta: x=4   
    5 vuelta: x=5 
"""
for x in range(1,6):
    print(x)
# crear una lista a partir de una cadena
cadena="Este es un jemplo de una cadena"
palabras=cadena.split()
print(palabras)
# crear una lista de numeros pares}
numeros_pares=[]
for i in range(2,11,2):
    numeros_pares.append(i)
print(numeros_pares)
# lista de listas
lista_de_listas=[[1,2,3],[4,5,6],[7,8,9]]
print(lista_de_listas[2])
print(lista_de_listas[2][1])
# acceder a las listas
frutas=["Piña","Manzana","Sandia","Uva"]
print (frutas[1])
print (frutas[3])
print (frutas[1:])  #(inicio:fin:paso)
print (frutas[0:3:2])
fruta=["Piña", "Manzana","Sandía","Uva"]
frutas[3]="Mango" 
print (frutas)
#  Agregar elemento en una posicion elegida
frutas.insert(1,"Naranja")
print(frutas)
# Agregar un elemento al final de la lista
frutas.append("Pera")
frutas.append("Maracuyá")
print(frutas)
otras_frutas=["Fresa","Melocoton"]
# Añadir elementos de otra lista
frutas.extend(otras_frutas)
print(frutas)
#Crear una lista de números pares y otra de números impares, ambas hasta el número 10
#Deberá añadirla en una sola lista
NumerosPares=[2,4,6,8,10]
NumerosImpares=[1,3,5,7,9]
numeros=[]
numeros.extend(NumerosImpares)
numeros.extend(NumerosPares)

print(numeros)

# Remover elementos
numeros.remove(6)
print(numeros)

# Elminar elementos usando posición

numeros.pop(8)
print(numeros)

# Eliminar todos los elementos
numeros.clear()
print(numeros)

#Eliminar elemento
print(len(frutas))
del frutas[8]
del frutas[4:]
print(frutas)

# Ordenar elementos de forma ascendente
numeros.sort()
print(numeros)

#Ordenar elementos de forma descendente
numeros.sort(reverse=True)
print(numeros)


Platos= ["Ceviche","Arroz con pollo","Causa","Arroz con cabrito","Tamal"]
Platos.sort()
print(Platos)
Platos.sort(reverse=True)
print(Platos)
NuevosPlatos=sorted(Platos)
print(NuevosPlatos)
NuevosPlatos=sorted(Platos,reverse=True)
print(NuevosPlatos)

Platos2= ["Ceviche","Arroz con pollo","Causa","Arroz con cabrito","Tamal"]
Platos2.reverse()
print(Platos2)

#Copiar datos de una lista a otra
Platos3=Platos2.copy()
print(Platos3)
Platos4=Platos3[1:4:2] #[1::2]
print(Platos4)
