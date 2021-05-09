import os, sys, signal, filelist, time, stat, message


def send_listonly(lis_dir,dic):
    '''recupere la liste de fichier file_list en utilisant filelist.py et affiche tous les fichiers de cette liste

    utilisee dans mrsync.py

    input : lis_dir = liste des noms de fichiers a traiter (liste de string)
            dic = dictionnaire des options (dictionnaire)
    output : rien
    ''' 
    #On récupère la liste de fichier et tout ses éléments descripteurs
    file_list = filelist.filelist(lis_dir,dic,'list-only')
    #L'affichage
    if not dic['-q'] :
        taille_tot = 0
        for elt in file_list:
            taille_tot += elt['size']
            print('{} {:>14} {} {}'.format(stat.filemode(elt['mode']), elt['size'], time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(elt['modtime'])), elt['name_loc']))
    if dic['-v'] :
        print('\ntaille totale : {}'.format(taille_tot))


def envoit_list_sender(dir,dic,w):
    '''cree la liste de fichiers et l'envoit sur le descripteur w fichier par fichier

    utilisee dans la fonction principale send_local et la fonction principale send_daemon

    input : dir = liste des noms de fichiers/repertoires a traiter (liste de string)
            dic = dictionnaire des options (dictionnaire)
            w = descripteur de fichier de l'endroit ou on envoit la liste (descripteur de fichier,int)
    output : rien
    '''
    file_list = filelist.filelist(dir,dic,'sender')
    nbr_file = len(file_list)
    if nbr_file == 0:
        tag=['','l',(0,0)]
        message.envoit(w,tag)
        sys.exit(0)
    for i in range(nbr_file):
        tag = [file_list[i]['name_loc'],'l',(i+1,nbr_file)]
        message.envoit(w,tag,v=file_list[i])
    

def envoit_fichier(gs_s,sr_s,dic):
    '''recoit la liste de fichiers du generateur et envoit les fichiers et leur contenu au receiver

    utilisee dans la fonction principale send_local

    input : gs_s = descripteur de fichier cote sender, generateur vers sender (descripteur de fichier, int)
            sr_s = descripteur de fichier cote sender, sender vers receiver (descripteur de fichier, int)
                   socket cliente si mode server daemon(socket)
            dic = dictionnaire des options (dictionnaire)
    output : rien
    '''
    if dic['-v'] :
        print('sending files ...', end=' ' if dic['-v'] < 2 else '\n')
    #reception de la liste de fichier du generateur + envoit des fichiers au receiver
    if dic['daemon'] and dic['push']: #daemon push
        tag,data = message.recoit_socket(gs_s)
    else :                   #local and daemon pull
        tag,data = message.recoit(gs_s) 
    nbr_file = tag[2][1]
    if nbr_file != 0:
        data = message.str_to_fic(data)
        #on envoit le nbr de fichiers a traiter
    if dic['--daemon'] or dic['daemon']: #daemon push and pull
        message.envoit_socket(sr_s,tag)
    else : #local
        message.envoit(sr_s,tag)
    i=1

    while i <= nbr_file : #si send_list est vide, on rentre pas dans la boucle
        if dic['-v'] > 1 :
            print('sending file \'{}\' ... '.format(data['name_loc']), end='')
        if os.path.isdir(data['name']):  #repertoire
            tag_e = [tag[0],'r',(1,1)]
            if dic["--daemon"] or dic['daemon']:
                message.envoit_socket(sr_s,tag_e,v=data)
            else :
                message.envoit(sr_s,tag_e,v=data)
        elif os.path.islink(data['name']): #lien symbolique
            tag_e = [tag[0],'s',(1,1)]
            if dic["--daemon"] or dic['daemon']:
                message.envoit_socket(sr_s,tag_e,v=data)
            else :
                message.envoit(sr_s,tag_e,v=data)
        elif os.path.isfile(data['name']): #fichier
            fd = os.open(data['name'],os.O_RDONLY)
            size_file = data['size']
            taille_msg = 5000
            nbr_transmission = size_file//taille_msg +1
            if size_file%taille_msg != 0:
                nbr_transmission += 1
            tag_e = [tag[0],'f',(1,nbr_transmission)]
            if dic["--daemon"] or dic['daemon']:
                message.envoit_socket(sr_s,tag_e,v=data)
            else :
                message.envoit(sr_s,tag_e,v=data)
            j = 2
            #envoyer le contenu du fichier
            while j <= nbr_transmission :
                msg = os.read(fd,taille_msg).decode('utf-8')
                tag_e = [tag[0],'f',(j,nbr_transmission)]
                if dic["--daemon"] or dic['daemon']:
                    message.envoit_socket(sr_s,tag_e,v=msg)
                else :
                    message.envoit(sr_s,tag_e,v=msg)
                j+=1
            os.close(fd)
        if dic['-v'] > 1 :
            print('done')
        i += 1
        if i <= nbr_file:
            if dic['daemon'] and dic['push']: #daemon push
                tag,data = message.recoit_socket(gs_s)
            else : #local and daemon pull
                tag,data = message.recoit(gs_s)
            data = message.str_to_fic(data)

    if dic['-v'] :
        print('done', end='\n' if dic['-v'] < 2 else ' sending files\n')


