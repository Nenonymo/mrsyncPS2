import os, sys, filelist, time, stat, message

def send_listonly(lis_dir,dic):
    #On cherche le dossier le plus englobant pour pouvoir faire le chemin relatif en partant de là
    cwd = os.getcwd()
    for elt in lis_dir:
        while cwd != os.path.abspath(elt)[:len(cwd)]:
            cwd = os.path.split(cwd)[0]

    #On récupère la liste de fichier et tout ses éléments descripteurs
    file_list=[]
    for dir in lis_dir:
        file_list = file_list + filelist.parcours(dir,dic)
    
    #L'affichage
    for elt in file_list:
        print('{} {:>14} {} {}'.format(stat.filemode(elt['mode']), elt['size'], time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(elt['modtime'])), elt['name'][len(cwd) + 1:]))

def send_local(dir,dic,gs_s,sr_s): #s'occupe des checksum
    file_list = filelist.parcours(norm_liste_dir(dir),dic)
    message.envoit(sr_s,tag,file_list) #envoit la liste de fichier au receveur
    tag,data = message.recoit(gs_s) #recoit la liste de fichier a envoyer
