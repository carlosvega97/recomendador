import streamlit as st
import os
import pandas as pd
import operator
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.snowball import SpanishStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
nltk.download('punkt')
nltk.download('stopwords')

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

def tokenizar_texto(ruta_noticia):
    texto = open(ruta_noticia, "r", encoding="utf8")
    lista_tokens = word_tokenize(texto.read().lower(), language="spanish")
    return lista_tokens


def limpiar_texto(lista_tokens: list):
    palabras = []
    lista = ["#", "@", ",", ".", "”", "“", "a", "actualmente", "adelante", "además", "afirmó", "agregó", "ahora", "ahí", "al", "algo", "alguna", "algunas", "alguno", "algunos", "algún", "alrededor", "ambos", "ampleamos", "ante", "anterior", "antes", "apenas", "aproximadamente", "aquel", "aquellas", "aquellos", "aqui", "aquí", "arriba", "aseguró", "así", "atras", "aunque", "ayer", "añadió", "aún", "bajo", "bastante", "bien", "buen", "buena", "buenas", "bueno", "buenos", "cada", "casi", "cerca", "cierta", "ciertas", "cierto", "ciertos", "cinco", "comentó", "como", "con", "conocer", "conseguimos", "conseguir", "considera", "consideró", "consigo", "consigue", "consiguen", "consigues", "contra", "cosas", "creo", "cual", "cuales", "cualquier", "cuando", "cuanto", "cuatro", "cuenta", "cómo", "da", "dado", "dan", "dar", "de", "debe", "deben", "debido", "decir", "dejó", "del", "demás", "dentro", "desde", "después", "dice", "dicen", "dicho", "dieron", "diferente", "diferentes", "dijeron", "dijo", "dio", "donde", "dos", "durante", "e", "ejemplo", "el", "ella", "ellas", "ello", "ellos", "embargo", "empleais", "emplean", "emplear", "empleas", "empleo", "en", "encima", "encuentra", "entonces", "entre", "era", "erais", "eramos", "eran", "eras", "eres", "es", "esa", "esas", "ese", "eso", "esos", "esta", "estaba", "estabais", "estaban", "estabas", "estad", "estada", "estadas", "estado", "estados", "estais", "estamos", "estan", "estando", "estar", "estaremos", "estará", "estarán", "estarás", "estaré", "estaréis", "estaría", "estaríais", "estaríamos", "estarían", "estarías", "estas", "este", "estemos", "esto", "estos", "estoy", "estuve", "estuviera", "estuvierais", "estuvieran", "estuvieras", "estuvieron", "estuviese", "estuvieseis", "estuviesen", "estuvieses", "estuvimos", "estuviste", "estuvisteis", "estuviéramos", "estuviésemos", "estuvo", "está", "estábamos", "estáis", "están", "estás", "esté", "estéis", "estén", "estés", "ex", "existe", "existen", "explicó", "expresó", "fin", "fue", "fuera", "fuerais", "fueran", "fueras", "fueron", "fuese", "fueseis", "fuesen", "fueses", "fui", "fuimos", "fuiste", "fuisteis", "fuéramos", "fuésemos", "gran", "grandes", "gueno", "ha", "haber", "habida", "habidas", "habido", "habidos", "habiendo", "habremos", "habrá", "habrán", "habrás", "habré", "habréis", "habría", "habríais", "habríamos", "habrían", "habrías", "habéis", "había", "habíais", "habíamos", "habían", "habías", "hace", "haceis", "hacemos", "hacen", "hacer", "hacerlo", "haces", "hacia", "haciendo", "hago", "han", "has", "hasta", "hay", "haya", "hayamos", "hayan", "hayas", "hayáis", "he", "hecho", "hemos", "hicieron", "hizo", "hoy", "hube", "hubiera", "hubierais", "hubieran", "hubieras", "hubieron", "hubiese", "hubieseis", "hubiesen", "hubieses", "hubimos", "hubiste", "hubisteis", "hubiéramos", "hubiésemos", "hubo", "igual", "incluso", "indicó", "informó", "intenta", "intentais", "intentamos", "intentan", "intentar", "intentas", "intento", "ir", "junto", "la", "lado", "largo", "las", "le", "les", "llegó", "lleva", "llevar", "lo", "los", "luego", "lugar", "manera", "manifestó", "mayor", "me", "mediante", "mejor", "mencionó", "menos", "mi", "mientras", "mio", "mis", "misma", "mismas", "mismo", "mismos", "modo", "momento", "mucha", "muchas", "mucho", "muchos", "muy", "más", "mí", "mía", "mías", "mío", "míos", "nada", "nadie", "ni", "ninguna", "ningunas", "ninguno", "ningunos", "ningún", "no", "nos", "nosotras", "nosotros", "nuestra", "nuestras", "nuestro", "nuestros", "nueva", "nuevas", "nuevo", "nuevos", "nunca", "o", "ocho", "os", "otra", "otras", "otro", "otros", "para", "parece", "parte", "partir", "pasada", "pasado", "pero", "pesar", "poca", "pocas", "poco", "pocos", "podeis", "podemos", "poder", "podria", "podriais", "podriamos", "podrian", "podrias", "podrá", "podrán", "podría", "podrían", "poner", "por", "por qué", "porque", "posible", "primer", "primera", "primero", "primeros", "principalmente", "propia", "propias", "propio", "propios", "próximo", "próximos", "pudo", "pueda", "puede", "pueden", "puedo", "pues", "que", "quedó", "queremos", "quien", "quienes", "quiere", "quién", "qué", "realizado", "realizar", "realizó", "respecto", "sabe", "sabeis", "sabemos", "saben", "saber", "sabes", "se", "sea", "seamos", "sean", "seas", "segunda", "segundo", "según", "seis", "ser", "seremos", "será", "serán", "serás", "seré", "seréis", "sería", "seríais", "seríamos", "serían", "serías", "seáis", "señaló", "si", "sido", "siempre", "siendo", "siete", "sigue", "siguiente", "sin", "sino", "sobre", "sois", "sola", "solamente", "solas", "solo", "solos", "somos", "son", "soy", "su", "sus", "suya", "suyas", "suyo", "suyos", "sí", "sólo", "tal", "también", "tampoco", "tan", "tanto", "te", "tendremos", "tendrá", "tendrán", "tendrás", "tendré", "tendréis", "tendría", "tendríais", "tendríamos", "tendrían", "tendrías", "tened", "teneis", "tenemos", "tener", "tenga", "tengamos", "tengan", "tengas", "tengo", "tengáis", "tenida", "tenidas", "tenido", "tenidos", "teniendo", "tenéis", "tenía", "teníais", "teníamos", "tenían", "tenías", "tercera", "ti", "tiempo", "tiene", "tienen", "tienes", "toda", "todas", "todavía", "todo", "todos", "total", "trabaja", "trabajais", "trabajamos", "trabajan", "trabajar", "trabajas", "trabajo", "tras", "trata", "través", "tres", "tu", "tus", "tuve", "tuviera", "tuvierais", "tuvieran", "tuvieras", "tuvieron", "tuviese", "tuvieseis", "tuviesen", "tuvieses", "tuvimos", "tuviste", "tuvisteis", "tuviéramos", "tuviésemos", "tuvo", "tuya", "tuyas", "tuyo", "tuyos", "tú", "ultimo", "un", "una", "unas", "uno", "unos", "usa", "usais", "usamos", "usan", "usar", "usas", "uso", "usted", "va", "vais", "valor", "vamos", "van", "varias", "varios", "vaya", "veces", "ver", "verdad", "verdadera", "verdadero", "vez", "vosotras", "vosotros", "voy", "vuestra", "vuestras", "vuestro", "vuestros", "y", "ya", "yo", "él", "éramos", "ésta", "éstas", "éste", "éstos", "última", "últimas", "último", "últimos"]
    lista_parada = set(stopwords.words('spanish'))
    lista_parada.update(lista)
    for palabra in lista_tokens:
        if palabra not in lista_parada:
            palabras.append(palabra)
    return palabras

