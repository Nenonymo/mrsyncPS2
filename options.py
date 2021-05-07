import os, sys

def parser(args) :
    args = args[1:]
    fichiers = []
    destination = ''
    #le dictionnaire de tous les arguments possibles
    dic = {'-v':0, '-q':False, '-a':False, '-r':False, '-u':False, '-d':False, '-H':False, '-p':False, '-t':False, '--existing':False, '--ignore-existing':False, '--delete':False, '--force':False, '--timeout':0, '--blocking-io':False, '-I':False, '--size-only':False, '--address':'', '--port':'', '--list-only':False, '-h':False, 'ssh':False, 'daemon':False, '--no-detach':False, '--daemon':False, '--server':False}
    if len(args) == 0 : #si on entre aucun argument, on montre l'aide et arrête le programme
        show_help()
        sys.exit(0)
    for i in range(len(args)) :
        if args[i][0] == '-' :        #si c'est un argument
            try : dic = argument_management(args[i],args[i+1])
            except : dic = argument_management(args[i],args[i])
        else :                        #si c'est un fichier
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
    else :                           #le dernier fichier entré est la destination
        destination = fichiers[-1]
        fichiers = fichiers[:-1]
    
    if dic['--daemon'] :  #daemon (serveur), le client du daemon peut avoir toutes les options qu'il veut
        for key,elt in dic.items() :
            if elt and key not in ['--daemon', '--address', '--no-detach', '--port', '-h'] :
                raise Exception('Arguments invalide (daemon mode)')

    return dic, fichiers, destination

def show_help() :
    file = open('mrsync.txt', 'r')
    for i in file :
        print(i, end='')
    print()
    file.close()

def argument_management(dic, elt, elt_next) :  #on actualise dic et fait les changements relatifs aux arguments
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
