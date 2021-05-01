import os
'''contient une fonction d'envoit send(fd,tag,v)
une fonction de reception receive(fd) qui retourne tag et v recus
des fonctions pour savoir si on affiche ou non qqchose (avec les options -v et -q)
'''
MAXBYTES = 100 #provisoire

class ModeError(Exception): pass

def recoit(fd):
    '''reception et traitement d'un message
    
    Args:
        fd (file descriptor): descriptor of the input file
        
    Returns:
        tag (list): info about the file and the properties of the transmission (localName, cat, transmissionNumber)
        msg (string): content of the file'''

    dataRaw = str(os.read(fd, 100))[2:-1] #read the whole message

    #Tag
    tagRaw = dataRaw.split('\\n')[0] #Première ligne uniquement
    tagRawL = tagRaw.split(' ')
    tag = [tagRawL[0], tagRawL[1]] #localFileName and transmission category
    tag.append(tuple(map(int, tagRawL[2].split('_')))) #transmission num
    
    #Msg
    msg = dataRaw[len(tagRaw)+2:] #Everything but the first line
    
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

    if tag[1] == 'r' or tag[1] == 'l' or tag[1] == 'f':
        content = "{} {} {}_{}\n{}".format(tag[0], tag[1], tag[2][0], tag[2][1], v)
    else:
        raise ModeError("The send mode isn't of the followings: [f=file, r=dir, l=list]")

    fd.write(content)
    return(0)
