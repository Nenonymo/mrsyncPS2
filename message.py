import os
'''contient une fonction d'envoit send(fd,tag,v)
une fonction de reception receive(fd) qui retourne tag et v recus
des fonctions pour savoir si on affiche ou non qqchose (avec les options -v et -q)
'''
MAXBYTES = 100 #provisoire

def recoit(fd):
    v = os.read(fd,MAXBYTES)
    #fonction de reception d'un message
    return tag,msg

def envoit(fd,tag,v):
    #a preciser, le tag ne sera pas tjr le nom
    if os.path.isfile(tag):
        file = open(tag)
        #envoit le contenu du fichier
    elif tag == "liste" or tag=="listef":
        
        #envoit le fichier v
