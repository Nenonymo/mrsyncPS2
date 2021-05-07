import os, receiver, socket, signal, sender, generator, filelist


def server_local(dirs,dirr,dic,gs_g,sr_r):
    receiver.receive_local(dirs,dirr,dic,gs_g,sr_r)

def reception_filelist(soc):
    file_lists=[]
    tag = ['','l',(0,1)]
    while tag[2][0]<tag[2][1]:  #file_lists ne peut pas etre vide
        tag,data = message.recoit_socket(soc)
        file_lists.append(message.str_to_dic(data))
    return file_lists

def envoit_filelist(soc,file_list):
    nbr_file = len(file_list)
    for i in range(nbr_file):
        tag = [file_list[i]['name_loc'],'l',(i+1,nbr_file)]
        message.envoit_socket(soc,tag,v=file_list[i])

def server_daemon(dic):
    port = 10873
    if dic['--port'] != '':
        port = int(dic['--port'])
    servsock = socket.socket(socket.AF_INET,socket.SOCK_STREAM,0)
    servsock.bind((localhost, port)) #localhost??
    servsock.listen(maxqueuesize) #maxqueuesize ?
    while True: #condition?-> reception SIGTERM
        clisock = sock.accept()
        pid = os.fork()
        if pid == 0: #fils
            #gestion socket
            #reception des répertoires du client a stocker dans une liste
            tag,data  = message.recoit_socket(clisock)
            data = data.split(":")
            dic = message.str_to_dic(data[1])
            dic['--daemon'] = True #pour tester si c'est le cote server dans les fonctions suivantes
            dst = data[2]
            src = data[3] #a mettre sous forme de liste
            if data[0] == 'pull':
                dic['pull'] = True
                dic['push'] = False
                if dic['--list-only']:
                    filelistSender = filelist.filelist(src,dic,'list-only')
                    envoit_filelist(clisock,filelistSender)
                    sys.exit(0)
                    #et imprimmer chez le client
                filelistSender = filelist.filelist(src,dic,'sender')
                filelistReceiver = reception_filelist(soc)
                r,w = os.pipe()
                pid1 = os.fork()
                if pid1 == 0 :
                    sender.send_daemon(dic,r,clisock,servsock)
                else :
                    #reception file_list_sender 
                    generator.generator_daemon(filelistSender,filelistReceiver,dic,w)
                    os.wait()
                #utilisation de receiver local, generator et sender local (aproximatif, refaire un truc)
                #liste des fichiers a creer envoyés au client
                clisock.close()
                sys.exit()
            elif data[0] == 'push':
                dic['pull'] = False
                dic['push'] = True
                #reception de filelist sender
                filelistSender = reception_filelist(soc)
                if dst[-1] != '/':
                    dst = dst + '/'
                filelistReceiver = filelist.filelist([dst],dic,'receiver')
                pid1 = os.fork()
                if pid1 == 0: #role receiver
                else : #role generateur
                    generator.generator_daemon(filelistSender,filelistReceiver,dic,clisock)
                #on enregistre dans dst ce qu'on recoit
            
        else : #pere
            clisock.close()
