import os, receiver, sys, socket, signal, sender, generator, filelist, message

def handler_SIGCHLD(sig,frame):
    try:
        (pid,statut)=os.waitpid(-1,0)
    except ChildProcessError:
        pass
    return

def handler_SIGTERM(sig,frame):
    #os.kill(-1,signal.SIGINT)
    sys.exit()
    return

def server_local(dirr,dic,gs_g,sr_r):
    receiver.receive_local(dirr,dic,gs_g,sr_r)

def reception_filelist(soc):
    file_lists=[]
    tag = ['','l',(0,1)]
    while tag[2][0]<tag[2][1]:  #file_lists ne peut pas etre vide
        tag,data = message.recoit_socket(soc)
        file_lists.append(message.str_to_fic(data))
    return file_lists

def envoit_filelist(file_list,soc):
    nbr_file = len(file_list)
    for i in range(nbr_file):
        tag = [file_list[i]['name_loc'],'l',(i+1,nbr_file)]
        message.envoit_socket(soc,tag,v=file_list[i])

def server_daemon(dic):
    signal.signal(signal.SIGCHLD,handler_SIGCHLD)
    signal.signal(signal.SIGTERM,handler_SIGTERM)
    port = 10873
    addr = '127.0.0.1' #addresse par defaut ?
    if dic['--port'] != '':
        port = int(dic['--port'])
    if dic['--address'] != '':
        addr = dic['--address']
    servsock = socket.socket(socket.AF_INET,socket.SOCK_STREAM,0)
    servsock.bind((addr, port)) 
    servsock.listen(10) #maxqueuesize ?
    while True:
        clisock,(fromaddr,fromport) = servsock.accept()
        pid = os.fork()
        if pid == 0: #fils, gère la requète
            #reception du dictionnaire client, repertoire destination, repertoire source
            tag,data  = message.recoit_socket(clisock)
            data = data.split(";")#changer la methode 3 envoit
            dic = message.str_to_dic(data[0])
            dic['--daemon'] = True #pour tester si c'est le cote server dans les fonctions suivantes
            dst = data[1]
            src = message.str_to_list(data[2]) #a mettre sous forme de liste
            if dic['pull']:
                if dic['--list-only']:
                    filelistSender = filelist.filelist(src,dic,'list-only')
                    envoit_filelist(filelistSender,clisock)
                    sys.exit(0)
                filelistSender = filelist.filelist(src,dic,'sender')
                filelistReceiver = reception_filelist(clisock)
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
            elif dic['push']:
                #reception de filelist sender
                filelistSender = reception_filelist(clisock)
                if dst[-1] != '/':
                    dst = dst + '/'
                filelistReceiver = filelist.filelist([dst],dic,'receiver')
                pid1 = os.fork()
                if pid1 == 0: #role receiver
                    receiver.receive_daemon(dst,dic,clisock)
                else : #role generateur
                    generator.generator_daemon(filelistSender,filelistReceiver,dic,clisock)
                #on enregistre dans dst ce qu'on 
                    clisock.close()
                    os.kill(os.getppid(),signal.SIGCHLD)
                    sys.exit(0)

        else : #pere, retourne en attente
            clisock.close()
