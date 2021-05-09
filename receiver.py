import os, stat, time, filelist,message,generator,sys,signal

def creation_filelist_receiver(dirr,dic):
    '''creation de la liste de fichier destination

    utilisee dans la fonction principale receiver

    input : dirr = repertoire destination, chemin absolu (string)
            dic = dictionnaire des options (dictionnaire)
    output : file_listr = liste de fichier destination (liste de fichier)
            un fichier est représenté par un dictionnaire contenant des informations sur celui-ci
            {'name_loc':nom local,'name':nom absolu,'user':propriètaire,'groupe':groupe propriètaire,'mode':permissions,'size':taille,'modtime':date de derniere modification}
    '''
    if dirr[-1] != '/':
        dirr = dirr + '/'
    file_listr = filelist.filelist([dirr],dic,'receiver')
    return file_listr

def reception_filelist_sender(fd):
    '''receptionne la liste des fichiers source

    utilisee dans la fonction principale receiver

    input : fd = descripteur de fichier de l'endroit ou on receptionne les fichiers (descripteur de fichier, int)
    output : file_lists = liste des fichiers source (liste de fichiers)
    '''
    file_lists=[]
    tag = ['','l',(0,1)]
    while tag[2][0]<tag[2][1]:  #file_lists ne peut pas etre vide
        tag,data = message.recoit(fd)
        if tag[2][1]!= 0:
            file_lists.append(message.str_to_fic(data))
    return file_lists

def reception_fichiers(dirr,d,dic):
    '''receptionne les fichiers envoyés par sender et les crée dans le repertoire de destination

    utilisee dans la fonction principale receiver

    input : dirr = repertoire de destination, chemin absolu (string)
            d = descripteur de fichier de l'endroit ou on recoit les fichiers (descripteur de fichier, int)
                ou socket server si mode daemon pull (socket)
            dic = dictionnaire d'options
    output : rien
    '''
    if dic['-v'] > 0 :
        print('receiving files ...', end=' ' if dic['-v'] < 2 else '\n')
    if dic['daemon']:
        tag,data = message.recoit_socket(d)
    else :
        tag,data = message.recoit(d)
    nbr_file = tag[2][1]
    i = 1
    while i <= nbr_file:
        if dic['daemon']:
            tag,data = message.recoit_socket(d)
        else :
            tag,data = message.recoit(d)
        data = message.str_to_fic(data)
        #repertoire
        if tag[1]=='r':
            chemin = os.path.join(dirr,tag[0])
            os.mkdir(chemin,data['mode'])
        #lien symbolique
        elif tag[1]=='s':
            chemin=os.path.join(dirr,tag[0])
            fic = os.readlink(data['name'])
            os.symlink(fic,chemin)
        #fichier
        elif tag[1]=='f':
            chemin = os.path.join(dirr,tag[0])
            nbr_transmission = tag[2][1]
            try:
                os.unlink(chemin)
            except:
                pass
            fd = os.open(chemin,os.O_CREAT|os.O_WRONLY|os.O_APPEND)
            j = tag[2][0]+1
            while j <= nbr_transmission:
                if dic['daemon']:
                    tag,data = message.recoit_socket(d)
                else :
                    tag,data = message.recoit(d)
                j +=1
                data = data.encode('utf-8')
                os.write(fd,data)
            os.close(fd)
        if dic['-v'] > 1 :
            print('\'{}\' received'.format(tag[0]))
        i+=1

    if dic['-v']>0 :
        print('done', end='\n' if dic['-v'] < 2 else ' receiving files\n')

def supprimer(rep,dic):
    '''supprime un fichier ou un repertoire et
    tous les fichiers qui se trouvent dedans
    
    utilisée dans reception_delete
    
    input : rep = un nom de répertoire ou fichier absolu (string)
            dic = dictionnaire des options (dictionnaire)
    output : rien
    '''
    if os.path.isdir(rep): #si repertoire
        cur_dir=os.listdir(rep)
        for elt in cur_dir: #pour tout element dans dossier en cours de traitement
            elt = os.path.join(rep,elt) #On recupère l'adresse absolue de l'élément traité
            if os.path.isdir(elt): #Si elt traité = répertoire
                supprimer(elt,dic) #Suppression du repertoire
            else: #si autre que repertoire (fichier/lien symbolique)
                if dic['-v'] > 1 :
                    print('{} deleted'.format(elt[len(rep)+1:]))
                os.unlink(elt) #suppression du fichier
        os.rmdir(rep) #suppression du repertoire
        if dic['-v'] > 1 :
            print('{} deleted'.format(elt['name_loc']))
    else : #si fichier ou symlink ou hardlink
        try :
            os.unlink(rep)
            if dic['-v'] > 1 :
                print('{} deleted'.format(elt['name_loc']))
        except :
            pass

