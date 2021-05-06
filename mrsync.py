import os, sys, options, sender, server

if __name__ == '__main__' :
    dic, src, dest = options.parser(sys.argv)

    if os.path.exists("pid"): #a placer à la fin de l'éxécution du programme, quand tout est fini
        os.remove("pid")
    
    if dic['--list-only'] :    #gerer le liste only avec le ssh dans list only ou ssh ?
        if dic['-v'] > 1 :
            print('mode list-only')
        sender.send_listonly(src, dic)

    elif dic['ssh']:
        if dic['-v'] > 1 :
            print('mode ssh')
        print('ssh')

    elif dic['--daemon']:

        #séparation CMD
        #Démarrage en mode démon
        
        #gestion détacher du file puis appel dans les deux cas du elif en dessous
        server.server_daemon(dic)

    elif dic['daemon']:
        if dic['-v'] > 1 :
            print('mode daemon')

    else : #si local
        if dic['-v'] > 1 :
            print('mode local')
        sr_r,sr_s = os.pipe()
        gs_s,gs_g = os.pipe()
        pid=os.fork()
        if pid != 0 : #pere, server
            server.server_local(src,dest,dic,gs_g,sr_r)
        else : #fils, sender
            sender.send_local(src,dic,gs_s,sr_s)
