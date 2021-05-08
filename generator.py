import os, sys, message
    #(modification time and size differs dans la plupart des cas)
    #si --checksum, a file-level checksum will be cerated and compared
    #on crée les repertoires et on ne skip pas les repertoires, symlink et device nodes
    
    #si --whole-file on réenvoit le fichier entier(empty block checksum)
    #sinon on compare le fichier dans le rep de receiver et e fichier dans le rep de sender 
    #en local on fair avec whole-file par defaut

'''#tri avec repertoire a la fin
#actuellement sort_receiver ne sert a rien je le garde au cas ou mais si on l'utilise pas poubelle
def sort_receiver(dir):
    i=0
    while i < len(dir):
        if os.path.isdir(dir[i]['name']):
            j=i+1
            while os.path.isdir(dir[j]['name']) and j < len(dir):
                j=j+1
            if j == len(dir):
                i = j
            else:
                tmp = dir[i]
                dir[i]=dir[j]
                dir[j]=tmp'''


def supprimer(rep,verbose):
    '''supprime un repertoire et
    tous les fichiers qui se trouvent dedans
    
    utilisée dans delete_files lorsque l'option --delete est activée
    
    input : rep = un nom de répertoire absolu (string)
            verbose = niveau de verbose (int)
    output : rien
    '''
    cur_dir=os.listdir(rep)
    for elt in cur_dir: #pour tout element dans dossier en cours de traitement
        elt = os.path.join(rep,elt) #On recupère l'adresse absolue de l'élément traité
        if os.path.isdir(elt): #Si elt traité = répertoire
            supprimer(elt,verbose) #Suppression du repertoire
        else: #si autre que repertoire (fichier/lien symbolique)
            if verbose > 1 :
                print('{} deleted'.format(elt[len(rep)+1:]))
            os.unlink(elt) #suppression du fichier
    os.rmdir(rep) #suppression du repertoire


def delete_files(file_list_sender,file_list_receiver,verbose):
    '''supprime les fichiers et répertoires qui sont dans file_list_receiver et pas dans file_list_sender

    utilisée dans la fonction principale generator lorsque l'option --delete est activée

    input : file_list_sender = la liste des fichiers source (liste de fichiers)
            file_list_receiver = la liste des fichiers de destination (qui se trouvent dans le répertoire de destination) (liste de fichiers)
            un fichier est représenté par un dictionnaire contenant des informations sur celui-ci
            {'name_loc':nom local,'name':nom absolu,'user':propriètaire,'groupe':groupe propriètaire,'mode':permissions,'size':taille,'modtime':date de derniere modification}
            verbose = niveau de verbose (int)
    output : rien
    '''
    for elt in file_list_receiver: #tout les elt de filelistreceiver
        test = True
        for e in file_list_sender: #tout les elt de filelistsender
            if elt['name_loc'] == e['name_loc']: #si les deux elt sont les memes
                test = False
                break
        if test: #si l'élément doit etre supprimé
            if os.path.isdir(elt['name']): #si repertoire
                supprimer(elt['name'],verbose)
                if verbose > 1 :
                    print('{} deleted'.format(elt['name_loc']))
            else: #si fidhier
                try :
                    os.unlink(elt['name'])
                    if verbose > 1 :
                        print('{} deleted'.format(elt['name_loc']))
                except :
                    pass


def no_skip(fichier,file_list_receiver,dic):
    '''teste si le fichier 'fichier' doit ajoute a la send_list = liste des fichiers a envoyer au receiver

    utilisee dans la fonction creation_sendlist

    input : fichier = le fichier a tester (fichier)
            file_list_receiver = la liste des fichiers de destination (liste de fichiers)
            dic = dictionnaire des options (dictionnaire)
    output : Vrai si le fichier doit etre envoyé, Faux sinon (booleen)
    '''
    new_file = True
    for elt in file_list_receiver:
        if elt['name_loc'] == fichier['name_loc']:
            new_file = False
            if dic['--ignore-existing'] or os.path.isdir(elt['name']) or os.path.islink(elt['name']):
                return False
            elif os.path.isfile(elt['name']):
                if elt['size'] == fichier['size'] and elt['modtime'] == fichier['modtime']:
                    return dic['-I'] #-I est le contraire du mode normal, on envoie s'ils ont la même taille et le même modtime
                elif dic['-u'] and fichier['modtime'] <= elt['modtime'] :
                    return False
                elif dic['--size-only'] and elt['size'] == fichier['size'] :
                    return False
    if dic['--existing'] and new_file :
        return False

#gestion des fichiers spéciaux (device node) ?
    return True


