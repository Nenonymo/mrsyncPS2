import os,filelist,message,generator,sys

'''creation de la liste de fichier destination

utilisee dans la fonction principale receiver

input : dirr = repertoire destination, chemin absolu (string)
        dic = dictionnaire des options (dictionnaire)
ouput : file_listr = liste de fichier destination (liste de fichier)
        un fichier est représenté par un dictionnaire contenant des informations sur celui-ci
        {'name_loc':nom local,'name':nom absolu,'user':propriètaire,'groupe':groupe propriètaire,'mode':permissions,'size':taille,'modtime':date de derniere modification}
'''
def creation_filelist_receiver(dirr,dic):
    if dirr[-1] != '/':
        dirr = dirr + '/'
    file_listr = filelist.filelist([dirr],dic,'receiver')
    return file_listr

'''receptionne la liste des fichiers source

utilisee dans la fonction principale receiver

input : fd = descripteur de fichier de l'endroit ou on receptionne les fichiers (descripteur de fichier, int)
output : file_lists = liste des fichiers source (liste de fichiers)
'''
def reception_filelist_sender(fd):
    file_lists=[]
    tag = ['','l',(0,1)]
    while tag[2][0]<tag[2][1]:  #file_lists ne peut pas etre vide
        tag,data = message.recoit(fd,lineFile='comSize2')
        file_lists.append(message.str_to_dic(data))
    return file_lists

'''receptionne les fichiers envoyés par sender et les crée dans le repertoire de destination

utilisee dans la fonction principale receiver

input : dirr = repertoire de destination, chemin absolu (string)
        d = descripteur de fichier de l'endroit ou on recoit les fichiers (descripteur de fichier, int)
ouput : rien
'''
def reception_fichiers(dirr,d):
    tag,data = message.recoit(d,lineFile='comSize2')
        nbr_file = tag[2][1]
        i = 1
        while i <= nbr_file:
            tag,data = message.recoit(d,lineFile='comSize2')
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
                try:
                    os.unlink(chemin)
                except:
                    pass
                fd = os.open(chemin,os.O_CREAT|os.O_WRONLY|os.O_APPEND)
                j = tag[2][0]+1
                while j <= nbr_transmission:
                    tag,data = message.recoit(d,lineFile='comSize2')
                    j +=1
                    data = data.encode('utf-8')
                    os.write(fd,data)
                os.close(fd)
            i+=1

'''fonction principale du receiver en mode local

utilisee par server.server_local, dans server.py

input : dirs = repertoires sources, chemins absolus (liste de string)
        dirr = repertoire destination, chemin absolu (string)
        dic = dictionnaire des options (dictionnaire)
        gs_g = descripteur de fichier du generateur, pipe generateur vers sender (descripteur de fichier, int)
        sr_r = descripteur de fichier du receiver, pipe sender vers receiver (descripteur de fichier, int)
'''
def receive_local(dirs,dirr,dic,gs_g,sr_r):
    #creation de la liste de fichier du repertoire de destination
    file_listr = creation_filelist_receiver(dirr,dic)
    #reception de la liste de fichier du repertoire source
    file_lists=reception_filelist_sender(sr_r)
    if dic['daemonserveur']:
        generator.generator_local(dirs,dirr,file_lists,file_listr,gs_g)
        sys.exit()
    #creation du generateur
    pid=os.fork()
    if pid != 0: #père, générateur
        generator.generator_local(dirs,dirr,file_lists,file_listr,dic,gs_g)
    else: #fils, receiver, reception des fichiers
        reception_fichiers(dirr,sr_r)
        #terminaison
        sys.exit(0)