import streamlit as st
import os
import pandas as pd
import operator
from nltk.tokenize import word_tokenize
import string
import Stemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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
    for elemento in os.scandir("Codigo/Noticias/" + medio + "/" + categoria + "/"):        # Escanear la carpeta del medio y categoria seleccionadas, devolver todo el contenido
        lista.append(elemento.path)                                                 # Guardar las rutas de todos los ficheros de las carpetas, (DirEntry.path)
    return lista                                                                    # Devolver lista con todas las rutas de todos los ficheros de la carpeta

def rastrear_directorio(medio): 
    lista_noticias = []
    for item in os.scandir("Codigo/Noticias/" + medio):
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

def tokenizar_texto(ruta_noticia):
    texto = open(ruta_noticia, "r", encoding="utf8")
    lista_tokens = word_tokenize(texto.read().lower(), language="spanish")
    return lista_tokens

def tokenizar_busqueda(busqueda: str):
    lista_tokens = word_tokenize(busqueda.lower(), language="spanish")
    return lista_tokens


def limpiar_texto(lista_tokens: list):
    palabras = []
    fichero_parada = open("Codigo/Lista_Stop_Words.txt", "r", encoding="utf8")
    lista_parada = fichero_parada.read().split("\n")
    puntuacion = list(string.punctuation)
    lista_parada += puntuacion
    for palabra in lista_tokens:
        if palabra not in lista_parada:
            palabras.append(palabra)
    return palabras

def stemming(lista_palabras: list):
    texto = ""
    stemmer = Stemmer.Stemmer('spanish')
    for palabra in lista_palabras:
        s = stemmer.stemWord(palabra)
        texto = texto + " " + s
    return texto

def generar_coleccion(lista_textos):
    coleccion = []
    for texto in lista_textos:
        tokens = tokenizar_texto(texto)
        lista_limpia = limpiar_texto(tokens)
        texto = stemming(lista_limpia)
        coleccion.append(texto)
    return coleccion


def crear_vectores(coleccion_documentos: list, nombres_ficheros: list):
    tf = TfidfVectorizer()
    vector_idf = tf.fit_transform(coleccion_documentos).toarray() 
    matriz_idf = pd.DataFrame(vector_idf, columns=tf.get_feature_names_out())
    sim_coseno = cosine_similarity(matriz_idf)
    matriz_similitud = pd.DataFrame(sim_coseno, index=nombres_ficheros, columns=nombres_ficheros)
    return matriz_similitud.loc[nombres_ficheros[len(nombres_ficheros) - 1]]

def visualizar_resultados(serie: pd.Series):
    resultados = []
    serie = serie.sort_values(ascending=False)
    for fichero, similitud in serie.items():
        resultados.append(str(fichero) + "- Similitud: " + str(similitud))
    return resultados

#----------------------------------------------- Interfaz Aplicacion ------------------------------------
def main():
    paginas = {
    "pagina1": "Busquedas de Texto",
    "pagina2": "Noticias Similares/Recomendaciones Noticias"
    }

    pagina_selec = st.sidebar.radio("Selecciona la página", paginas.values())

    if pagina_selec == paginas["pagina1"]:
        st.title("Búsqueda de Noticias")
        consulta = st.text_input("Consulta: ", placeholder="Texto a buscar")

        col1, col2, col3 = st.columns(3)
        with col1:
            n = st.selectbox("N Resultados: ", ["5", "7", "10"])
        with col2:
            medio = st.selectbox("Filtro: ", ["Todas", "El Pais", "El Mundo", "20 Minutos"])
        with col3:
            st.write("Buscar:")
            buscar = st.checkbox("Buscar")
        if buscar:
            textos = busqueda(medio)
            lista_tokens_busqueda = tokenizar_busqueda(consulta)
            texto_limpio = limpiar_texto(lista_tokens_busqueda)
            query = stemming(texto_limpio)
            coleccion = generar_coleccion(textos)
            coleccion.append(query)
            textos.append(consulta)
            similares_consulta = crear_vectores(coleccion, textos)
            resultados = visualizar_resultados(similares_consulta)
            ranking = st.selectbox("Ranking: ", resultados[1:int(n) + 1])
            indice_guion = ranking.rfind("-")
            noticia_resultado = ranking[:indice_guion]
            noticia_resultado = open(noticia_resultado, "r", encoding="utf8")
            st.text_area("Noticia", noticia_resultado.read(), height=200)

    elif pagina_selec == paginas["pagina2"]:
        st.title("Noticias Similares/Recomendación de Noticias")
        st.write("Seleccione una noticia de referencia: ")

        col1,col2,col3 = st.columns(3)

        with col1:
            medio = st.selectbox("Medio", ["El Pais", "El Mundo", "20 Minutos"])
        with col2:
            categoria = st.selectbox("Categoria", ["Tecnologia", "Ciencia", "Salud"])
        with col3:
            noticia = st.selectbox("Noticia", mostrar_noticias(medio, categoria))

        texto_noticia = open(noticia, "r", encoding="utf8")
        st.text_area("Preview Noticia", texto_noticia.read(), height=200)

        col1, col2, col3 = st.columns(3)
        
        with col1:
            medio = st.selectbox("Filtro: ", ["Todas", "El Pais", "El Mundo", "20 Minutos"])
        with col2:
            n = st.selectbox("N Resultados: ", ["5", "7", "10"])
        with col3:
            opcion = st.radio("Seleccione una opcion", ["Noticias Recomendadas", "Noticias Similares"])

        st.write("")
        
        if opcion == "Noticias Recomendadas":
            lista_noticias = busqueda(medio)
            res = guardar_resultados(noticia, lista_noticias)
            lista_resultados = mostrar_resultados(res)
            resultados = st.selectbox("Ranking: ", lista_resultados[:int(n)])
            indice_guion = resultados.rfind("-")
            noticia_resultado = resultados[:indice_guion]
            noticia_resultado = open(noticia_resultado, "r", encoding="utf8")
            st.text_area("Noticia", noticia_resultado.read(), height=200)
        elif opcion == "Noticias Similares": 
            lista_textos = busqueda(medio)
            lista_textos.append(noticia)
            coleccion = generar_coleccion(lista_textos)
            noticia_refencia = crear_vectores(coleccion, lista_textos)
            lista_similitudes = visualizar_resultados(noticia_refencia)
            ranking = st.selectbox("Ranking: ", lista_similitudes[:int(n)])
            indice_guion = ranking.rfind("-")
            noticia_resultado = ranking[:indice_guion]
            noticia_resultado = open(noticia_resultado, "r", encoding="utf8")
            st.text_area("Noticia", noticia_resultado.read(), height=200)
main()