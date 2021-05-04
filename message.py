import os
'''contient une fonction d'envoit send(fd,tag,v)
une fonction de reception receive(fd) qui retourne tag et v recus
des fonctions pour savoir si on affiche ou non qqchose (avec les options -v et -q)
'''

class ModeError(Exception): pass

def recoit(fd, lineFile="comSize"):
    '''reception et traitement d'un message
    
    Args:
        fd (file descriptor): descriptor of the input file
        
    Returns:
        tag (list): info about the file and the properties of the transmission (localName, cat, transmissionNumber)
        msg (string): content of the file'''

    with open(lineFile, 'r') as f:
        n=f.readline()[:-1]
        while n == '':
            n = f.readline()[:-1]
        comSize = int(n)
        '''n=f.read()
        while n == '':
            n=f.read()
        comSize=int(n.split("\n")[0])'''

    os.system('sed -i 1d {}'.format(lineFile))

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

def envoit(fd,tag,lineFile="comSize",v=''):
    '''Wrtiting the message on the pipe

    Args:
        fd (file descriptor): descriptor of the output pipe, must be opened with `fd = os.fdopen(fd, 'w')`
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
    with open(lineFile, 'a') as f: #ecriture de la longueur du write
        f.write('{}\n'.format(len(content)))
    
    os.write(fd,content)

    return(0)

def str_to_dic(v):
    v = v[1:-1].split(',')
    d=dict()
    for i in range(len(v)):
        e = v[i].split(':')
        if i == 0 :
            d[e[0][1:-1]]=e[1][2:-1]
        elif i == 1:
            d[e[0][2:-1]]=e[1][2:-1]
        elif i == len(v)-1:
            d[e[0][2:-1]]=e[1][1:]
        else :
            d[e[0][2:-1]]=int(e[1][1:])
    return d

'''
Traceback (most recent call last):
  File "mrsyncPS2/mrsync.py", line 22, in <module>
    server.server_local(src,dest,dic,gs_g,sr_r)
  File "/home/gargaranza/Systeme2/mrsyncPS2/server.py", line 5, in server_local
    receiver.receive_local(dirs,dirr,dic,gs_g,sr_r)
  File "/home/gargaranza/Systeme2/mrsyncPS2/receiver.py", line 14, in receive_local
    file_lists.append(message.str_to_dic(data))
  File "/home/gargaranza/Systeme2/mrsyncPS2/message.py", line 79, in str_to_dic
    d[e[0][2:-1]]=e[1][1:]
IndexError: list index out of range
'''
