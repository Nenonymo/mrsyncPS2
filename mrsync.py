import os, sys, socket, options, sender, server, receiver, message

if __name__ == '__main__' :
    dic, src, dest = options.parser(sys.argv)

    if os.path.exists("pid"): #a placer à la fin de l'éxécution du programme, quand tout est fini
        os.remove("pid")
    
    if dic['--list-only'] and not dic['daemon'] and not dic['ssh']:    #gerer le liste only avec le ssh dans list only ou ssh ?
        if dic['-v'] > 1 :
            print('mode list-only')
        sender.send_listonly(src, dic)

    elif dic['--server']:
        if dic['-v'] > 1: print("mode serveur ssh")

        server.server_ssh(dic)

    elif dic['ssh']:
        if dic['-v'] > 1 :
            print('mode ssh')
        
        pid = os.fork()

        if pid > 0: #père
            sys.exit(0) #je sais pas quoi mettre pour le moment

        else:
            #trucs surement importants
            sshcom = "ssh -e none -l {} {}".format("distant", "localhost") #a remplacer avec le bon utilisateur et la bonne machine
            os.execvp("{} ./mrsync.py --server {}".format(sshcom, dic['brut'])) #remplacement du processus par le processus server, n'executeras plus aucun code suivant cette ligne !

    elif dic['--daemon']:

        #séparation CMD
        #Démarrage en mode démon
        
        #gestion détacher du file puis appel dans les deux cas du elif en dessous
        if dic['--no-detach']:
            if dic['-v'] >= 1: print("Lancement du daemon en mode non detache")
            server.server_daemon(dic)
        else:
            if dic['-v'] >= 1: print("Lancement du daemon en mode detache")
            #Deamonizing the process
            log_file = '/tmp/mrsync.log'
            #Vérification pas de démon en cours
            if dic['-v'] >= 2: print("Verification qu'un autre daemon n'es pas en cours")
            os.system('ps -ef | grep -v grep | grep "mrsync.py" | wc -l > tmp')
            a = open('tmp', 'r').read()
            os.remove('tmp')
            if int(a) > 1:
                #code erreur démon déjà en cours
                print("erreur : mrsync est déjà en cours sur cette machine")
                sys.exit(0)

            if dic['-v'] >= 2: print("Séparation des processus et meurtre du pere")
            pid = os.fork() #Séparation en deux processus
            if pid > 0:
                #terminaison du père, fils devient zombie
                sys.exit(0)
            if dic['-v'] >= 2: print("Changement du repertoire de travail\nDetachement du groupe de processus\nChangement du masque de permissions")
            os.chdir('/') #changement du répertoire actuel
            os.setsid() #detachement du processus du groupe de processus
            os.umask(0) #changement du masque de permissions

            #Deuxième fois séparation puis meurtre du parent
            if dic['-v'] >= 2: print("Deuxieme separation des processus puis meurtre du parent")
            pid = os.fork()
            if pid > 0: sys.exit(0)
            
            #Redirection des descripteurs standards
            if dic['-v'] == 1: print("Redirection des entrees/sorties, log du daemon dans {}".format(log_file))
            if dic['-v'] > 1: print("Redirection des entrees/sorties :\n\tLog -> {}\n\n\tStdin <- devnull\n\tStdout <- Log\n\tStderr <- Log".format(log_file))
            sys.stdout.flush()
            sys.stderr.flush()
            i = open(os.devnull, 'r')
            os.dup2(i.fileno(), sys.stdin.fileno())
            if log_file != '': o = open(log_file, 'w')
            else: o = open(os.devnull, 'w')
            os.dup2(o.fileno(), sys.stdout.fileno())
            #e = open(os.devnull, 'w')
            #os.dup2(e.fileno(), sys.stderr.fileno())
            os.dup2(o.fileno(), sys.stderr.fileno())
            if dic['-v'] >= 1: print("Lancement du serveur sur le daemon")
            server.server_daemon(dic)

    elif dic['daemon']:
        if dic['-v'] > 1 :
            print('mode daemon')
        if '::' in dest :
            dest = dest.split('::')
            host = dest[0]  #a quoi sert host ??? addr ?
            dest = dest[1]
            dest = os.path.abspath(dest)
            dic['push'] = True
            dic['pull'] = False
        elif '::' in src[0]:
            src[0]= src[0].split('::')
            host = src[0][0]
            src[0] = src[0][1]
            for i in range(len(src)):
                a=''
                if src[i][-1]=='/': a = '/'
                src[i] = os.path.abspath(src[i]) + a
            dic['push'] = False
            dic['pull'] = True
        #se connecter au serveur + envoyer premieres infos
        port = 10873
        addr = '127.0.0.1' #addresse par defaut ?
        if dic['--port'] != '':
            port = int(dic['--port'])
        if dic['--address'] != '':
            addr = dic['--address']
        clisock = socket.socket(socket.AF_INET,socket.SOCK_STREAM,0)
        clisock.connect((addr,port))
        tag =['','l',(1,1)]
        data=str(dic)+';'+ dest +';'+ str(src) #changer la methode, 3 envois
        message.envoit_socket(clisock,tag,v=data)
        if dic['pull']:
            receiver.receive_daemon(dest,dic,clisock)
        elif dic['push']:
            sender.sender_daemon(src,dic,clisock,clisock)

    else : #si local
        if dic['-v'] > 1 :
            print('mode local')
        sr_r,sr_s = os.pipe()
        gs_s,gs_g = os.pipe()
        pid=os.fork()
        if pid != 0 : #pere, server
            server.server_local(dest,dic,gs_g,sr_r)
        else : #fils, sender
            sender.send_local(src,dic,gs_s,sr_s)
#love you
