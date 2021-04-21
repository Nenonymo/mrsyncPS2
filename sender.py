import os, sys, filelist, time, stat, message

def send_listonly(lis_dir,dic):
    #On créé la liste complète (sans -r) de fichiers à traiter en faisant gaffe aux doublons
    if dic['-r'] :
        i = 0
        while i < len(lis_dir) :
            j = i + 1
            while j < len(lis_dir) :
                if lis_dir[i] == lis_dir[j][:len(lis_dir[i])] + '/' :
                    del lis_dir[j]
                elif lis_dir[i][:len(lis_dir[j])] + '/' == lis_dir[j] :
                    del lis_dir[i]
                j += 1
            i += 1
    else :
        i = 0
        while i < len(lis_dir) :
            if lis_dir[i] == '.' or lis_dir[i] == './' :
                lis_dir = lis_dir[:i + 1] + [elt for elt in os.listdir(lis_dir[i])] + lis_dir[i + 1:]
            elif lis_dir[i][-1] == '/' :
                lis_dir = lis_dir[:i + 1] + [os.path.join(lis_dir[i], elt) for elt in os.listdir(lis_dir[i])] + lis_dir[i + 1:]
            elif lis_dir[i].startswith('./') :
                lis_dir[i] = lis_dir[i][2:]
            i += 1
        i = 0
        while i < len(lis_dir) :
            j = i+1
            while j < len(lis_dir) :
                if lis_dir[i] == lis_dir[j] :
                    del lis_dir[j]
                j += 1
            i += 1
    
    #On cherche le dossier le plus englobant pour pouvoir faire le chemin relatif en partant de là
    cwd = os.getcwd()
    for elt in lis_dir:
        while cwd != os.path.abspath(elt)[:len(cwd)]:
            print(os.path.abspath(elt)[:len(cwd)], cwd)
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
    message.envoit(sr_s,tag,file_list) #envoit la liste de fichier au receveur
    tag,data = message.recoit(gs_s) #recoit la liste de fichier a envoyer
