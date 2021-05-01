import os

def appToFile(file, v): #Ajoute v au fichier d'adresse file
    '''append 'v' to the local file'''
    with open(file, 'a') as f:
        f.write(v)

def getPidList(file):
    '''Get the pid values stored in the file.

    Args:
        file (str): path to the local file where the PIDs are stored. The file must be like this:
            a1:[pid]
            b1:[pid2]
            (each pid identified by a 2chars string)

    Returns:
        A dictionnary with the PIDs, indentified by a 2chars string.'''

    fd = os.open(file, os.O_RDONLY)
    txt = str(os.read(fd, 100))[2:]
    rep = dict()
    for l in txt.split(sep='\\n'):
        if l != "'":
            rep[l[0:2]] = int(l[3:])
    return(rep)