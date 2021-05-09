import os, sys, message

def supprimer(rep,repabs,dic):
    '''supprime un repertoire et tous les fichiers qui se trouvent dedans
    
    utilisée dans delete_files lorsque les options --delete ou --force sont activées
    
    input : rep = nom local du repertoire (string)
            repabs = un nom de répertoire absolu (string)
            dic = dictionnaire des options (dictionnaire)
    output : rien
    '''
    cur_dir=os.listdir(repabs) #obtient tous les fichiers du répertoire
    if len(cur_dir) == 0 or dic['--force']:
        for elt in cur_dir:
            eltabs = os.path.join(repabs,elt) #On recupère l'adresse absolue de l'élément traité
            elt = os.path.join(rep,elt)
            if os.path.isdir(eltabs): #Si elt traité = répertoire
                supprimer(elt,eltabs,dic)
            else: #si autre que repertoire 
                try : #suppression du fichier
                    os.unlink(eltabs)
                    if dic['-v'] > 1 :
                        print('{} deleted'.format(elt))
                except:
                    if dic['-v'] > 1 :
                        print('{} permission not granted'.format(elt))
        try :  #suppression du repertoire
            os.rmdir(repabs) 
            if dic['-v'] > 1 :
                print('{} deleted'.format(rep))
        except:
            if dic['-v'] > 1 :
                print('{} permission not granted or dicrectory not empty'.format(rep))
        

def delete_files(filelistSender,filelistReceiver,dic):
    '''supprime les fichiers et répertoires qui sont dans file_list_receiver et pas dans file_list_sender

    utilisée dans la fonction principale generator lorsque les options --delete ou --force sont activées

    input : filelistSender = la liste des fichiers source (liste de fichiers)
            filelistReceiver = la liste des fichiers de destination (qui se trouvent dans le répertoire de destination) (liste de fichiers)
            un fichier est représenté par un dictionnaire contenant des informations sur celui-ci
            {'name_loc':nom local,'name':nom absolu,'user':propriètaire,'groupe':groupe propriètaire,'mode':permissions,'size':taille,'modtime':date de derniere modification}
            dic = dictionnaire des options (dictionnaire)
    output : rien
    '''
    for elt in filelistReceiver: #tout les elt de filelistreceiver
        test = True
        for e in filelistSender: #tout les elt de filelistsender
            if elt['name_loc'] == e['name_loc']: #si les deux elt sont les memes alors on ne le supprime pas
                test = False
                break
        if test: #true si l'élément doit etre supprimé
            if os.path.isdir(elt['name']): #si repertoire
                supprimer(elt['name_loc'],elt['name'],dic)
            else: #si fichier
                try :
                    os.unlink(elt['name'])
                    if dic['-v'] > 1 :
                        print('{} deleted'.format(elt['name_loc']))
                except :
                    if dic['-v'] > 1 :
                        print('{} permission not granted'.format(elt['name_loc']))


def creation_deletelist(filelistSender,filelistReceiver):
    '''cree une liste de fichiers a supprimer pour le mode daemon 
    
    utilisee dans generator_daemon si les options --delete ou --force sont activées

    input : filelistSender = liste des fichiers source (liste de fichier)
            filelistReceiver = liste des fichiers destination (liste de fichier)
    output : deleteList = liste des fichier a supprimmer dans la destination (liste de fichier)
             len(deleteList) = taille de deleteList (int)
    '''
    deleteList=[]
    for elt in filelistReceiver:
        test = True
        for e in filelistSender:
            if elt['name_loc'] == e['name_loc']: #si les deux elt sont les memes alors on ne l'ajoute pas à la deleteList
                test = False
                break
        if test:
                deleteList.append(elt)
    return deleteList,len(deleteList)


def no_skip(fichier,filelistReceiver,dic):
    '''teste si le fichier 'fichier' doit etre ajoute a la sendlist = liste des fichiers a envoyer au receiver

    utilisee dans la fonction creation_sendlist

    input : fichier = le fichier a tester (fichier)
            filelistReceiver = la liste des fichiers de destination (liste de fichiers)
            dic = dictionnaire des options (dictionnaire)
    output : Vrai si le fichier doit etre envoyé, Faux sinon (booleen)
    '''
    new_file = True #true si nouveau fichier
    for elt in filelistReceiver:
        if elt['name_loc'] == fichier['name_loc']: #si fichier existe dans le repertoire destination 
            new_file = False #ce n'est pas un nouveau fichier
            if dic['--ignore-existing'] or os.path.isdir(elt['name']) or os.path.islink(elt['name']): #si --ignore-existing alors on envoit pas si le fichier existe deja dans la destination, pareil si le repertoire ou le lien symbolique existe deja
                return False
            elif os.path.isfile(elt['name']): #si c'est un fichier
                if elt['size'] == fichier['size'] and elt['modtime'] == fichier['modtime']: #si -I ont envoit s'ils ont la même taille et la même date de derniere modification sinon on envoit pas
                    return dic['-I']
                elif dic['-u'] and fichier['modtime'] <= elt['modtime'] :#si -u alors on envoit pas si la date de derniere modification du fichier dans la destination est inferieur a celle du fichier dans la source
                    return False
                elif dic['--size-only'] and elt['size'] == fichier['size'] : #si --size-only on envoit pas si esa tailles des deux fichier sont egales
                    return False
    if dic['--existing'] and new_file : #si --existing on ne crée pas de nouveaux fichiers
        return False
    return True


