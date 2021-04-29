import os, sys

def parser(args) :
    args = args[1:]
    fichiers = []
    arguments = []
    dic = {'-v':0, '-q':False, '-a':False, '-r':False, '-u':False, '-d':False, '-H':False, '-p':False, '-t':False, '--existing':False, '--ignore-existing':False, '--delete':False, '--force':False, '--timeout':0, '--blocking-io':False, '-I':False, '--size-only':False, '--adress':'', '--port':'', '--list-only':False, '-h':False, 'ssh':False, '--daemon':False, '--no-detach':False}
    
    if len(args) == 0 or (len(args) == 1 and args[0] == '-h') :
        show_help('mrsync.txt')
        sys.exit()
    elif '--daemon' in args and '-h' in args :
        show_help('mrsync_daemon.txt')
    
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
        show_help('mrsync.txt')
        raise Exception('Pas de fichier')
    elif len(fichiers) == 1 :
        destination = '.'
        dic['--list-only'] = True
    else :
        destination = fichiers[-1]
        fichiers = fichiers[:-1]

    for i in arguments :
        convert = {'--verbose':'-v','--quiet':'-q','--archive':'-a','--recursive':'-r','--update':'-u','--dirs':'-d','--hard-links':'-H','--perms':'-p','--times':'-t','--ignore-times':'-I','--help':'-h'}
        try :
            i = convert[i]
        except :
            None
        if '=' in i :
            j = i.split('=')
            dic[j[0]] = j[1]
        elif i == '-v' :
            if dic['-v'] >= 5 :
                dic['-v'] = 5
            else :
                dic['-v'] += 1
        else :
            dic[i] = True
    
    if dic['--daemon'] :
        listDaemonArgs = ['--daemon', '--address', '--no-detach', '--port', '-h']
        for i in arguments :
            if i.split('=')[0] not in listDaemonArgs :
                raise Exception('Arguments invalide')

    return dic, fichiers, destination

def show_help(fileName) :
    file = open(fileName, 'r')
    for i in file :
        print(i, end='')
    print()