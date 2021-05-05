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

'''supprime un repertoire et
 tous les fichiers qui se trouvent dedans
 
 utilisée dans delete_files lorsque l'option --delete est activée
 
 input : rep = un nom de répertoire absolu (string)
 ouput : rien
'''
def supprimer(rep):
    cur_dir=os.listdir(rep)
    for elt in cur_dir:
        elt = os.path.join(rep,elt)
        if os.path.isdir(elt):
            supprimer(elt)
        else:
            os.unlink(elt)
    os.rmdir(rep)

'''supprime les fichiers et répertoires qui sont dans file_list_receiver et pas dans file_list_sender

utilisée dans la fonction princiaple generator lorsque l'option --delete est activée

input : file_list_sender = la liste des fichiers source (liste de fichiers)
        file_list_receiver = la liste des fichiers de destination (qui se trouvent dans le répertoire de destination) (liste de fichiers)
        un fichier est représenté par un dictionnaire contenant des informations sur celui-ci
        {'name_loc':nom local,'name':nom absolu,'user':propriètaire,'groupe':groupe propriètaire,'mode':permissions,'size':taille,'modtime':date de derniere modification}
ouput : rien
'''
def delete_files(file_list_sender,file_list_receiver):
    for elt in file_list_receiver:
        test = True
        for e in file_list_sender:
            if elt['name_loc'] == e['name_loc']:
                test = False
                break
        if test:
            if os.path.isdir(elt['name']):
                supprimer(elt['name'])
            else:
                try :
                    os.unlink(elt['name'])
                except :
                    pass

'''teste si le fichier 'fichier' doit ajoute a la send_list = liste des fichiers a envoyer au receiver

utilisee dans la fonction creation_sendlist

input : fichier = le fichier a tester (fichier)
        file_list_receiver = la liste des fichiers de destination (liste de fichiers)
ouput : Vrai si le fichier doit etre envoyé, Faux sinon (booleen)
'''
def no_skip(fichier,file_list_receiver):
    for elt in file_list_receiver:
        if elt['name_loc'] == fichier['name_loc'] :
            if os.path.isdir(elt['name']) or os.path.islink(elt['name']):
                return False
            elif os.path.isfile(elt['name']):
                if elt['size'] == fichier['size'] and elt['modtime'] == fichier['modtime']: #modtime ??
                    return False
#gestion des fichiers spéciaux (device node) ?
    return True

'''cree une liste de fichiers a supprimer pour le mode daemon, pas utilise pour le moment 
'''
def creation_deletelist(file_list_sender,file_list_receiver):
    delete_list=[]
    for elt in file_list_receiver:
        test = True
        for e in file_list_sender:
            if elt['name_loc'] == e['name_loc']:
                test = False
                break
        if test:
                delete_list.append(elt)
    return delete_list,len(delete_list)

'''cree la liste de fichiers a envoyer au receiver

utilisee dans la fonction principale generator

input : file_list_sender = liste de fichiers sources (liste de fichiers)
        file_list_receiver = liste de fichiers destination (liste de fichiers)
ouput : send_list = liste de fichiers à envoyer (liste de fichier)
        len(send_list) = taille de send_list (int)
'''
def creation_sendlist(file_list_sender,file_list_receiver):
    send_list=[]
    for elt in file_list_sender:
        if no_skip(elt,file_list_receiver):
            send_list.append(elt)
    print(send_list)
    return send_list,len(send_list)

'''envoit fichier par fichier la liste de fichiers liste au sender

utilisee dans la fonction principale generator

input : liste = la liste des fichiers à envoyer (liste de fichiers)
        nbr_file = le nombre de fichiers à envoyer = taille de liste (int)
        fd = le descripteur de fichier de l'endroit ou on envoit les fichiers (descripteur de fichier, int)
ouput : rien
'''
def envoyer_liste(liste,nbr_file,fd):
    if nbr_file == 0:   #si liste est vide
        tag = ['','l',(0,0)]
        message.envoit(fd,tag,lineFile='comSize1')
    for i in range(nbr_file):
        tag = [liste[i]["name_loc"],"l",(i+1,nbr_file)]
        message.envoit(fd,tag,v=liste[i],lineFile='comSize1')

'''fonction principale du generateur pour le mode local

utilisee par le receiver dans receive_local dans receiver.py

input : dirs = repertoires source (liste de string)
        dirr = repertoire destination (string)
        file_list_sender = liste de fichiers source (liste de fichiers)
        file_list_receiver = liste de fichiers destination (liste de fichiers)
        dic = dictionnaire des options (dictionnaire)
        gs_g = descripteur de fichier du pipe generateur vers sender (descripteur de fichier, int)
ouput : rien
'''
def generator_local(dirs,dirr,file_list_sender,file_list_receiver,dic,gs_g):
    if dic["--delete"]:
        delete_files(file_list_sender,file_list_receiver)
    send_list,nbr_file = creation_sendlist(file_list_sender,file_list_receiver)
    #envoit de la liste des fichiers au sender
    envoyer_liste(send_list,nbr_file,gs_g)
    #attente de la fin des fils et terminaison
    os.wait()
    os.wait()
    sys.exit(0)

'''fonction principale du generateur pour le mode daemon
'''
def generator_daemon(dirs,dirr,file_list_sender,file_list_receiver,dic,gs_g):
    delete_list =[]
    nbr_delete=0
    #if dic["--delete"]:   pas de delete dans le mode deamon
    #    delete_list,nbr_delete=creation_deletelist(file_list_sender,file_list_receiver)
    send_list,nbr_file = creation_sendlist(file_list_sender,file_list_receiver)
    #envoit de la liste de fichier au sender
    #envoyer_liste(delete_list,nbr_delete,gs_g)
    envoyer_liste(send_list,nbr_file,gs_g)

#A faire : gérer les options perm et time