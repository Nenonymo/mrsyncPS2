import os, receiver, sys, socket, signal, sender, generator, filelist, message

def handler_SIGCHLD(sig,frame):
    '''handler pour SIGCHLD

    utilisée dans server_daemon
    '''
    try:
        (pid,statut)=os.waitpid(-1,0)
    except ChildProcessError:
        pass
    return

def handler_SIGTERM(sig,frame):
    '''hanlder pour SIGTERM
    
    utilisée dans server_daemon
    '''
    try:
        (pid,statut)=os.waitpid(-1,0)
    except ChildProcessError:
        pass
    sys.exit()
    return

def server_local(dirr,dic,gs_g,sr_r):
    '''fonction principale du server en mode local
    
    input = dirr = repertoire du receveur (string)
            dic = dictionnaire des options (dictionnaire)
            gs_g = pipe genereateur vers sender coté generateur (descripteur de fichier, int)
            sr_r = pipe sender vers receiver cote receiver (descripteur de fichier, int)
    output : rien
    '''
    receiver.receive_local(dirr,dic,gs_g,sr_r)

def reception_filelist(soc):
    '''receptionne la liste de fichier du client
    fichiers source si mode push
    fichiers dans la destination si mode pull
    un fichier est représenté par un dictionnaire contenant des informations sur celui-ci
            {'name_loc':nom local,'name':nom absolu,'user':propriètaire,'groupe':groupe propriètaire,'mode':permissions,'size':taille,'modtime':date de derniere modification}

    utilisee dans server_daemon

    input : soc = socket du client (socket)
    output : file_list = la liste de fichier recu (liste de fichier) 
    '''
    file_list=[]
    tag = ['','l',(0,1)]
    while tag[2][0]<tag[2][1]:
        tag,data = message.recoit_socket(soc)
        if tag[2][1]!=0:
            file_list.append(message.str_to_fic(data))
    return file_list

def envoit_filelist(file_list,soc):
    '''envoit la liste de fichier du client, seulement si --list-only
    fichiers sources

    utilisee dans server_daemon

    input : soc = socket du client (socket)
            file_list = la liste de fichier recu (liste de fichier) 
    output : rien
    '''
    nbr_file = len(file_list)
    for i in range(nbr_file):
        tag = [file_list[i]['name_loc'],'l',(i+1,nbr_file)]
        message.envoit_socket(soc,tag,v=file_list[i])

def server_daemon(dic):
    '''fonction principale du daemon (server)

    se met en attente de requete, et cree un fils quand il en recoit une, puis se remet en attente
    le fils traite la requete

    termine avec ses fils lorsqu'il recoit un signal SIGTERM
    '''
    signal.signal(signal.SIGCHLD,handler_SIGCHLD)
    signal.signal(signal.SIGTERM,handler_SIGTERM)
    port = 10873
    addr = '127.0.0.1'
    if dic['--port'] != '':
        port = int(dic['--port'])
    if dic['--address'] != '':
        addr = dic['--address']
    servsock = socket.socket(socket.AF_INET,socket.SOCK_STREAM,0)
    servsock.bind((addr, port)) 
    servsock.listen(10)
    while True:
        clisock,(fromaddr,fromport) = servsock.accept()
        pid = os.fork()
        if pid == 0: #fils, gère la requète
            #reception du dictionnaire client, repertoire destination, repertoire source
            tag,data  = message.recoit_socket(clisock)
            data = data.split(";")
            dic = message.str_to_dic(data[0]) #on prend le dictionnaire du client
            dic['--daemon'] = True #on le rajoute pour tester si c'est le cote server dans les fonctions suivantes
            dst = data[1] #liste du repertoire destination
            src = message.str_to_list(data[2]) #liste des repertoires source
            if dic['pull']: #le sender et generateur sont cote server
                if dic['--list-only']: #mode list only, on envoit la liste de fichiers sources et on termine
                    filelistSender = filelist.filelist(src,dic,'list-only')
                    envoit_filelist(filelistSender,clisock)
                    sys.exit(0)
                filelistSender = filelist.filelist(src,dic,'sender')
                filelistReceiver = reception_filelist(clisock)
                if len(filelistSender) == 0: #si la liste de fichiers sources est vide
                    tag = ['','l',(0,0)]
                    message.envoit_socket(clisock,tag) #delete liste vide
                    message.envoit_socket(clisock,tag) #liste de fichiers vide
                    clisock.close()
                    os.kill(os.getppid(),signal.SIGCHLD) #on previent le pere qu'on va se terminer
                    sys.exit(0) #terminaison
                r,w = os.pipe()
                pid1 = os.fork()
                if pid1 == 0 :
                    sender.sender_daemon(src,dic,r,clisock)
                else :
                    #reception file_list_sender 
                    generator.generator_daemon(filelistSender,filelistReceiver,dic,w)
                #utilisation de receiver local, generator et sender local (aproximatif, refaire un truc)
                #liste des fichiers a creer envoyés au client
                    clisock.close()
                    os.kill(os.getppid(),signal.SIGCHLD)
                    sys.exit()
            elif dic['push']: #le generateur et le receveur sont cote server 
                #reception de filelist sender
                filelistSender = reception_filelist(clisock)
                if len(filelistSender) == 0: #si liste de fichier recu vide on termine
                    clisock.close()
                    os.kill(os.getppid(),signal.SIGCHLD)
                    sys.exit(0)
                if dst[-1] != '/':
                    dst = dst + '/'
                filelistReceiver = filelist.filelist([dst],dic,'receiver') #creation de la liste des fichiers dans la destination
                pid1 = os.fork()
                if pid1 == 0: #role receiver
                    receiver.receive_daemon(dst,dic,clisock)
                else : #role generateur
                    generator.generator_daemon(filelistSender,filelistReceiver,dic,clisock)
                    clisock.close()
                    os.kill(os.getppid(),signal.SIGCHLD)
                    sys.exit(0)

        else : #pere, retourne en attente
            clisock.close()