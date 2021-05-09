import os, sys

def parser(args) :
    ''' parser
    input : args = liste des arguments entrés brut (string list)
    output : dic = dictionnaire des options (dictionnaire)
             fichiers = liste des fichiers sources (string list)
             destination = dossier de destination (string)
    '''
    args = args[1:]
    fichiers = []
    destination = ''
    dic = {'-v':0, '--timeout':0,'-q':False, '-a':False, '-r':False, '-u':False, '-d':False,
        '-H':False, '-p':False, '-t':False, '--existing':False, '--ignore-existing':False,
        '--delete':False, '--force':False, '--blocking-io':False, '-I':False, '--size-only':False, 
        '--list-only':False, '-h':False, 'ssh':False, 'daemon':False, '--no-detach':False,
        '--daemon':False, '--server':False,'push':False,'pull':False,'--address':'', '--port':''}
    if len(args) == 0 :
        show_help()
        sys.exit(0)
    pas = False
    for i in range(len(args)) :
        if pas:
            pas=False
            pass
        if args[i][0] == '-' :
            try : dic,pas = argument_management(dic,args[i],args[i+1])
            except : dic,pas = argument_management(dic,args[i],args[i])
        else :
            if '::' in args[i] :
                dic['daemon'] = True
            elif ':' in args[i] :
                dic['ssh'] = True
            fichiers += [args[i]]
    
    if not(dic['--daemon']) and not(dic['--server']) and len(fichiers) == 0 : #exception si pas de fichier et pas un serveur
        show_help()
        raise Exception('Pas de fichier')
    elif len(fichiers) == 1 :
        destination = '.'
        dic['--list-only'] = True
    elif dic['--daemon'] or dic['--server']:
        destination = ''
        fichiers = []
    else:
        destination = fichiers[-1]
        fichiers = fichiers[:-1]
    

    if dic['--daemon'] :  #daemon (serveur), le client du daemon peut avoir toutes les options qu'il veut
        for key,elt in dic.items() :
            if elt and key not in ['-v','-vv','-vvv','--daemon', '--address', '--no-detach', '--port', '-h'] :
                raise Exception('Arguments invalide (daemon mode)')


    return dic, fichiers, destination

def show_help() :
    '''Affiche l'aide depuis 'mrsync.txt' '''
    file = open('mrsync.txt', 'r')
    for i in file :
        print(i, end='')
    print()
    file.close()

def argument_management(dic, elt, elt_next) :
    '''actualise dic et fait les changements relatifs aux arguments
    input : dic = dictionnaire des options (dictionnaire)
            elt = ième élément de argv (string)
            elt_next = (i+1)ème élément de argv (string)
    output : dic = dictionnaire des options (dictionnaire)
             pas = dis si on passe l'argument suivant ou non (booleen)
    '''
    pas = False
    convert = {'--verbose':'-v','--quiet':'-q','--archive':'-a','--recursive':'-r','--update':'-u','--dirs':'-d',
                '--hard-links':'-H','--perms':'-p','--times':'-t','--ignore-times':'-I','--help':'-h'}
    try : elt = convert[elt]
    except : None
    
    if elt == '-h' :
        show_help()
        sys.exit(0)
    elif elt == '--force':
        dic['--delete']=True
        dic['--force']=True
    elif elt == '-a': #same as rpt
        dic['-r'] = True
        dic['-p'] = True
        dic['-t'] = True
    elif elt == '-d':
        dic['-d']=True
        dic['-r']=False
    elif elt == '-r':
        if not dic['-d']:
            dic['-r']=True
    elif '=' in elt :   #s'il y a '=' on fait l'affectation
        j = elt.split('=')
        if j[0] == '--timeout' or j[0] == '--port':
            dic[j[0]] = int(j[1])
    elif elt in ['--port','--timeout','--address'] : #on prends en compte si le séparateur n'est pas '=' mais ' '
        if elt == '--timeout' or let == '--port':
            dic[elt] = int(elt_next)
        else :
            dic[elt] = elt_next
        pas = True
    elif elt == '-q' :      #mode quiet, on enlève la verbose
        dic['-q'] = True
        dic['-v'] = 0
    elif '-v' in elt : #si on veut ajouter de la verbose et qu'on n'est pas en mode -quiet(il est prioritaire) et on limite la verbose à 3
            if not dic['-q'] : 
                dic['-v'] = min(dic['-v'] + elt.count('v'),3)
    else :                   #cas par défaut on set l'argument à True
        dic[elt] = True
    
    return dic,pas
