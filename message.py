import os,socket
'''fonctions d'envoit, de reception et de transformation de chaine de caractere en autre chose
'''

class ModeError(Exception): pass

def recoit(fd):
    '''reception et traitement d'un message
    
    Args:
        fd (file descriptor): descriptor of the input file
        
    Returns:
        tag (list): info about the file and the properties of the transmission (localName, cat, transmissionNumber)
        msg (string): content of the file'''

    taille = os.read(fd,32) #reception de la taille du paquet
    taille = taille.decode('utf-8')
    comSize = taille.split('r')[0]
    comSize = int(comSize) #taille du paquet

    dataRaw = os.read(fd, comSize) #read the whole message
    dataRaw = dataRaw.decode('utf-8')
    #Tag
    tagRaw = (dataRaw.split('\n')[0]) #Première ligne uniquement
    tagRawL = tagRaw.split(' ')
    tag = [tagRawL[0], tagRawL[1]] #localFileName and transmission category
    tag.append(tuple(map(int, tagRawL[2].split('_')))) #transmission num
    
    #Msg
    msg = (dataRaw[len(tagRaw)+1:]) #Everything but the first line
    return tag,msg


def envoit(fd,tag,v=''):
    '''Wrtiting the message on the pipe

    Args:
        fd (file descriptor): descriptor of the output pipe, must be opened with `fd = os.fdopen(fd, 'w')`
        tag (struct): info about the file and the properties of the transmission (localName, cat, transmissionNumber)
        v (string): content to write
    
    Returns:
        None
    '''

    if tag[1] == 'r' or tag[1] == 'l' or tag[1] == 'f' or tag[1] == 's': #on verifie qu'on a un mode valide (r = repertoire, l = liste, f = fichier, s = lien symbolique)
        content = "{} {} {}_{}\n{}".format(tag[0], tag[1], tag[2][0], tag[2][1], v)
    else:
        raise ModeError("The send mode isn't of the followings: [f=file, r=dir, l=list, s=symlink]")
    content = bytes(content,'utf-8') #tag + message
    nbr = str(len(content))
    clp = 32 - len(nbr)
    nbr = (nbr + clp*"r").encode('utf-8') #taille du paquet
    os.write(fd,nbr) #envoit de la taille sur 32 octets
    os.write(fd,content) #envoit du paquet
    return(0)


def envoit_socket(soc, tag, v=''):
    '''Wrtiting the message on the socket soc

    Args:
        soc (socket descriptor): descriptor of the output socket
        tag (struct): info about the file and the properties of the transmission (localName, cat, transmissionNumber)
        v (string): content to write
    
    Returns:
        None
    '''
    if tag[1] == 'r' or tag[1] == 'l' or tag[1] == 'f' or tag[1] == 's':
        content = "{} {} {}_{}\n{}".format(tag[0], tag[1], tag[2][0], tag[2][1], v)
    else:
        raise ModeError("The send mode isn't of the followings: [f=file, r=dir, l=list]")
    content = bytes(content,'utf-8')
    taille = str(len(content))
    clp = 32 - len(taille)
    taille = (taille + clp*"r").encode('utf-8')
    soc.send(taille)           #packet size
    soc.send(content)          #packet

    return(0)


def recoit_socket(soc):
    '''reception et traitement d'un message
    
    Args:
        soc (socket descriptor): descriptor of the input socket
        
    Returns:
        tag (list): info about the file and the properties of the transmission (localName, cat, transmissionNumber)
        msg (string): content of the file'''

    taille = soc.recv(32)   #size of the incomming packet
    taille = taille.decode('utf-8')
    comSize = taille.split('r')[0]
    comSize = int(comSize)

    dataRaw = soc.recv(comSize) #read the whole message
    dataRaw = dataRaw.decode('utf-8')

    #Tag
    tagRaw = (dataRaw.split('\n')[0]) #Première ligne uniquement
    tagRawL = tagRaw.split(' ')
    tag = [tagRawL[0], tagRawL[1]] #localFileName and transmission category
    tag.append(tuple(map(int, tagRawL[2].split('_')))) #transmission num
    
    #Msg
    msg = (dataRaw[len(tagRaw)+1:]) #Everything but the first line
    
    return tag,msg


def str_to_fic(v):
    '''convertit une chaine en fichier (represente par un dictionnaire)
    la chaine de caractère doit avoir une forme de fichier ({a:b,c:d......})

    input : v = la chaine de caractere a convertir (string)
    output : d = le fichier associé a v (fichier, dictionnaire)
    '''
    v = v[1:-1].split(',')
    d=dict()
    for i in range(len(v)):
        e = v[i].split(':')
        if i == 0 :
            d[e[0][1:-1]]=e[1][2:-1]
        elif i == 1 :
            d[e[0][2:-1]]=e[1][2:-1]
        elif i == len(v)-2:
            d[e[0][2:-1]]=float(e[1][1:])
        elif i == len(v)-1:
            d[e[0][2:-1]]=float(e[1][1:])
        else :
            d[e[0][2:-1]]=int(e[1][1:])
    return d  

def str_to_dic(v):
    '''converti une chaine en dictionnaire d'options
    la chaine de caractère doit avoir une forme de dictionnaire d'option ({a:b,c:d......})

    input : v = la chaine de caractere a convertir (string)
    output : d = le dictionnaire d'option associé a v (dictionnaire)
    '''
    v = v[1:-1].split(',')
    d=dict()
    for i in range(len(v)):
        e = v[i].split(':') 
        if i == 0 :
            d[e[0][1:-1]]=int(e[1][1:])
        elif i == 1:
            d[e[0][2:-1]]=int(e[1][1:])
        elif i == len(v)-1:
            try :
                d[e[0][2:-1]]=int(e[1][1:])
            except :
                d[e[0][2:-1]]=e[1][2:-1]
        elif i == len(v) - 2 :
            d[e[0][2:-1]]=e[1][2:-1]
        else :
            if e[1][1:] == 'False':
                d[e[0][2:-1]]= False
            else :
                d[e[0][2:-1]]= True
    return d

def str_to_list(v):
    '''converti une chaine en liste
    la chaine de caractère doit avoir une forme de liste de chaine de caractere [a,b...]

    input : v = la chaine de caractere a convertir (string)
    output : l = la liste associé a v (liste)
    '''
    v = v[1:-1]
    l = []
    i = 1
    mot = ''
    while i < len(v):
        if v[i]== ",":  
            if v[i-1] == "'" and v[i-2] != "\\": 
                l.append(mot[:-1])
                mot = ''
                i = i+3
            else:
                mot = mot + v[i]
                i += 1
        else :
            mot = mot + v[i]
            i+=1
    l.append(mot[:-1])
    return l

def str_to_diclist(v): 
    '''convertit une chaine de caractere en une liste de fichiers (represente par un dictionnaire)
    la chaine de caractère doit avoir une forme de liste ([a,b,...])
    avec a et b des fichiers

    input : v = la chaine de caractere a convertir (string)
    output : l = la liste associée a v (liste de fichiers, liste de dictionnaires)
    '''
    v = v[1:-1].split(',')
    i=0
    j=0
    l=[]
    while i < len(v):
        e = v[i].split(':')
        if e[0][0] == '{':
            j=0
            l1 = dict()
            l1[e[0][1:-1]]=e[1][2:-1]
        elif j == 1:
            l1[e[0][2:-1]]=e[1][2:-1]
        elif e[1][-1] == '}': 
            l1[e[0][2:-1]]=e[1][1:]
            l.append(l1)
        else :
            l1[e[0][2:-1]]=int(e[1][1:])
        i+=1
        j+=1
    return l