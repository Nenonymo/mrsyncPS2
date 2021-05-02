import os,filelist,message,generator,sys

#brouillon

def receive_local(dirs,dirr,dic,gs_g,sr_r):
    #creation de la liste de fichier du repertoire de destination
    print(dirr)
    if dirr[-1] != '/':
        dirr = dirr + '/'
    file_listr = filelist.filelist([dirr],dic) #pourquoi j'obtient la mauvaise liste de fichier ?
    print(file_listr)

    #reception de la liste de fichier du repertoire source
    file_lists=[]
    tag = ['','l',(0,1)]
    while tag[2][0]<tag[2][1]:  #file_lists ne peut pas etre vide
        tag,data = message.recoit(sr_r,lineFile='comSize2')
        file_lists.append(message.str_to_dic(data))

    #creation du generateur
    pid=os.fork()
    if pid != 0: #père, générateur
        generator.generator_local(dirs,dirr,file_lists,file_listr,dic,gs_g)

    else: #fils, receiver, reception des fichiers
        tag,data = message.recoit(sr_r,lineFile='comSize2')
        nbr_file = tag[2][1]

        i = 1
        while i <= nbr_file:
            tag,data = message.recoit(sr_r,lineFile='comSize2')
            data = message.str_to_dic(data)
            #repertoire
            if tag[1]=='r':
                chemin = os.path.join(dirr,tag[0])
                os.mkdir(chemin,data['mode'])
            #lien symbolique
            elif tag[1]=='s':
                chemin=os.path.join(dirr,tag[0])
                os.symlink(data['name'],chemin)
            #fichier
            elif tag[1]=='f':
                chemin = os.path.join(dirr,tag[0])
                nbr_transmission = tag[2][1]
                fd = os.open(chemin,os.O_CREAT|os.O_WRONLY)
                tag,data = message.recoit(sr_r,lineFile='comSize2')
                os.write(fd,data)
                fd.close()
                fd = os.open(chemin,os.O_WRONLY|os.O_APPEND)
                j = tag[2][0]
                while j <= nbr_transmission:
                    tag,data = message.recoit(sr_r,lineFile='comSize2')
                    j = tag[2][0]
                    os.write(fd,data)
                fd.close()

            i+=1
        
        #terminaison
        sys.exit(0)