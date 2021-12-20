#Glosario de imports

from bs4 import BeautifulSoup
import requests
import re
import os
from datetime import datetime

#Metodos sacar URL's de cada medio

def lista_urls_pais(url):
    lista = [] 
    html = requests.get(url)

    web = BeautifulSoup(html.text, 'html.parser')
    noticias = web.find_all("h2", class_="c_t")
    

    for url in noticias:
        url_noticia = url.find('a').get('href')
        url_noticia = "https://elpais.com" + url_noticia
        lista.append(url_noticia)
    return lista

def lista_urls_20minutos(url):
    lista = [] 
    html = requests.get(url)

    web = BeautifulSoup(html.text, 'html.parser')
    noticias = web.find_all("div", class_="media-content")
    
    for url in noticias:
        url_noticia = url.find('a').get('href')
        lista.append(url_noticia)
    return lista

def lista_urls_elmundo(url):
    lista = [] 
    html = requests.get(url)

    web = BeautifulSoup(html.text, 'html.parser')
    noticias = web.find_all("a", class_="ue-c-cover-content__link-whole-content")
    
    for url in noticias:
        url_noticia = url.get('href')
        lista.append(url_noticia)
    return lista

#Llamada a los metodos que sacan las URL's
       
lista_ciencia_pais = lista_urls_pais("https://elpais.com/ciencia/")
lista_tecnologia_pais = lista_urls_pais("https://elpais.com/tecnologia/")
lista_salud_pais = lista_urls_pais("https://elpais.com/noticias/salud/")

lista_salud_20minutos = lista_urls_20minutos("https://www.20minutos.es/salud/")
lista_ciencia_20minutos = lista_urls_20minutos("https://www.20minutos.es/ciencia/")
lista_tecnologia_20minutos = lista_urls_20minutos("https://www.20minutos.es/tecnologia/")

lista_ciencia_elmundo = lista_urls_elmundo("https://www.elmundo.es/ciencia-y-salud/ciencia.html")
lista_tecnologia_elmundo = lista_urls_elmundo("https://www.elmundo.es/tecnologia.html")
lista_salud_elmundo = lista_urls_elmundo("https://www.elmundo.es/ciencia-y-salud/salud.html")

#Metodos guardar noticias de cada medio 

def guardar_noticias_pais(lista_urls, tipo):
    index = 0
    for url in lista_urls:
        html = requests.get(url)
        web = BeautifulSoup(html.text, 'html.parser')
        
        try:
            tags = web.find('meta', property="news_keywords").attrs['content']
            titulo = web.find('h1', class_="a_t").text
            entradilla = web.find('h2', class_="a_st").text
            cuerpo = ""
            
            for para in web.find_all("p", class_=""):
                cuerpo = cuerpo + para.get_text()
                cuerpo = re.sub("Puedes seguir a EL PAÍS TECNOLOGÍA en Facebook y Twitter o apuntarte aquí para recibir nuestra newsletter semanal.", "", cuerpo)
                cuerpo = re.sub("Suscríbete y lee sin límites", "", cuerpo)    
            
        except:
            tags = ""
            titulo = ""
            entradilla = "" 
        
        noticia = titulo + "\n######\n" + entradilla + "\n######\n" + cuerpo + "\n######\n" + tags 
        directory = "Noticias/El Pais/" + tipo + "/"
        file = open(str(directory) + tipo + "." + datetime.today().strftime('%Y-%m-%d') + "." + "{:03d}".format(index) + ".txt", "w", encoding="utf-8")
        file.write(noticia)
        file.close()
        index = index + 1
        
        
def guardar_noticias_20minutos(lista_urls, tipo):
    index = 0
    for url in lista_urls:
        html = requests.get(url)
        web = BeautifulSoup(html.text, 'html.parser')
        
        try:
            tags = web.find("meta",  {"name":"news_keywords"}).attrs['content']
            titulo = web.find("meta",  {"property":"og:title"}).attrs['content']
            entradilla = web.find('div', class_="article-intro").text
            cuerpo= ""
            for para in web.find_all('p', class_="paragraph"):
                cuerpo = cuerpo + para.get_text()
                cuerpo = re.sub("Apúntate a nuestra newsletter y recibe en tu correo las últimas noticias sobre tecnología.", "", cuerpo)             
            
        except:
            tags = ""
            titulo = ""
            entradilla = "" 
        
        noticia = titulo + "\n######\n" + entradilla + "\n######\n" + cuerpo + "\n######\n" + tags  
        directory = "Noticias/20 Minutos/" + tipo + "/"
        file = open(str(directory) + tipo + "." + datetime.today().strftime('%Y-%m-%d') + "." + "{:03d}".format(index) + ".txt", "w", encoding="utf-8")
        file.write(noticia)
        file.close()
        index = index + 1

        
def guardar_noticias_mundo(lista_urls, tipo):
    index = 0
    for url in lista_urls:
        html = requests.get(url)
        web = BeautifulSoup(html.text, 'html.parser')
        
        etiquetas = ""
        tags = web.find_all('li', class_="ue-c-article__tags-item")
        titulo = web.find('h1', class_="ue-c-article__headline js-headline")
        entradilla = web.find('p', class_="ue-c-article__standfirst")

        if titulo == None:
            titulo = ""
        else:
            titulo = titulo.text

        if entradilla == None:
            entradilla = ""
        else:
            entradilla = entradilla.text
        if tags == None:
            tags = ""
        else:
            for t in tags:
                etiquetas = etiquetas + ", " + t.get_text()

        cuerpo= ""
        for para in web.find_all('p', class_=""):
            cuerpo = cuerpo + para.get_text()                      

        noticia = titulo + "\n######\n" + entradilla + "\n######\n" + cuerpo + "\n######\n" + etiquetas  
        directory = "Noticias/El Mundo/" + tipo + "/"
        file = open(str(directory) + tipo + "." + datetime.today().strftime('%Y-%m-%d') + "." + "{:03d}".format(index) + ".txt", "w", encoding="utf-8")
        file.write(noticia)
        file.close()
        index = index + 1
        
#Llamada a los metodos que guardan las noticias

guardar_noticias_pais(lista_tecnologia_pais, "tecnologia")
guardar_noticias_pais(lista_ciencia_pais, "ciencia")
guardar_noticias_pais(lista_salud_pais, "salud")

guardar_noticias_20minutos(lista_tecnologia_20minutos, "tecnologia")
guardar_noticias_20minutos(lista_ciencia_20minutos, "ciencia")
guardar_noticias_20minutos(lista_salud_20minutos, "salud")

guardar_noticias_mundo(lista_tecnologia_elmundo, "tecnologia")
guardar_noticias_mundo(lista_ciencia_elmundo, "ciencia")
guardar_noticias_mundo(lista_salud_elmundo, "salud")
 
 