import os, sys

def parser(args) :
    args = args[1:]
    fichiers = []
    arguments = []
    if len(args) > 1 :
        for i in args :
            if i[0] == '-' :
                arguments += [i]
            else :
                fichiers += [i]
    if len(fichiers) == 0 :
        raise Exception('Pas de fichier')
    elif len(fichiers) > 1 :
        destination = fichiers[-1]
        fichiers = fichiers[:-1]
    else :
        destination = '.'
    
    return arguments, fichiers, destination

if __name__ == '__main__' :
    arg, files, dest = parser(sys.argv)
    
    
