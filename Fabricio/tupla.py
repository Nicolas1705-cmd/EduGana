#tupla -> ()
#Carácteristicas: Inmutables, ordenadas, permiten duplicados
#Tupla vacia
tuplavacia=()
print(tuplavacia)
print(type(tuplavacia))
miprimeratupla=(1,2,3,4,5,"Hola", True,2,5,2+5j)
print(miprimeratupla)
tuplaelemento=(45,)
print(tuplaelemento)
#Tuplas anidadas
tuplaanidada=(1,2,3,4),("Hola","Ciber"),(2.5,2.6)
print(tuplaanidada)
#Tupla de lista
tuplalista=([1,2,3,4],["Hola",True,2.6])
print(tuplalista)
tupladiccionario=({"Nombre:Fabricio"},{"Apellidos:Nuñez"})
print(tupladiccionario)
#Longitud e una tupla
tupla=(1,2,3,4,5)
print(len(tupla))
#Constructor de tuplas -> Tuple
numeros=tuple((1,2,3,4,5)) #Una tupla
print(numeros)
numeros=tuple(((1,2,3,4,5),(45,))) #Dos tuplas
print(numeros)
#Intercambio de valores con tuplas
a=5
b=6
(a,b)=(b,a)
print(a,b)
colores=("Azul","Rojo","Verde","Amarillo","Celeste")
print(colores[2])
print(colores[-4])
existe="Rojo" in colores #true
print(existe)
#Cambiar valores en una tupla
tuplanumero=(1,2,3,4,5)
listanumeros=list(tuplanumero)
listanumeros.append(6)
print(listanumeros)
tuplaactualizada=tuple(listanumeros)
print(tuplaactualizada)