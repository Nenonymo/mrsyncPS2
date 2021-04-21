import os, sys

def parser(args) :
    args = args[1:]
    fichiers = []
    arguments = []
    dic = {'-v':False, '-q':False, '-a':False, '-r':False, '-u':False, '-d':False, '-H':False, '-p':False, '-t':False, '--times':False, '--existing':False, '--ignore-existing':False, '--delete':False, '--force':False, '--timeout':0, '--blocking-io':False, '-I':False, '--ignore-times':False, '--size-only':False, '--adress':'', '--port':'', '--list-only':False, '-h':False, 'ssh':False, '--daemon':False, '--no-detach':False}
    for i in args :
        if i[0] == '-' :
            arguments += [i]
        else :
            if '::' in i :
                dic['--daemon'] = True
            elif ':' in i :
                dic['ssh'] = True
            fichiers += [i]
    if len(fichiers) == 0 :
        raise Exception('Pas de fichier')
    elif len(fichiers) == 1 :
        destination = '.'
        dic['--list-only'] = True
    else :
        destination = fichiers[-1]
        fichiers = fichiers[:-1]
    
    for i in arguments :
        if '=' in i :
            j = i.split('=')
            dic[j[0]] = j[1]
        else :
            dic[i] = True
    
    if dic['--daemon'] :
        listDaemonArgs = ['--daemon', '--address', '--no-detach', '--port', '-h']
        for i in arguments :
            if i.split('=')[0] not in listDaemonArgs :
                raise Exception('Arguments invalide')
                

    return dic, fichiers, destination
