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
    file_list = filelist.filelist(dir,dic)
    sr = os.open(sr_s,os.O_WRONLY)
    gs = os.open(gs_s,os.O_RDONLY)
    nbr_file = len(file_list)
    for i in range(nbr_file):
        tag = [file_list[i]['name_loc'],'l',(i,nbr_file)]
        message.envoit(sr,tag,file_list[i]) #envoit la liste de fichier au receveur
    tag,data = message.recoit(gs)
    nbr_file=tag[2][1]
    tag_e = ['','l',(0,nbr_file)]
    message.envoit(sr,tag_e)   #on envoit le nbr de fichiers a traiter
    while tag[2][0] <= nbr_file : #si send_list est vide, on rentre pas dans la boucle
        #traitement du premier message ici
        tag,data = message.recoit(gs)
        tag_e = [tag[0]]
        filename = os.path.abspath(tag2)
        tag2 += "d"
        #tester si un seul envoit necessaire mettre df
        while tag2 != "" :
            #data2 = os.read(filename,n)
            message.envoit(sr_s,tag2,data2)
            if tag2 == data+"d":
                tag2 = data
            '''if #dernier :
                tag2 += "f"
            elif tag2 == data+"f" or tag2 == data+"df":
                tag2 = ""'''


        #envoit les fichiers correspondant a receiver
        #ouvre le fichier, le lit et l'envoie au receveur en plusieurs messages(+ gros que 16 Mo)
        #tag = quel fichier il s'agit+tag data pour les messages contennant des bytearray+tagfin d'envoie
