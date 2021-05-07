import os,filelist,message,generator,sys

'''creation de la liste de fichier destination

utilisee dans la fonction principale receiver

input : dirr = repertoire destination, chemin absolu (string)
        dic = dictionnaire des options (dictionnaire)
output : file_listr = liste de fichier destination (liste de fichier)
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
            ou socket server si mode daemon pull (socket)
        dic = dictionnaire d'options
output : rien
'''
def reception_fichiers(dirr,d,dic):
    if dic['-v'] > 0 :
        print('receiving files ...', end=' ' if dic['-v'] < 2 else '\n')
    if dic['daemon'] and dic['pull']:
        tag,data = message.recoit_socket(d)
    else :
        tag,data = message.recoit(d)
    nbr_file = tag[2][1]
    i = 1
    while i <= nbr_file:
        if dic['daemon'] and dic['pull']:
            tag,data = message.recoit_socket(d)
        else :
            tag,data = message.recoit(d)
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
                if dic['daemon'] and dic['pull']:
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
    file_lists=reception_filelist_sender(sr_r)
    #creation du generateur
    pid=os.fork()
    if pid != 0: #père, générateur
        generator.generator_local(file_lists,file_listr,dic,gs_g)
    else: #fils, receiver, reception des fichiers
        reception_fichiers(dirr,sr_r,dic)
        #terminaison
        sys.exit(0)


def receive_daemon(dst,dic,soc):
    if dic['pull']: #cote client
        if dic['--list-only']:
            #On récupère la liste de fichier et tout ses éléments descripteurs
            taille_tot = 0
            tag,data = message.recoit(d)
            nbr_file = tag[2][1]
            i = 1
            while i <= nbr_file:
                tag,data = message.recoit_socket(soc)
                data = message.str_to_dic(data)
                taille_tot += data['size']
                if not dic['-q'] :
                    print('{} {:>14} {} {}'.format(stat.filemode(elt['mode']), elt['size'], time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(elt['modtime'])), elt['name_loc']))
                i+=1
            if dic['-v']>0 and not dic['-q'] ::
                print('\ntaille totale : {}'.format(taille_tot)) #nombres à changer, je ne sais pas ce à quoi ça correspond
        else :
            #calcul et envoit de filelistReceiver au demon
            filelistReceiver = creation_filelist_receiver(dst,dic)
            nbrFile = len(filelistReceiver)
            for i in range(nbrFile):
                tag = [filelistReceiver[i]['name_loc'],'l',(i+1,nbrFile)]
                message.envoit_socket(soc,tag,v=filelistReceiver[i])

            reception_fichiers(dst,soc,dic)
        sys.exit(0)
        
    elif dic['push']:#cote server