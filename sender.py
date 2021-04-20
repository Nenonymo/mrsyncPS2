import os, sys, filelist, time, stat

def send_listonly(lis_dir,dic):
    #On exclu les fichiers traités plusieurs fois (peut-on faire plus simple ?)
    if dic['-r'] :
        for i in range(len(lis_dir)) :
            for j in range(i + 1, len(lis_dir)) :
                if lis_dir[i] == lis_dir[j][:len(lis_dir[i])] + '/' :
                    del lis_dir[j]
                elif lis_dir[i][:len(lis_dir[j])] + '/' == lis_dir[j] :
                    del lis_dir[i]
    else :
        for i in range(len(lis_dir)) :
            for j in range(i + 1, len(lis_dir)) :
                if lis_dir[i] == os.path.split(lis_dir[j])[0] + '/' :
                    del lis_dir[j]
                if os.path.split(lis_dir[i])[0] + '/' == lis_dir[j] :
                    del lis_dir[i]
    
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
    file_list = filelist.parcours(dir,dic)
    envoit(sr_s,tag,file_list) #envoit la liste de fichier au receveur
    tag,data = recoit(gs_s) #recoit la liste de fichier a envoyer
