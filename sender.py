import os, sys, filelist, time, stat, message

def send_listonly(lis_dir,dic):
    #On récupère la liste de fichier et tout ses éléments descripteurs
    file_list = filelist.filelist(lis_dir,dic)
    
    #L'affichage
    for elt in file_list:
        print('{} {:>14} {} {}'.format(stat.filemode(elt['mode']), elt['size'], time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(elt['modtime'])), elt['name_loc']))

def send_local(dir,dic,gs_s,sr_s): #s'occupe des checksum
    file_list = filelist.filelist(dir,dic)
    message.envoit(sr_s,tag,file_list) #envoit la liste de fichier au receveur

    while tag == "liste" : #s'arrete quand on recoit listef
        tag,data = message.recoit(gs_s)
        tag2 = data
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
