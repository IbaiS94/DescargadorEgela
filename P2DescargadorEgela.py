import os
import re
import sys
import urllib.parse

import requests
from getpass import getpass
from colorama import Fore
from bs4 import BeautifulSoup
from pick import pick
from tqdm import tqdm
import os


"""
 Nombre: Ibai Sologuestoa Aguirrebeita
 Asignatura | Grupo: Sistemas Web | Grupo 1
 Fecha de Entrega: 23/03/2024
 Nombre de la Tarea: 2.Práctica: Buscar Información en eGela
 Descripción: El objetivo de esta práctica es realizar un programa en Python
 que permita descargar los archivos de la asignatura de sistemas web de la plataforma eGela,
 teniendo en cuenta las secciones y otras cosas (Se ha optado por mejorar el programa y ahora puede
 descargar archivos de cualquier asignatura).
"""

# Solicitar usuario y contraseña
usuario = sys.argv[1]
nombre = sys.argv[2]
nombre = nombre.upper()
contraseña = getpass("Introduce tu contraseña: ")
flag = False
secciones = BeautifulSoup("", 'html.parser')


def requestWeb(metodo, uri, cabeceras, cuerpo):
    cuerpo_encoded = urllib.parse.urlencode(cuerpo)
    cabeceras['Content-Length'] = str(len(cuerpo_encoded))
    respuesta = requests.request(metodo, uri, headers=cabeceras,data=cuerpo_encoded, allow_redirects=False)
    return respuesta
def Pet1():
    a = requestWeb('GET', "https://egela.ehu.eus/login/index.php",{'Host': 'egela.ehu.eus'},{})
    MoodleS = a.cookies.get('MoodleSessionegela')
    url = a.url
    soup = BeautifulSoup(a.text, 'html.parser')
    tag = soup.find('input', {'name': 'logintoken'})
    valuelogin = tag['value']
    print(Fore.MAGENTA+"---PETICIÓN 1---"+Fore.RESET)
    print(a.request.method + " " + a.request.url)
    print(Fore.GREEN+str(a.status_code)+" "+a.reason+Fore.RESET)
    print(str(a.headers.get('Set-Cookie')))
    return MoodleS, valuelogin, url
def Pet2(codMoodle, valuelogin, valuser, valpass, url):
    cuerpo = {'logintoken': valuelogin, 'username': valuser, 'password': valpass}
    b = requestWeb('POST', url, {'Host': 'egela.ehu.eus', 'Content-Type': 'application/x-www-form-urlencoded', 'Cookie': 'MoodleSessionegela=' + codMoodle}, cuerpo)
    print(Fore.MAGENTA+"---PETICIÓN 2---"+Fore.RESET)
    print(b.request.method + " " + b.request.url)
    print(b.request.body)
    print(Fore.YELLOW+str(b.status_code)+" "+b.reason+Fore.RESET)
    print(str(b.headers.get("Location"))+" "+str(b.headers.get('Set-Cookie')))
    return b.headers['Location'], b.cookies.get('MoodleSessionegela')
def Pet3(codMoodle, url):
    c = requestWeb('GET', url,{'Host':'egela.ehu.eus', 'Cookie':'MoodleSessionegela='+codMoodle},{})
    url2 = c.headers.get("Location")
    print(Fore.MAGENTA+"---PETICIÓN 3---"+Fore.RESET)
    print(c.request.method + " " + c.request.url)
    print(Fore.YELLOW+str(c.status_code)+" "+c.reason+Fore.RESET)
    print(str(c.headers.get("Location")))

    return url2
def Pet4(codMoodle, url):
    d = requestWeb('GET', url,{'Host':'egela.ehu.eus', 'Cookie':'MoodleSessionegela='+codMoodle},{})
    print(Fore.MAGENTA+"---PETICIÓN 4---"+Fore.RESET)
    print(d.request.method + " " + d.request.url)
    print(Fore.GREEN+str(d.status_code)+" "+d.reason+Fore.RESET)
    if(re.search(nombre, d.text) is not None):
        print(Fore.GREEN+"Autenticación correcta, se ha encontrado el nombre en la página"+Fore.RESET)
        return d.content
    else:
        print(Fore.RED+"Autenticación incorrecta, no se ha encontrado el nombre en la página, se procede a salir"+Fore.RESET)
        exit()


def menuCursos(html):
        html= html.decode('utf-8') 
        busqueda = r'<a class="ehu-visible" href="([^"]+)">([^<]+)</a>'
        aciertos = re.findall(busqueda, html)
        lista = []
        listaLinks = []
        for acierto in aciertos:
            lista.append(acierto[1])
            listaLinks.append(acierto[0])
        index = pick(lista, title="Cursos de "+ nombre, indicator='->', default_index=0)
        nombreasignatura  = lista[index[1]]
        print("Has seleccionado el curso: "+Fore.CYAN+nombreasignatura+Fore.RESET)
        urlasignatura = listaLinks[index[1]]
        print("URL: "+Fore.CYAN+urlasignatura+Fore.RESET)
        return urlasignatura, nombreasignatura   
