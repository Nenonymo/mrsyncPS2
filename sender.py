import os, sys, filelist, time, stat, message, time

def send_listonly(lis_dir,dic):
    #On récupère la liste de fichier et tout ses éléments descripteurs
    file_list = filelist.filelist(lis_dir,dic)
    #L'affichage
    if not dic['-q'] :
        for elt in file_list:
            print('{} {:>14} {} {}'.format(stat.filemode(elt['mode']), elt['size'], time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(elt['modtime'])), elt['name_loc']))
    if dic['-v'] > 0 :
        print('\nsent {} bytes received {} bytes {} bytes/sec\ntotal size is {} speedup is {}'.format(572, 1533, 4210.00, 69201, 32.87)) #nombres à changer, je ne sais pas ce à quoi ça correspond

def send_local(dir,dic,gs_s,sr_s): #s'occupe des checksum
    #creation de la liste des fichiers sources + envoit au receiver
    file_list = filelist.filelist(dir,dic)
    nbr_file = len(file_list)

    for i in range(nbr_file):
        tag = [file_list[i]['name_loc'],'l',(i+1,nbr_file)]
        print(i,nbr_file)
        message.envoit(sr_s,tag,v=file_list[i])

    #reception de la liste de fichier du generateur + envoit des fichiers au receiver
    tag,data = message.recoit(gs_s)
    nbr_file=tag[2][1]
    tag_e = ['c','l',(0,nbr_file)]
    message.envoit(sr_s,tag_e)   #on envoit le nbr de fichiers a traiter
    i=1

    while i <= nbr_file : #si send_list est vide, on rentre pas dans la boucle
        if os.path.isdir(data['name']):  #repertoire
            tag_e = [tag[0],'r',(1,1)]
            message.envoit(sr_s,tag_e,data)
        elif os.path.islink(data['name']): #lien symbolique
            tag_e = [tag[0],'s',(1,1)]
            message.envoit(sr_s,tag_e,data)
        elif os.path.isfile(data['name']): #fichier
            fd = os.open(data['name'],os.O_RDONLY)
            size_file = data['size']
            taille_msg = 5000
            nbr_transmission = size_file//taille_msg +1
            if size_file%taille_msg != 0:
                nbr_transmission += 1
            tag_e = [tag[0],'f',(1,nbr_transmission)]
            message.envoit(sr_s,tag_e,data)
            j = 2
            while j <= nbr_transmission :
                msg = os.read(fd,taille_msg)
                tag_e = [tag[0],'f',(j,nbr_transmission)]
                message.envoit(sr_s,tag_e,msg)
            #envoyer le contenu du fichier
            os.close(fd)

        i += 1
        if i <= nbr_file:
            tag,data = message.recoit(gs_s) #prochain fichier a traiter
    
    #terminaison
    sys.exit(0)


#autres types de fichiers ???
        
#a faire : checksum

#ouvre le fichier, le lit et l'envoie au receveur en plusieurs messages(+ gros que 16 Mo)
#tag = quel fichier il s'agit+tag data pour les messages contennant des bytearray+tagfin d'envoie
