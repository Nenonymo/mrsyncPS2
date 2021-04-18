import os, sys

def parser(args) :
    args = args[1:]
    fichiers = []
    arguments = []
    dic = {'-v':False, '-q':False, '-a':False, '-r':False, '-u':False, '-d':False, '-H':False, '-p':False, '-t':False, '--times':False, '--existing':False, '--ignore-existing':False, '--delete':False, '--force':False, '--timeout':0, '--blocking-io':False, '-I':False, '--ignore-times':False, '--size-only':False, '--adress':'', '--port':'', '--list-only':False, '-h':False,}
    for i in args :
        if i[0] == '-' :
            arguments += [i]
        else :
            if os.path.isdir(i) and i[-1] != '/' :
                fichiers += [i + '/']
            else :
                fichiers += [i]
    if len(fichiers) == 0 :
        raise Exception('Pas de fichier')
    elif len(fichiers) > 1 :
        destination = fichiers[-1]
        fichiers = fichiers[:-1]
    else :
        destination = '.'
        dic['--list-only'] = True
    
    for i in arguments :
        if '=' in i :
            j = i.split('=')
            dic[j[0]] = j[1]
        else :
            dic[i] = True

    return dic, fichiers, destination