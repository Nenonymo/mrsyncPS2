import filelist, time

#brouillon

def send_listonly(lis_dir,dic): #améliorer l'affichage
    file_list=[]
    for dir in lis_dir:
        file_list = file_list + filelist.parcours(dir,dic)
    for elt in file_list:
        print('{}{}{}{} {:>14} {} {}'.format('d' if elt['isDirectory'] else '-', 'r' if elt['perm'][0] else '-', 'w' if elt['perm'][1] else '-', 'x' if elt['perm'][2] else '-', elt['size'], time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(elt['modtime'])), elt['name']))

def send_local(dir,dic):
    file_lists = filelist.parcours(dir,dic)
    return file_lists
    #envoit la liste de fichier au receveur qui crée le generateur
