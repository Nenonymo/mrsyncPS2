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
                

    return dic, norm_liste_dir(fichiers), destination

def norm_liste_dir(lis_dir) :
    #On créé la liste complète (sauf avec -r) de fichiers à traiter en faisant gaffe aux doublons
    if dic['-r'] :
        i = 0
        while i < len(lis_dir) :
            j = i + 1
            while j < len(lis_dir) :
                if lis_dir[i] == lis_dir[j][:len(lis_dir[i])] + '/' :
                    del lis_dir[j]
                elif lis_dir[i][:len(lis_dir[j])] + '/' == lis_dir[j] :
                    del lis_dir[i]
                j += 1
            i += 1
    else :
        i = 0
        while i < len(lis_dir) :
            if lis_dir[i] == '.' or lis_dir[i] == './' :
                lis_dir = lis_dir[:i + 1] + [elt for elt in os.listdir(lis_dir[i])] + lis_dir[i + 1:]
            elif lis_dir[i][-1] == '/' :
                lis_dir = lis_dir[:i + 1] + [os.path.join(lis_dir[i], elt) for elt in os.listdir(lis_dir[i])] + lis_dir[i + 1:]
            elif lis_dir[i].startswith('./') :
                lis_dir[i] = lis_dir[i][2:]
            i += 1
        i = 0
        while i < len(lis_dir) :
            j = i+1
            while j < len(lis_dir) :
                if lis_dir[i] == lis_dir[j] :
                    del lis_dir[j]
                j += 1
            i += 1