def creation_deletelist(filelistSender,filelistReceiver):
    '''cree une liste de fichiers a supprimer pour le mode daemon 
    
    utilisee dans generator_daemon

    input : filelistSender = liste des fichiers source (liste de fichier)
            filelistReceiver = liste des fichiers destination (liste de fichier)
    output : deleteList = liste des fichier a supprimmer dans la destination (liste de fichier)
             len(deleteList) = taille de deleteList (int)
    '''
    deleteList=[]
    for elt in filelistReceiver:
        test = True
        for e in filelistSender:
            if elt['name_loc'] == e['name_loc']:
                test = False
                break
        if test:
                deleteList.append(elt)
    return deleteList,len(deleteList)


def creation_sendlist(file_list_sender,file_list_receiver,dic):
    '''cree la liste de fichiers a envoyer au receiver

    utilisee dans la fonction principale generator

    input : file_list_sender = liste de fichiers sources (liste de fichiers)
            file_list_receiver = liste de fichiers destination (liste de fichiers)
            dic = dictionnaire des options (dictionnaire)
    output : send_list = liste de fichiers à envoyer (liste de fichier)
            len(send_list) = taille de send_list (int)
    '''
    send_list=[]
    for elt in file_list_sender:
        if no_skip(elt,file_list_receiver,dic):
            send_list.append(elt)
        elif dic['-v'] > 1:
            print('{} skipped'.format(elt['name_loc']))
    return send_list,len(send_list)


def envoyer_liste(liste,nbr_file,fd,dic):
    '''envoit fichier par fichier la liste de fichiers liste au sender

    utilisee dans la fonction principale generator

    input : liste = la liste des fichiers à envoyer (liste de fichiers)
            nbr_file = le nombre de fichiers à envoyer = taille de liste (int)
            fd = si local ou daemon pull : le descripteur de fichier de l'endroit ou on envoit les fichiers (descripteur de fichier, int)
                 si daemon push : la socket cliente (socket)
            dic = dictionnaire des options (dictionnaire)
    output : rien
    '''
    if nbr_file == 0:   #si liste est vide
        tag = ['','l',(0,0)]
        if dic['--daemon'] and dic['push']: #daemon push
            message.envoit_socket(fd,tag)
        else : #local and daemon pull
            message.envoit(fd,tag)
    for i in range(nbr_file):
        tag = [liste[i]["name_loc"],"l",(i+1,nbr_file)]
        if dic['--daemon'] and dic['push']: #daemon push
            message.envoit_socket(fd,tag,v=liste[i])
        else : #local and daemon pull
            message.envoit(fd,tag,v=liste[i])


def generator_local(file_list_sender,file_list_receiver,dic,gs_g):
    '''fonction principale du generateur pour le mode local

    utilisee par le receiver dans receive_local dans receiver.py

    input : file_list_sender = liste de fichiers source (liste de fichiers)
            file_list_receiver = liste de fichiers destination (liste de fichiers)
            dic = dictionnaire des options (dictionnaire)
            gs_g = descripteur de fichier du pipe generateur vers sender (descripteur de fichier, int)
    output : rien
    '''
    if dic["--delete"]:
        if dic['-v'] :
            print('deleting files ...',end=' ' if dic['-v'] < 2 else '\n')
        delete_files(file_list_sender,file_list_receiver,dic['-v'])
        if dic['-v'] :
            print('done',end='\n' if dic['-v'] < 2 else ' deleting files\n')
    if dic['-v'] :
        print('creation sendlist ...',end=' ' if dic['-v'] < 2 else '\n')
    send_list,nbr_file = creation_sendlist(file_list_sender,file_list_receiver,dic)
    if dic['-v'] :
        print('done' if dic['-v'] < 2 else 'sendlist created')
    #envoit de la liste des fichiers au sender
    envoyer_liste(send_list,nbr_file,gs_g,dic)
    #attente de la fin des fils et terminaison
    os.wait()
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
    if dic["--delete"]:
        deleteList,nbrDelete = creation_deletelist(filelistSender,filelistReceiver)
    sendList,nbrFile = creation_sendlist(filelistSender,filelistReceiver,dic)
    #envoit de la liste de fichier au sender
    envoyer_liste(deleteList,nbrDelete,gs_g,dic)
    envoyer_liste(sendList,nbrFile,gs_g,dic)

#A faire : gérer les options perm et time
'''à ajouter :
-d : transfer directories without recursing
-H : preserve hard links
-p : preserve permissions
-t : preserve times
--force : force deletion of dirs even if not empty

(ceux-là, j'avoue ne pas les comprendre)
--timeout=TIME : set I/O timeout in seconds
--blocking-io : use blocking I/O for the remote shell
-a : archive mode; same as -rpt (no -H)
'''