def Pet5(urlasignatura, newMoodleS):
    f = requestWeb('GET', urlasignatura,{'Host':'egela.ehu.eus', 'Cookie':'MoodleSessionegela='+newMoodleS},{})
    print(Fore.MAGENTA+"---PETICIÓN 5---"+Fore.RESET)
    print(f.request.method + " " + f.request.url)
    print(Fore.GREEN+str(f.status_code)+" "+f.reason+Fore.RESET)
    with open('asignatura.html', 'wb') as g:
        g.write(f.content)
        g.close()
    
def Pet6(urltarea, newMoodleS):
    h = requestWeb('GET', urltarea,{'Host':'egela.ehu.eus', 'Cookie':'MoodleSessionegela='+newMoodleS},{})
    if h.status_code == 303:
        i = requestWeb('GET', h.headers.get("Location"),{'Host':'egela.ehu.eus', 'Cookie':'MoodleSessionegela='+newMoodleS},{})
        """
        print(Fore.MAGENTA+"---PETICIÓN 6---"+Fore.RESET) """  
        print(i.request.method + " " + i.request.url)
        print(Fore.GREEN+str(i.status_code)+" "+i.reason+Fore.RESET) 
        return h.headers.get("Location"), i.content
    else:
        """
        print(Fore.MAGENTA+"---PETICIÓN 6---"+Fore.RESET) """  
        print(h.request.method + " " + h.request.url)
        print(Fore.GREEN+str(h.status_code)+" "+h.reason+Fore.RESET)      
        return h.content
def BuscarArchivos(newMoodleS, nombreasignatura, archivo):
    global flag
    global secciones
    with open(archivo, 'r', encoding='utf-8') as fichero:
        cont = fichero.read()
        soup = BeautifulSoup(cont, 'html.parser')              
        """Se busca la sección actual en la que se encuentra el usuario"""
        seccionesbck = secciones
        secciones = soup.find_all('a', {'aria-current':'page'})
        if 'title' in secciones[0].attrs:
            secciones = seccionesbck
        if flag:
            soup = soup.find_all('span', {'class':'fp-filename-icon'})
            soup = [link.find('a') for link in soup]
        else:
            soup = soup.find_all('a', {'class':'aalink'})
                
        fichero.close()
        if not os.path.exists("./Datos " + nombreasignatura + "/" + secciones[0].text + "/"):
            os.makedirs("./Datos " + nombreasignatura + "/" + secciones[0].text + "/")
        for link in tqdm(soup, desc="Descargando archivos de la sección "+secciones[0].text):
            try:
                h, i= Pet6(link['href'], newMoodleS)
            except Exception:
                """Aqui se gestiona si la seccion tiene carpetas"""
                if flag == False:    
                    h = Pet6(link['href'], newMoodleS)
                    with open('carpeta.html', 'wb') as f:
                        f.write(h)
                        f.close()
                    flag = True
                    BuscarArchivos(newMoodleS, nombreasignatura,"carpeta.html")
                    flag = False
                    continue
                else:
                    h = link['href']
                    i = Pet6(link['href'], newMoodleS)

            if re.search(r'/([^/]+)$', h) and i is not None:
                fnombre = h.split('?')[0]
                fnombre = re.search(r'/([^/]+)$', fnombre).group(1)
                fnombre = urllib.parse.unquote(fnombre)
                if fnombre.endswith('.pdf'):
                    if not os.path.exists("./Datos " + nombreasignatura + "/" + secciones[0].text +  "/PDFs/"):
                        os.makedirs("./Datos " + nombreasignatura + "/" + secciones[0].text +  "/PDFs/")
                    with open("./Datos " + nombreasignatura +"/"+ secciones[0].text +  "/PDFs/" + fnombre, 'wb') as file:
                        file.write(i)
                        file.close()
                else:
                    if not os.path.exists("./Datos " + nombreasignatura + "/"+ secciones[0].text + "/Otros/"):
                        os.makedirs("./Datos " + nombreasignatura + "/" + secciones[0].text + "/Otros/")
                    with open("./Datos " + nombreasignatura + "/" + secciones[0].text + "/Otros/" + fnombre, 'wb') as file:
                        file.write(i)
                        file.close()
def BuscarSecciones(urlasignatura, newMoodleS):
    for i in range(0, 8):
        url = urlasignatura + "&section=" + str(i)
        f = requestWeb('GET', url,{'Host':'egela.ehu.eus', 'Cookie':'MoodleSessionegela='+newMoodleS},{})
        if f.status_code == 200:
            with open('asignatura.html', 'wb') as g:
                g.write(f.content)
                g.close()
            BuscarArchivos(newMoodleS, nombreasignatura,"asignatura.html")
        else:
            break
    
MoodleS, valuelogin, url = Pet1()
url, newMoodleS = Pet2(MoodleS,valuelogin,usuario,contraseña,url)
try:
    url = Pet3(newMoodleS,url)
    html = Pet4(newMoodleS, url)
    urlasignatura, nombreasignatura = menuCursos(html)
    Pet5(urlasignatura, newMoodleS)
    BuscarSecciones(urlasignatura, newMoodleS)
    print(Fore.GREEN+"Descarga completada"+Fore.RESET)
except TypeError:
    print(Fore.RED+"ERROR: Contraseña incorrecta o usuario incorrecto"+Fore.RESET) 
except Exception as e:
    print(Fore.RED+"ERROR :", str(e)+Fore.RESET)