def reception_delete(soc,dic):
    '''recoit la delete liste depuis la socket soc et supprime les fichier
    de cette liste

    utilisee dans la fonction principale receive_daemon

    input : soc = socket cliente (socket)
            dic = dictionnaire des options (dictionnaire)
    output : rien
    '''
    tag,data = message.recoit_socket(soc)
    nbrFile = tag[2][1]
    if nbrFile != 0 :
        supprimer(data['name'])
    for i in range(1,nbrFile):
        tag,data = message.recoit_socket(soc)
        supprimer(data['name'])

def receive_local(dirr,dic,gs_g,sr_r):
    '''fonction principale du receiver en mode local

    utilisee par server.server_local, dans server.py

    input : dirr = repertoire destination, chemin absolu (string)
            dic = dictionnaire des options (dictionnaire)
            gs_g = descripteur de fichier du generateur, pipe generateur vers sender (descripteur de fichier, int)
            sr_r = descripteur de fichier du receiver, pipe sender vers receiver (descripteur de fichier, int)
    output : rien
    '''
    #creation de la liste de fichier du repertoire de destination
    file_listr = creation_filelist_receiver(dirr,dic)
    #reception de la liste de fichier du repertoire source
    file_lists = reception_filelist_sender(sr_r)
    if len(file_lists) == 0:
        try :
            os.wait()
        except :
            pass
        sys.exit(0)
    #creation du generateur
    pid=os.fork()
    if pid != 0: #père, générateur
        generator.generator_local(file_lists,file_listr,dic,gs_g)
    else: #fils, receiver, reception des fichiers
        reception_fichiers(dirr,sr_r,dic)
        #terminaison
        sys.exit(0)


def receive_daemon(dst,dic,soc):
    '''fonction principale du receiver en mode local

    input : dst: repertoire de destination (str)
            dic: dictionnaire des options (dic)
            soc: socket de communication du daemon (socket)

    output : rien
    '''
    if dic['--list-only'] and dic['pull']:
        #On récupère la liste de fichier et tout ses éléments descripteurs
        taille_tot = 0
        tag,data = message.recoit_socket(soc)
        nbr_file = tag[2][1]
        data = message.str_to_fic(data)
        taille_tot += data['size']
        if not dic['-q'] :
            print('{} {:>14} {} {}'.format(stat.filemode(data['mode']), data['size'], time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(float(data['modtime']))), data['name_loc']))    
        i = 1
        while i < nbr_file:
            tag,data = message.recoit_socket(soc)
            data = message.str_to_fic(data)
            taille_tot += data['size']
            if not dic['-q'] :
                print('{} {:>14} {} {}'.format(stat.filemode(data['mode']), data['size'], time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(float(data['modtime']))), data['name_loc']))
            i+=1
        if dic['-v']>0 and not dic['-q'] :
            print('\ntaille totale : {}'.format(taille_tot)) #nombres à changer, je ne sais pas ce à quoi ça correspond
    else :
        #calcul et envoit de filelistReceiver au demon
        if dic['pull']:
            filelistReceiver = creation_filelist_receiver(dst,dic)
            nbrFile = len(filelistReceiver)
            if nbrFile == 0:
                tag=['','l',(0,0)]
                message.envoit_socket(soc,tag)
            for i in range(nbrFile):
                tag = [filelistReceiver[i]['name_loc'],'l',(i+1,nbrFile)]
                message.envoit_socket(soc,tag,v=filelistReceiver[i])
        #reception delete liste + suppression fichiers a faire
        reception_delete(soc,dic)
        reception_fichiers(dst,soc,dic)
        if dic['push']:
            os.kill(os.getppid(),signal.SIGCHLD)
    sys.exit(0)
