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

    for i in range(len(args)) :
        if args[i][0] == '-' :
            try : dic = argument_management(args[i],args[i+1])
            except : dic = argument_management(args[i],args[i])
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
    else :
        destination = fichiers[-1]
        fichiers = fichiers[:-1]
    

    if dic['--daemon'] :  #daemon (serveur), le client du daemon peut avoir toutes les options qu'il veut
        for key,elt in dic.items() :
            if elt and key not in ['--daemon', '--address', '--no-detach', '--port', '-h'] :
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
    '''
    convert = {'--verbose':'-v','--quiet':'-q','--archive':'-a','--recursive':'-r','--update':'-u','--dirs':'-d','--hard-links':'-H','--perms':'-p','--times':'-t','--ignore-times':'-I','--help':'-h'}
    try : elt = convert[elt]
    except : None
    
    if elt == '-h' :
        show_help()
        sys.exit(0)
    elif '=' in elt :   #s'il y a '=' on fait l'affectation
        j = elt.split('=')
        dic[j[0]] = j[1]
    elif elt in ['--port','--timeout','--address'] : #on prends en compte si le séparateur n'est pas '=' mais ' '
        dic[elt] = elt_next
    elif elt == '-q' :      #mode quiet, on enlève la verbose
        dic['-q'] = True
        dic['-v'] = 0
    elif elt == '-v' and not dic['-q'] and dic['-v'] != 3 : #si on veut ajouter de la verbose et qu'on n'est pas en mode -quiet(il est prioritaire) et on limite la verbose à 3
        dic['-v'] += 1
    else :                   #cas par défaut on set l'argument à True
        dic[elt] = True
    
    return dic
