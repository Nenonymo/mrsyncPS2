import os, receiver, socket, signal, sender, generator


def server_local(dirs,dirr,dic,gs_g,sr_r):
    receiver.receive_local(dirs,dirr,dic,gs_g,sr_r)

def server_daemon(dic): #comment faire pour qu'un seul demon soit demarrer ?
    port = 10873
    if dic['--port'] != '':
        port = int(dic['--port'])
    servsoc = socket.socket(socket.AF_INET,socket.SOCK_STREAM,0) #???
    serv.bind((localhost, port)) #localhost??
    serv.listen(maxqueuesize) #maxqueuesize ?
    pid = os.fork()
    while True: #condition?-> reception SIGTERM
        clisock = sock.accept()
        if pid == 0: #fils
            #gestion socket
            #reception des répertoires du client a stocker dans une liste
            gs_s,gs_g = os.pipe()
            sr_r,sr_s = os.pipe()
            pid1 = os.fork()
            if pid1 == 0 :
                sender.send_local(dirs,dic,gs_s,sr_s)
            else : 
                generator.generator_daemon(dirs,dirr,file_list_sender,file_list_receiver,dic,gs_g)
            #utilisation de receiver local, generator et sender local (aproximatif, refaire un truc)
            #liste des fichiers a creer envoyés au client
            clisock.close()
            sys.exit()
        else : #pere
            clisock.close()