def creation_sendlist(filelistSender,filelistReceiver,dic):
    '''cree la liste de fichiers a envoyer au receiver

    utilisee dans les fonctions principales generator_local et generator_daemon

    input : filelistSender = liste de fichiers sources (liste de fichiers)
            filelistReceiver = liste de fichiers destination (liste de fichiers)
            dic = dictionnaire des options (dictionnaire)
    output : sendList = liste de fichiers à envoyer (liste de fichier)
            len(sendList) = taille de sendList (int)
    '''
    sendList=[]
    for elt in filelistSender:
        if no_skip(elt,filelistReceiver,dic): #si no_skip renvoit True, on ajoute le fichier à la sendList
            sendList.append(elt)
        elif dic['-v'] > 1:
            print('{} skipped'.format(elt['name_loc']))
    return sendList,len(sendList)


def envoyer_liste(liste,nbrFile,fd,dic):
    '''envoit fichier par fichier la liste de fichiers liste au sender

    utilisee dans les fonctions principales generator_local et generator_daemon

    input : liste = la liste des fichiers à envoyer (liste de fichiers)
            nbrFile = le nombre de fichiers à envoyer = taille de liste (int)
            fd = si local ou daemon pull : le descripteur de fichier de l'endroit ou on envoit les fichiers (descripteur de fichier, int)
                 si daemon push : la socket cliente (socket)
            dic = dictionnaire des options (dictionnaire)
    output : rien
    '''
    if nbrFile == 0:   #si liste est vide, on envoit l'information qu'elle est vide
        tag = ['','l',(0,0)]
        if dic['--daemon'] and dic['push']: #daemon push
            message.envoit_socket(fd,tag)
        else : #local and daemon pull
            message.envoit(fd,tag)
    for i in range(nbrFile): #si non vide, on envoit chaque fichier de la liste
        tag = [liste[i]["name_loc"],"l",(i+1,nbrFile)] #nom local du fichier, mode liste, numero de communication, nombre de communications
        if dic['--daemon'] and dic['push']: #daemon push
            message.envoit_socket(fd,tag,v=liste[i]) # v=fichier
        else : #local and daemon pull
            message.envoit(fd,tag,v=liste[i])


def generator_local(filelistSender,filelistReceiver,dic,gs_g):
    '''fonction principale du generateur pour le mode local

    utilisee par le receiver dans receive_local dans receiver.py

    input : filelistSender = liste de fichiers source (liste de fichiers)
            filelistReceiver = liste de fichiers destination (liste de fichiers)
            dic = dictionnaire des options (dictionnaire)
            gs_g = descripteur de fichier du pipe generateur vers sender (descripteur de fichier, int)
    output : rien
    '''
    if dic["--delete"]: #si option --delete (ou --force, --delete toujours à True quand --force) on supprime les fichers dans la destination qui ne sont pas dans la source
        if dic['-v'] > 0:
            print('deleting files ...',end=' ' if dic['-v'] < 2 else '\n')
        delete_files(filelistSender,filelistReceiver,dic)
        if dic['-v'] > 0:
            print('done',end='\n' if dic['-v'] < 2 else ' deleting files\n')
    if dic['-v'] > 0:
        print('creation sendlist ...',end=' ' if dic['-v'] < 2 else '\n')
    sendList,nbrFile = creation_sendlist(filelistSender,filelistReceiver,dic) #creation de la liste de fichiers a envoyer
    if dic['-v'] > 0:
        print('done' if dic['-v'] < 2 else 'sendlist created')
    envoyer_liste(sendList,nbrFile,gs_g,dic) #envoit de la liste des fichiers au sender
    os.wait()     #attente de la fin des fils et terminaison
    os.wait()
    sys.exit(0)


def generator_daemon(filelistSender,filelistReceiver,dic,gs_g):
    '''fonction principale du generateur en mode daemon 

    utilisee dans server_daemon dans server.py

    input : filelistSender = liste de fichiers source (liste de fichiers)
            filelistReceiver = liste de fichiers destination (liste de fichiers)
            dic = dictionnaire des options (dictionnaire)
            gs_g = si pull : descripteur de fichier du pipe generateur vers sender (descripteur de fichier, int)
                   si push : socket cliente (socket)
    output : rien
    '''
    deleteList =[]
    nbrDelete=0
    if dic["--delete"]: #creation de l liste des fichiers a supprimer dans la destination si --delete (ou --force car --delete activee quand --force activee)
        if dic['-v'] > 0:
            print('creation deletelist ...',end=' ' if dic['-v'] < 2 else '\n')
        deleteList,nbrDelete = creation_deletelist(filelistSender,filelistReceiver)
        if dic['-v'] > 0:
            print('done',end='\n' if dic['-v'] < 2 else ' deletelist created\n')
    if dic['-v'] > 0:
        print('creation sendlist ...',end=' ' if dic['-v'] < 2 else '\n')
    sendList,nbrFile = creation_sendlist(filelistSender,filelistReceiver,dic) #creation de la liste des fichiers a envoyer
    if dic['-v'] > 0:
        print('done' if dic['-v'] < 2 else 'sendlist created')

    envoyer_liste(deleteList,nbrDelete,gs_g,dic) #envoit de la deleteList
    envoyer_liste(sendList,nbrFile,gs_g,dic) #envoit de la sendListe