def send_local(dir,dic,gs_s,sr_s): #s'occupe des checksum
    '''gere la partie sender du mode local

    utilisee dans mrsync.py

    input : dir = liste des noms de fichiers a traiter (liste de string)
            dic = dictionnaire des options (dictionnaire)
            gs_s = descripteur de fichier cote sender, pipe generateur vers sender (descripteur de fichiers, int)
            sr_s = descripteur de fichier cote sender, pipe sender vers receiver (descripteur de fichiers, int)
    output : rien
    '''
    envoit_list_sender(dir,dic,sr_s)
    envoit_fichier(gs_s,sr_s,dic)
    #terminaison
    sys.exit(0)


def sender_daemon(src,dic,gs_s,clisock):
    '''gere la partie sender en mode pull daemon

    utilisee dans server_daemon, dans server.py

    input : src = repertoires sources (liste de string)
            dic = dictionnaire des options (dictionnaire)
            gs_s = si pull descripteur de fichier cote sender, pipe generateur vers sender (descripteur de fichiers, int)
                   si push socket client (socket)
            clisock = socket client (socket)
    output : rien
    '''
    #envoit filelist
    if dic['push']:
        filelistSender = filelist.filelist(src,dic,'sender')
        nbrFile=len(filelistSender)
        if nbrFile == 0:
            tag=['','l',(0,0)]
            message.envoit_socket(clisock,tag)
            sys.exit(0)
        for i in range(nbrFile):
                tag = [filelistSender[i]['name_loc'],'l',(i+1,nbrFile)]
                message.envoit_socket(clisock,tag,v=filelistSender[i])
    #reception delete liste
    if dic['push']: #cote client
        tag,data = message.recoit_socket(gs_s)
    elif dic['pull']: #cote server
        tag,data = message.recoit(gs_s)
    nbrFile = tag[2][1]
    message.envoit_socket(clisock,tag,data)
    for i in range(1,nbrFile):
        if dic['push']: #cote client
           tag,data = message.recoit_socket(gs_s)
        elif dic['pull']: #cote server
            tag,data = message.recoit(gs_s)
        message.envoit_socket(clisock,tag,data)
    #reception de la liste des fichiers et envoit des fichiers
    envoit_fichier(gs_s,clisock,dic)
    if dic['pull']:
        os.kill(os.getppid(),signal.SIGCHLD)
    sys.exit(0)

#autres types de fichiers ???
        
#a faire : checksum

#ouvre le fichier, le lit et l'envoie au receveur en plusieurs messages(+ gros que 16 Mo)
#tag = quel fichier il s'agit+tag data pour les messages contennant des bytearray+tagfin d'envoie