def stemming(lista_palabras: list):
    texto = ""
    stemmer = SpanishStemmer()
    for palabra in lista_palabras:
        s = stemmer.stem(palabra)
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
paginas = {
  "pagina1": "Busquedas de Texto",
  "pagina2": "Noticias Similares/Recomendaciones Noticias"
}

pagina_selec = st.sidebar.radio("Selecciona la página", paginas.values())

if pagina_selec == paginas["pagina1"]:
    st.title("Busqueda de Noticias")
    st.text_input("Consulta: ", placeholder="Texto a buscar")

    col1, col2, col3 = st.columns(3)
    with col1:
        n = st.selectbox("N Resultados: ", ["5", "7", "10"])
    with col2:
        medio = st.selectbox("Filtro: ", ["Todas", "El Pais", "El Mundo", "20 Minutos"])
    with col3:
        st.write("Buscar:")
        buscar = st.button("Buscar")

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
    st.text_area("Preview Noticia", texto_noticia.read())

    col1, col2, col3 = st.columns(3)
    with col2:
        n = st.selectbox("N Resultados: ", ["5", "7", "10"])

    st.write("")

    col1,col2,col3 = st.columns(3)

    with col1:
        medio = st.selectbox("Filtro: ", ["Todas", "El Pais", "El Mundo", "20 Minutos"])
    with col3:
        recomenadciones = st.checkbox("Noticas recomendadas")
        comparaciones = st.checkbox("Noticias Similares")
    
    if recomenadciones:
        lista_noticias = busqueda(medio)
        res = guardar_resultados(noticia, lista_noticias)
        lista_resultados = mostrar_resultados(res)
        resultados = st.selectbox("Ranking: ", lista_resultados[:int(n)])
        indice_guion = resultados.index("-")
        noticia_resultado = resultados[:indice_guion]
        noticia_resultado = open(noticia_resultado, "r", encoding="utf8")
        st.text_area("Noticia", noticia_resultado.read())
    if comparaciones: 
        lista_textos = busqueda(medio)
        lista_textos.append(noticia)
        coleccion = generar_coleccion(lista_textos)
        noticia_refencia = crear_vectores(coleccion, lista_textos)
        lista_similitudes = visualizar_resultados(noticia_refencia)
        ranking = st.selectbox("Ranking: ", lista_similitudes[:int(n)])
        indice_guion = ranking.index("-")
        noticia_resultado = ranking[:indice_guion]
        noticia_resultado = open(noticia_resultado, "r", encoding="utf8")
        st.text_area("Noticia", noticia_resultado.read())
