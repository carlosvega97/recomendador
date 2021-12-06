import streamlit as st
import os
import pandas as pd
import operator

#------------------------------------------ Funciones ----------------------------------------------------
def extraer_etiquetas(ruta_noticia):
    noticia = open(ruta_noticia, "r", encoding="utf8")      # Abrir y leer el fichero que se pasa por parametro
    etiquetas = noticia.readlines()[-1]                     # Etiquetas de noticia estan en la ultima linea del fichero de texto
    lista_etiquetas = etiquetas.split(",")                  # Se crea un lista con todas las etiquetas de la noticia
    return lista_etiquetas

def guardar_resultados(noticia_referencia, lista):
    res = {}
    etiquetas_noticia = extraer_etiquetas(noticia_referencia)
    for noticia in lista:
        lista_etiquetas = extraer_etiquetas(noticia)
        res[noticia] = simlitud_dice(etiquetas_noticia, lista_etiquetas)
    return res

def mostrar_resultados(diccionario: dict):
    lista_ranking = []
    resultados = sorted(diccionario.items(), key=operator.itemgetter(1), reverse=True)
    ranking = {k: v for k, v in resultados}
    for noticia, similitud in ranking.items():
        lista_ranking.append(str(noticia) + "- " + "Similitud: " + str(similitud))
    return lista_ranking


def simlitud_dice(etiquetas_texto1, etiquetas_texto2):
    a = set(etiquetas_texto1)
    b = set(etiquetas_texto2)

    return (2*len(a.intersection(b)))/((len(a))+len(b))

def mostrar_noticias(medio, categoria):
    lista = []
    for elemento in os.scandir("Noticias/" + medio + "/" + categoria + "/"):        # Escanear la carpeta del medio y categoria seleccionadas, devolver todo el contenido
        lista.append(elemento.path)                                                 # Guardar las rutas de todos los ficheros de las carpetas, (DirEntry.path)
    return lista                                                                    # Devolver lista con todas las rutas de todos los ficheros de la carpeta

def rastrear_directorio(medio): 
    lista_noticias = []
    for item in os.scandir("Noticias/" + medio):
        carpeta = os.scandir(item)
        for fichero in carpeta:
            lista_noticias.append(fichero.path)
    return lista_noticias 

def busqueda(filtro):
    lista = []
    if filtro == "Todas":
        pais = rastrear_directorio("El Pais")
        mundo = rastrear_directorio("El Mundo")
        minutos = rastrear_directorio("20 Minutos")
        lista = pais + mundo + minutos
    else: 
        lista = rastrear_directorio(filtro)
    return lista

#----------------------------------------------- Interfaz Aplicacion ------------------------------------
paginas = {
  "pagina1": "Busquedas de Texto",
  "pagina2": "Recomendaciones Noticias"
}

pagina_selec = st.sidebar.radio("Selecciona la página", paginas.values())

if pagina_selec == paginas["pagina1"]:
    st.title("Busqueda de Noticias")

elif pagina_selec == paginas["pagina2"]:
    st.title("Recomendación de Noticias")
    st.write("Seleccione una noticia de referencia: ")

    col1,col2,col3 = st.columns(3)

    with col1:
        medio = st.selectbox("Medio", ["El Pais", "El Mundo", "20 Minutos"])
    with col2:
        categoria = st.selectbox("Categoria", ["Tecnologia", "Ciencia", "Salud"])
    with col3:
        noticia = st.selectbox("Noticia", mostrar_noticias(medio, categoria))

    texto_noticia = open(noticia, "r", encoding="utf8")
    st.text_area("Preview Noticia", texto_noticia.read())

    col1, col2, col3 = st.columns(3)
    with col1:
        n = st.selectbox("N Resultados: ", ["5", "7", "10"])

    st.write("")


    medio = st.selectbox("Filtro: ", ["Todas", "El Pais", "El Mundo", "20 Minutos"])


    lista_noticias = busqueda(medio)
    res = guardar_resultados(noticia, lista_noticias)
    lista_resultados = mostrar_resultados(res)
    resultados = st.selectbox("Ranking: ", lista_resultados[:int(n)])
    indice_guion = resultados.index("-")
    noticia_resultado = resultados[:indice_guion]
    noticia_resultado = open(noticia_resultado, "r", encoding="utf8")
    st.text_area("Noticia", noticia_resultado.read())